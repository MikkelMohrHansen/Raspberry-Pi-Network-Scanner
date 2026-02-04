# Endpoints/ScannerEndpoints.py
from flask import Blueprint, request, jsonify
from Database import DB_Data
from Scanner import scanner

DB_bp = Blueprint("DB_bp", __name__)

def _json():
    return request.get_json(silent=True) or {}

@DB_bp.get("/getApproved")
def get_approved():
    return jsonify(DB_Data.get_approved()), 200

@DB_bp.get("/getUnapproved")
def get_unapproved():
    return jsonify(DB_Data.get_unapproved()), 200

@DB_bp.post("/addUnapproved")
def add_unapproved():
    data = _json()
    DB_Data.add_unapproved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
        description=data.get("description"),
        vendor=data.get("vendor"),
        first_seen=data.get("first_seen"),
        last_seen=data.get("last_seen"),
    )
    return jsonify({"ok": True}), 201

@DB_bp.post("/addApproved")
def add_approved():
    data = _json()
    DB_Data.add_approved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
        description=data.get("description"),
        vendor=data.get("vendor"),
        first_seen=data.get("first_seen"),
        last_seen=data.get("last_seen"),
    )
    return jsonify({"ok": True}), 201

@DB_bp.put("/updateUnApproved")
def update_unapproved():
    data = _json()
    DB_Data.update_unapproved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
        description=data.get("description"),
        vendor=data.get("vendor"),
        first_seen=data.get("first_seen"),
        last_seen=data.get("last_seen"),
    )
    return jsonify({"ok": True}), 200

@DB_bp.put("/updateApproved")
def update_approved():
    data = _json()
    DB_Data.update_approved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
        description=data.get("description"),
        vendor=data.get("vendor"),
        first_seen=data.get("first_seen"),
        last_seen=data.get("last_seen"),
    )
    return jsonify({"ok": True}), 200

@DB_bp.delete("/removeApproved")
def remove_approved():
    data = _json()
    DB_Data.remove_approved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
    )
    return jsonify({"ok": True}), 200

@DB_bp.delete("/removeUnapproved")
def remove_unapproved():
    data = _json()
    DB_Data.remove_unapproved(
        mac_address=data.get("mac_address"),
        ip_address=data.get("ip_address"),
    )
    return jsonify({"ok": True}), 200

