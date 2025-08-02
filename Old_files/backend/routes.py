from flask import Blueprint, request, jsonify, send_file
from backend.orchestrator import run_agent_task
from pathlib import Path

api = Blueprint("api", __name__)

@api.route("/task", methods=["POST"])
def handle_task():
    """
    Genel API endpoint: Her bir buton buraya istek atar.
    URL parametresi: task_name=worldcloud | summarize | transcribe | ...
    Body: Göreve göre gerekli input JSON verisi
    """
    task_name = request.args.get("task_name")
    if not task_name:
        return jsonify({"error": "task_name parametresi eksik"}), 400

    try:
        input_data = request.get_json()
        output = run_agent_task(task_name, input_data)
        return jsonify({"result": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/download")
def download_file():
    file = request.args.get("file")
    if not file or not Path(file).exists():
        return "Dosya bulunamadı.", 404
    return send_file(file, as_attachment=True)