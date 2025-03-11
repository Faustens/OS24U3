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
    return jsonify({"uuid": uuid}), 200

@api_bp.route("/deregister", methods=["DELETE"])
def deregister():
    data = request.json
    try:
        _tm.deregister_user(data["uuid"])
        return jsonify({"answer":"success"}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users", "code": "400"}), 400
    pass

@api_bp.route("/open_file", methods=["POST"])
def open_file():
    data = request.json
    try:
        uuid = data["uuid"]
        path = data["path"]
        tid, copy_path = _tm.open_file(uuid, path)
        return jsonify({"tid": tid, "copy_path": copy_path}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except FileNotFoundError:
        return jsonify({ "error": "Invalid Request", "message": "Path does not exist"}), 400
    except ex.NotAFileException:
        return jsonify({ "error": "Invalid Request", "message": "Path is not a file"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/commit_file", methods=["POST"])
def commit_file():
    data = request.json
    try:
        tid = data["tid"]
        _tm.commit_file(tid)
        return jsonify({"answer":"success"}), 200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except ex.TransactionInvalidException:
        return jsonify({ "error": "Invalid Transaction", "message": "Transaction has been invalidated or never existed"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    
@api_bp.route("/close_file", methods=["DELETE"])
def close_file():
    data = request.json
    try:
        tid = data["tid"]
        _tm.close_file(tid)
        return jsonify({"answer":"success"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not part of a valid pool"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/make_file", methods=["POST"])
def make_file():
    data = request.json
    try:
        uuid = data["uuid"]
        path = data["path"]
        _tm.create_file(uuid,path)
        return jsonify({"answer":"success"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not part of a valid pool"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/delete_file", methods=["POST"])
def delete_file():
    data = request.json
    try:
        uuid = data["uuid"]
        path = data["path"]
        _tm.delete_file(uuid,path)
        return jsonify({"answer":"success"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except FileNotFoundError:
        return jsonify({ "error": "Invalid Request", "message": "File not found"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except ex.NotAFileException:
        return jsonify({ "error": "Invalid Request", "message": "Path is not a file"}), 400   
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/make_directory", methods=["POST"])
def make_directory():
    data = request.json
    try:
        uuid = data["uuid"]
        path = data["path"]
        _tm.create_directory(uuid,path)
        return jsonify({"answer":"success"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not part of a valid pool"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@api_bp.route("/delete_directory", methods=["DELETE"])
def delete_directory():
    data = request.json
    try:
        uuid = data["uuid"]
        path = data["path"]
        _tm.delete_directory(uuid,path)
        return jsonify({"answer":"success"}),200
    except KeyError:
        return jsonify({ "error": "Invalid Request", "message": "Missing values in JSON"}), 400
    except ex.TopLevelFsNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "Path not part of a valid pool"}), 400
    except ex.UserNotFoundException:
        return jsonify({ "error": "Invalid Request", "message": "UUID not in users"}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500