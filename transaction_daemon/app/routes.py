from flask import Blueprint, jsonify, request
from .managers.transaction_manager import TransactionManager
from .utils import exceptions as ex

api_bp = Blueprint("api", __name__)
_tm = TransactionManager()

@api_bp.route("/status", methods=["GET"])
def status():
    return jsonify({"message": "API is running"}), 200

@api_bp.route("/register", methods=["GET"])
def register():
    uuid = _tm.regiser_user()
    return jsonify({"uuid":uuid,"code":"200"}), 200

@api_bp.route("/deregister", methods=["POST"])
def deregister():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        _tm.deregister_user(uuid)
        return jsonify({"answer":"success","code":"200"}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code": "400"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code": "401"}), 400
    except Exception:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/open_file", methods=["POST"])
def open_file():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        path = data["path"].strip()
        tid, copy_path = _tm.open_file(uuid, path)
        return jsonify({"tid": tid, "copy_path": copy_path,"code":"200"}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code":"401"}), 400
    except FileNotFoundError:
        return jsonify({ "error": "Invalid Request", "message": "File does not exist", "code":"403"}), 400
    except ex.NotAFileException:
        return jsonify({ "error": "Invalid Request", "message": "Path is not a file", "code":"403"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Mountpoint is not managed by zfs", "code":"407"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/commit_file", methods=["POST"])
def commit_file():
    data = request.json
    try:
        tid = data["tid"].strip()
        _tm.commit_file(tid)
        return jsonify({"answer":"success","code":"200"}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.TransactionInvalidException:
        return jsonify({ "error": "Invalid Transaction", "message": "Transaction has been invalidated or never existed", "code":"402"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    
@api_bp.route("/close_file", methods=["POST"])
def close_file():
    data = request.json
    try:
        tid = data["tid"].strip()
        _tm.close_file(tid)
        return jsonify({"answer":"success","code":"200"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/make_file", methods=["POST"])
def make_file():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        path = data["path"].strip()
        _tm.create_file(uuid,path)
        return jsonify({"answer":"success","code":"200"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Mountpoint is not managed by zfs", "code":"407"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code":"401"}), 400
    except ex.NotAFileException:
        return jsonify({ "error": "Invalid Request", "message": "Provided path is not a File", "code":"403"}), 400
    except ex.FilesystemNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not found", "code":"405"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/delete_file", methods=["POST"])
def delete_file():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        path = data["path"].strip()
        _tm.delete_file(uuid,path)
        return jsonify({"answer":"success","code":"200"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code":"401"}), 400
    except FileNotFoundError:
        return jsonify({ "error": "Invalid Request", "message": "File does not exist", "code":"403"}), 400
    except ex.NotAFileException:
        return jsonify({ "error": "Invalid Request", "message": "Path is not a file", "code":"403"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Mountpoint is not managed by zfs", "code":"407"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/make_directory", methods=["POST"])
def make_directory():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        path = data["path"].strip()
        _tm.create_directory(uuid,path)
        return jsonify({"answer":"success","code":"200"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Mountpoint is not managed by zfs", "code":"407"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code":"401"}), 400
    except ex.FilesystemExistsException:
        return jsonify({ "error": "Invalid Request", "message": "Path already exists", "code":"406"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/delete_directory", methods=["POST"])
def delete_directory():
    data = request.json
    try:
        uuid = data["uuid"].strip()
        path = data["path"].strip()
        _tm.delete_directory(uuid,path)
        return jsonify({"answer":"success","code":"200"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON", "code":"400"}), 400
    except ex.UserError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code":"401"}), 400
    except ex.FilesystemNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not managed", "code":"407"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Mountpoint is not managed by zfs", "code":"407"}), 400
    except ex.FilesystemInUseException:
        return jsonify({ "error": "Invalid Request", "message": "Filesystem has open transactions", "code":"408"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500