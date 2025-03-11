#!/usr/bin/env ./env/bin/python

from app.managers.filesystem_manager import FilesystemManager

_fm = FilesystemManager()

print("Create fs")
_fm.make_fs("/mypool/foo")
input("Press any key")

print("Create file")
_fm.create_file("/mypool/foo/bar.txt")
input("Press any key")

print("Create snapshot")
snap_name = _fm.create_snapshot("mypool/foo", "1")
input("Press any key")

print("Delete file")
_fm.delete_file("/mypool/foo/bar.txt")
input("Press any key")

print("Restore snapshot")
_fm.restore_snapshot(snap_name)
input("Press any key")

print("Destroy fs")
_fm.destroy_fs("/mypool/foo")
input("Press any key")