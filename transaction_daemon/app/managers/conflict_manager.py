from . import filesystem_manager
import time
from ..utils import exceptions as ex

class __ConflictNode:
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
    # Method: initiate_start --------------------------------------------------
    # Inserts a node representing a transaction start into the conflict structure
    # Inserting a new transaction can not lead to any conflict
    def initiate_start(self,id,path):
        timestamp = time.time()
        snapshot = self._fs.create_snapshot(path,id)
        node = __ConflictNode(
            id,
            "start",
            timestamp,
            snapshot,
            path
        )
        # Find list header id, create one if necessary
        header_id = self._fs.get_fs(path)
        if header_id not in self._headers or self._headers[header_id] is None:
            self._headers[header_id] = node
            return 0
        # insert node at the right place
        current = self._headers[header_id]
        while current.succ != None and current.succ.timestamp <= node.timestamp: # O(n)
            current = current.succ
        node.succ = current.succ
        node.pred = current
        current.succ = node
        if not node.succ is None: 
            node.succ.pred = node
        self._start_nodes[id] = node
        return 0
    # Method: initiate_commit -------------------------------------------------
    # Adds a commit of a transaction to the conflict structure
    # Checks if insertion leads to a conflict
    # if yes, remove all nodes after the start node
    def initiate_commit(self,id):
        start_node = self.get_start_node(id)
        file = start_node.file
        timestamp = time.time()
        node = __ConflictNode(
            id,
            "commit",
            timestamp,
            None,
            file
        )
        # Find node to insert the new node after
        current = start_node
        while current.succ != None and current.succ.timestamp <= node.timestamp:
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
        # Conflict handling
        if conflict:
            self._fs.restore_snapshot(start_node.snapshot)
            current = start_node
            while current is not None:
                if current.type == "start": 
                    del self._start_nodes[current.id]
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
            if not conflict_potential: self._remove_node(node)
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
    # Method: remove_node -----------------------------------------------------
    # Internal method
    # [A] node actually exists
    def _remove_node(self,node):
        if node.pred == None:
            fs_name = self._fs.get_fs(node.file)
            self._headers[fs_name] = node.succ
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

    def get_start_node(self,id):
        try:
            node = self._start_nodes[id]
        except Exception:
            raise ex.TransactionInvalidException
        return node