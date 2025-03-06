import subprocess
import os
from ..utils import exceptions as ex

# It is assumed that the root folder "/" and specifically "/tmp" is not (part of) a zfs file system
class FilesystemManager:
    _instance = None

    def __init__(self):
        self._instance = None
        self._top_level_fs = [] # List of all pools whose mount folder is also a zfs filesystem
        self._filesystems = []  # List of all current zfs filesystems
        # TODO Find all current top level fs and all filesystems
        try:
            result = subprocess.run(
                ["zfs", "list", "-H", "-o", "name,mountpoint"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                name, mountpoint = line.split("\t")
                if mountpoint != "legacy" and mountpoint != "-":
                    self._top_level_fs.append(name)
        except subprocess.CalledProcessError as e:
            raise ex.ZfsError
        finally:
            if len(self._top_level_fs) == 0: raise ex.ZfsError

        self._filecopy_path = f'/tmp/transaction_manager/filecopies'
        subprocess.run(["mkdir", "-r", self._filecopy_path])
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_instance(self):
        if self._instance == None: self._instance = FilesystemManager()
        return self._instance
# =============================================================================
# ZFS Interaction
# =============================================================================
    # Method: get_fs ----------------------------------------------------------
    # Takes in a path and returns the corresponding filesystem. creates a new filesystem if it doesn't exist yet
    def get_fs(self,path):
        if not os.path.isfile(path): path = f'{path}{os.sep}'
        fs_name = os.path.dirname(path).strip(os.sep)
        if fs_name not in self._filesystems:
            if not any(top_level_fs in fs_name for top_level_fs in self._top_level_fs): raise ex.TopLevelFsNotFoundException
            subprocess.run(["zfs","create",fs_name])
            self._filesystems.append(fs_name)
        return fs_name
    # Snapshots --------------------------------------------------------------
    def create_snapshot(self,path,id):
        fs_name = self.get_fs(path)
        snap_name = f'{fs_name}@{id}'
        subprocess.run(["zfs", "snapshot", snap_name])
        return snap_name
    # [TODO] Error handling
    def restore_snapshot(self, snap_name):
        subprocess.run(["zfs","rollback","-r",snap_name])
    def destroy_snapshot(self,snap_name):
        subprocess.run(["zfs","destroy",snap_name])
# =============================================================================
# File Interaction
# =============================================================================
    def create_file_copy(self, origin_path, id):
        _, filename = os.path.split(origin_path)
        copy_filename = f'{id}_{filename}'
        copy_path = f'{self._filecopy_path}/{copy_filename}'
        subprocess.run(["touch", copy_path])
        return copy_path
    # TODO
    def create_file(self,path):
        dirname, _ = os.path.split()
        if not os.path.exists(dirname): raise ex.PathNotFoundException
        subprocess.run["touch", path]

    def delete_file(self,path):
        if not os.path.exists(path): raise ex.PathNotFoundException
        if not os.path.isfile(path): raise ex.NotAFileException
        if os.path.exists(path): raise FileExistsError
        subprocess.run(["rm", path])
        
    def overwrite_file(self, origin_path, copy_path):
        subprocess.run(["cp", copy_path, origin_path])