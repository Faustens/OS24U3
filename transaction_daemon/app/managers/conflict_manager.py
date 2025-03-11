from . import filesystem_manager
import time
from ..utils import exceptions as ex
from ..utils import logging
import os

class _ConflictNode:
    def __init__(self,id,type,timestamp,snapshot,file):
        self.pred = None
        self.succ = None
        self.id = id
        self.timestamp = timestamp
        self.type = type
        self.snapshot = snapshot
        self.file = file

class ConflictManager:
    def __init__(self):
        self._headers = {}
        self._fs = filesystem_manager.FilesystemManager()
        self._start_nodes = {}
        self.logger = logging.Logger()
        self.logger.log(f"[CM][INFO] ConflictManager initialized.")
    # Method: initiate_start --------------------------------------------------
    # Inserts a node representing a transaction start into the conflict structure
    # Inserting a new transaction can not lead to any conflict
    def initiate_start(self,id,path):
        timestamp = time.time()
        dirname,_ = os.path.split(path)
        snapshot = self._fs.create_snapshot(dirname,id)
        node = _ConflictNode(
            id,
            "start",
            timestamp,
            snapshot,
            path
        )
        self.logger.log(f"[CM][INFO] ConflictNode '{id}', status 'start', timestamp:'{timestamp}' created")
        # Find list header id, create one if necessary
        header_id = self._fs.get_fs(path)
        print(f"header id: {header_id}")
        if header_id not in self._headers or self._headers[header_id] is None:
            self._headers[header_id] = node
        else:
        # insert node at the right place
            current = self._headers[header_id]
            while current.succ is not None and current.succ.timestamp <= node.timestamp: # O(n)
                current = current.succ
            node.succ = current.succ
            node.pred = current
            current.succ = node
            if not node.succ is None:
                node.succ.pred = node
        self._start_nodes[id] = node
        self.logger.log("[CM][INFO] Start node creation and insertion successful")
        return 0
    # Method: initiate_commit -------------------------------------------------
    # Adds a commit of a transaction to the conflict structure
    # Checks if insertion leads to a conflict
    # if yes, remove all nodes after the start node
    def initiate_commit(self,id):
        start_node = self.get_start_node(id)
        file = start_node.file
        timestamp = time.time()
        node = _ConflictNode(
            id,
            "commit",
            timestamp,
            None,
            file
        )
        self.logger.log(f"[CM][INFO] ConflictNode {id}, status: 'commit', timestamp: {timestamp} created")
        # Find node to insert the new node after
        current = start_node
        while current.succ is not None and current.succ.timestamp <= node.timestamp:
            current = current.succ
        node.succ = current.succ
        node.pred = current
        current.succ = node
        if not node.succ is None:
            node.succ.pred = node
        # Conflict checks -----------------------
        conflict = False
        conflict_potential = False
        current = start_node.succ
        while current != node:
            if current.file == file:
                if current.type == "start":
                    conflict_potential = True
                else: # current.type == "commit"
                    conflict = True
                    break
            current = current.succ
        print(f"conflict check finished with conflict:{conflict}, conflict_potential:{conflict_potential}")
        # Conflict handling
        if conflict:
            self._fs.restore_snapshot(start_node.snapshot)
            current = start_node
            while current is not None:
                if current.type == "start":
                    del self._start_nodes[current.id]
                current = current.succ
            left = start_node.pred
            start_node.pred = None
            if left is None:
                header_id = self._fs.get_fs(start_node.file)
                self._headers[header_id] = None
            else:
                left.succ = None
            raise ex.TransactionInvalidException
        else:
            self._remove_node(start_node)
            del self._start_nodes[id]
            if not conflict_potential:
                self._remove_node(node)
            self.logger.log("[CM][INFO] Commit successful")
            return 0
    # Method: cancel [TODO] Name ----------------------------------------------
    # Entfernt die betreffende start node aus der korrekten Knotenliste
    # und führt ein neues conflict assessment durch
    def cancel(self,id):
        node = self.get_start_node(id) # raises unhandled exception
        # Remove all commita after the node to be removed and before the next start node for the same file
        current = node.succ
        while current is not None:
            if current.filename != node.filename:
                current = current.succ
                continue
            if current.type == "start":
                break
            self._fs.destroy_snapshot(current.snapshot) # current.type == "commit"
            self._remove_node(current)
            current = current.succ
        self._fs.destroy_snapshot(node.snapshot)
        self._remove_node(node)

        del self._start_nodes[id]
        return 0

    def remove_from_management(self,fs_name):
        if fs_name not in self._headers: raise ex.FilesystemNotFoundException
        if self._headers[fs_name] is not None: raise ex.FilesystemInUseException
        del self._headers[fs_name]
        return 0
    # Method: remove_node -----------------------------------------------------
    # Internal method
    # [A] node actually exists
    def _remove_node(self,node):
        if node.pred == None:
            fs_name = self._fs.get_fs(node.file)
            self._headers[fs_name] = node.succ
            if node.succ is not None:
                node.succ.pred = None
            node.succ = None
        elif node.succ == None:
            node.pred.succ = node.succ
            node.pred = None
        else:
            node.pred.succ = node.succ
            node.succ.pred = node.pred
            node.succ = None
            node.pred = None
        self._fs.destroy_snapshot(node.snapshot)

    def get_start_node(self,id):
        try:
            node = self._start_nodes[id]
        except Exception:
            raise ex.TransactionInvalidException
        return node