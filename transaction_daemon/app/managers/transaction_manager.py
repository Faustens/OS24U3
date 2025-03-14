import uuid as other_uuid
from itertools import count
from . import filesystem_manager
from . import conflict_manager
import os
from ..utils import exceptions as ex
from ..utils import logging

# TODO Logging! (-> utils Logger schreiben, prolly gibt es auch einen den ich importieren kann)
class TransactionManager:
    def __init__(self):
        self._transactions = {}
        self._users = {}
        self._fm = filesystem_manager.FilesystemManager()
        self._cm = conflict_manager.ConflictManager()
        self.logger = logging.Logger()
        pass

# =============================================================================
# User Management
# =============================================================================
    def regiser_user(self):
        uuid = str(other_uuid.uuid4())
        self._users[uuid] = { 
            "utn_counter": count(1) 
        }
        self.logger.log(f'[TM][INFO] registered new user as \'{uuid}\'')
        return uuid
    def deregister_user(self,uuid):
        print(f"'{uuid}'")
        if uuid not in self._users: raise ex.UserError
        del self._users[uuid]
        self.logger.log(f'[TM][INFO] deregistered user \'{uuid}\'')
        return 0
# =============================================================================
# File Transactions
# =============================================================================
    # Method: open_file -------------------------------------------------------
    def open_file(self,uuid,origin_path):
        if not os.path.exists(origin_path): raise FileNotFoundError
        if not os.path.isfile(origin_path): raise ex.NotAFileException
        if uuid not in self._users: raise ex.UserError
        # Generate TID
        utn = next(self._users[uuid]["utn_counter"])
        tid = f'{uuid}_{utn}'
        # Create copy of file in tmp directory
        copy_path = self._fm.create_file_copy(origin_path,tid)
        # Create transaction
        transaction = {
            "type": "open_file",
            "origin_path": origin_path,
            "copy_path": copy_path,
            "status": "open"
        }
        self._transactions[tid] = transaction
        # Insert  relevant data into conflict management structure
        print("Before conflict start init")
        self._cm.initiate_start(tid,origin_path)
        self.logger.log(f"[TM][INFO] new transaction '{tid}' opened")
        print("open_file successfuly run")
        return tid, copy_path
    
    def commit_file(self,tid):
        try:
            transaction = self._transactions[tid]
            self._cm.initiate_commit(tid)
            self._fm.overwrite_file(transaction["origin_path"], transaction["copy_path"])
            self.logger.log(f"[TM][INFO] transaction '{tid}' successfully committed")
        except KeyError:
            raise ex.TransactionInvalidException
        except ex.TransactionInvalidException:
            self._fm.delete_file_copy(transaction["copy_path"])
            raise ex.TransactionInvalidException
        finally:
            transaction["status"] = "closed"
            del self._transactions[tid]
            # TODO Remove snapshot

    def close_file(self,tid):
        transaction = self._transactions[tid]
        self._cm.cancel(tid)
        print(f"Before copy deletion: {transaction['copy_path']}")
        self._fm.delete_file_copy(transaction["copy_path"])
        self.logger.log(f"[TM][INFO] transaction '{tid}' successfully cancelled")
        del self._transactions[tid]
    
    # File creations can never cause conflicts only be affected by them
    def create_file(self,uuid,path):
        if uuid not in self._users: raise ex.UserError
        self._fm.create_file(path)
        return 0

    # File deletions can cause conflicts and are handled like normal commits
    def delete_file(self,uuid,path):
        if not os.path.exists(path): raise FileNotFoundError
        if not os.path.isfile(path): raise ex.NotAFileException
        if uuid not in self._users: raise ex.UserError
        # Generate TID
        utn = next(self._users[uuid]["utn_counter"])
        tid = f'{uuid}_{utn}'
        # Create copy of file in tmp directory
        # Create transaction
        transaction = {
            "type": "delete_file",
            "origin_path": path,
            "copy_path": None,
            "status": "open"
        }
        self._transactions[tid] = transaction
        # Insert  relevant data into conflict management structure
        self._cm.initiate_start(tid,path)
        self.logger.log(f"[TM][INFO] new transaction '{tid}' opened")
        self._fm.delete_file(path)
        self._cm.initiate_commit(tid)
        return tid
    # Method: create_directory ------------------------------------------------
    # Creates a directory by creating a filesystem
    def create_directory(self,uuid,path):
        if uuid not in self._users: raise ex.UserError
        try:
            self._fm.make_fs(path)
        except ex.FilesystemExistsException:
            pass
        return 0
    # Method: delete_directory ------------------------------------------------
    # Removes the given path by destroying the dataset
    # Only possible if no transactions are currently open
    def delete_directory(self,uuid,path):
        if uuid not in self._users: raise ex.UserError
        fs_name = self._fm.get_fs(path,is_file=False)
        self._cm.remove_from_management(fs_name)
        self._fm.destroy_fs(path)
        return 0

