from flask import Blueprint, request, jsonify

from Scanner import scanner

Scanner_bp = Blueprint("scanner_bp", __name__)

@Scanner_bp.post("/StartScan")
def start_scan():
    scanner.main()
    return jsonify({"ok": True, "message": "Scan started"}), 200