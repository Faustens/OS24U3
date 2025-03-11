import subprocess
import os
from ..utils import exceptions as ex
from ..utils import logging

# =================================================================================================
# Class: FilesystemManager
# -------------------------------------------------------------------------------------------------
# Provides a number of methods to interact with the file system, zfs datasets and zfs snapshots
# Locks all managed filesystems/zfs pools, such that only sudo can directly manipulate files
#  without the use of this program
# It is assumed that the root folder "/" and specifically "/tmp" are not (part of) a zfs file system
# =================================================================================================
class FilesystemManager:
    _instance = None

    def __init__(self):
        if hasattr(self,"_initialized") and self._initialized: return
        self._initialized = True
        self._instance = None
        self._top_level_fs = [] # List of all pools whose mount folder is also a zfs filesystem
        self._filesystems = []  # List of all current zfs filesystems
        self.logger = logging.Logger()
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
            for fs in self._top_level_fs:
                self._filesystems.append(fs)

            self.logger.log(f"[FM][INFO] top level filesystems: {self._top_level_fs}")
            self.logger.log(f"[FM][INFO] filesystems: {self._filesystems}")
        except subprocess.CalledProcessError as e:
            raise ex.ZfsError
        finally:
            if len(self._top_level_fs) == 0: raise ex.ZfsError

        self._filecopy_path = f'/tmp/transaction_manager/filecopies'
        subprocess.run(["mkdir", "-p", self._filecopy_path])
        subprocess.run(["chmod", "777", self._filecopy_path])
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            print(f"[FM][INFO] new instance {cls._instance} created")
        return cls._instance
# =============================================================================
# ZFS Dataset Interaction
# =============================================================================
    # Method: get_fs ----------------------------------------------------------
    # Takes in a path and returns the corresponding filesystem.
    # Raises an exception if the path does not exist as a filesystem
    def get_fs(self,path,is_file=True):
        if not is_file: 
            path = f'{path}{os.sep}' # Add Separator to force 'path' to be interpreted as having no file
        fs_name = os.path.dirname(path).strip(os.sep)
        if fs_name not in self._filesystems: raise ex.FilesystemNotFoundException
        return fs_name
    # Method: make_fs ---------------------------------------------------------
    # Takes a path and creates a corresponding filesystem that acts like a path internally
    # Wille create a filesystem and folder structure with the given names, even
    # when path = "/tank/file.txt" ('file.txt' will be a folder!)
    def make_fs(self,path):
        fs_name = path.strip(os.sep)
        if fs_name in self._filesystems: raise ex.FilesystemExistsException
        if not any(top_level_fs in fs_name for top_level_fs in self._top_level_fs): 
            raise ex.TopLevelFsNotFoundException
        subprocess.run(["sudo","zfs","create",fs_name])
        self._filesystems.append(fs_name)
        return 0
    # Method: destroy_fs ------------------------------------------------------
    # Takes a path and destroys the corresponding filesystem, if it exists
    # If a path has subpaths or subdirectories only the files in the given path will
    # be destroyed (i.e.: if tank/foo is destroyed, but tank/foo/bar exists, the second will be preserved
    # [WARNING] All files in dataset will be lost, use with caution!
    def destroy_fs(self,path):
        fs_name = path.strip(os.sep)
        if fs_name not in self._filesystems: return 0
        subprocess.run(["sudo", "zfs", "destroy", "-r", fs_name])
        self._filesystems.remove(fs_name)
        return 0
# =============================================================================
# ZFS Snapshot Interaction
# =============================================================================
    def create_snapshot(self,path,id):
        fs_name = self.get_fs(path, is_file=False)
        if fs_name not in self._filesystems: raise ex.PathNotFoundException
        snap_name = f'{fs_name}@{id}'
        subprocess.run(["sudo", "zfs", "snapshot", snap_name])
        self.logger.log(f"[FM][INFO] Snapshot {snap_name} created")
        return snap_name
    # [TODO] Error handling
    def restore_snapshot(self, snap_name):
        subprocess.run(["sudo","zfs","rollback","-r",snap_name])
    def destroy_snapshot(self,snap_name):
        if snap_name is None: return
        subprocess.run(["sudo","zfs","destroy",snap_name])
        self.logger.log(f"[FM][INFO] Snapshot {snap_name} destroyed")
# =============================================================================
# File Interaction
# =============================================================================
    # Method: create_file_copy ------------------------------------------------
    # [EX] FileNotFoundError, ex.FilesystemNotFoundException, ex.NotAFileException
    def create_file_copy(self, origin_path, id):
        self.get_fs(origin_path) # Crude way to check if the path actually exists.
        if not os.path.exists(origin_path): raise FileNotFoundError
        if not os.path.isfile(origin_path): raise ex.NotAFileException
        _, filename = os.path.split(origin_path)
        copy_filename = f'{id}_{filename}'
        copy_path = f'{self._filecopy_path}/{copy_filename}'
        subprocess.run(["sudo", "touch", copy_path])
        subprocess.run(["sudo", "chmod", "666", copy_path])
        return copy_path
    def delete_file_copy(self,copy_path):
        if not os.path.exists(copy_path): return 0
        subprocess.run(["sudo", "rm", copy_path])
        
    # Method: create_file -----------------------------------------------------
    # [EX] ex.NotAFileException, ex.FilesystemNotFoundException,
    def create_file(self,path):
        _, filename = os.path.split(path)
        if filename == "": raise ex.NotAFileException
        self.get_fs(path)
        subprocess.run(["sudo", "touch", path])
    # Method: delete_file -----------------------------------------------------
    # [EX] ex.NotAFileException, ex.FilesystemNotFoundException
    def delete_file(self,path):
        if not os.path.isfile(path): raise ex.NotAFileException
        self.get_fs(path)
        print("before deletion")
        subprocess.run(["sudo","rm", path])
    # Method: overwrite_file --------------------------------------------------
    def overwrite_file(self, origin_path, copy_path):
        try:
            self.get_fs(origin_path)
            subprocess.run(["sudo", "mv", copy_path, origin_path])
            subprocess.run(["sudo", "chmod", "644", origin_path])
            self.logger.log(f"[FM][INFO] {copy_path} -> {origin_path}")
        except Exception:
            self.delete_file(copy_path)


        