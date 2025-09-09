import os
from flask import Flask, render_template, request, jsonify, send_file, abort
from dotenv import load_dotenv

from utils import new_job_id, read_status, list_media, make_zip, job_dir
from insta_worker import start_worker

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/scrape")
def api_scrape():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username wajib diisi"}), 400

    ig_user = (data.get("ig_user") or os.getenv("IG_USER") or "").strip() or None
    ig_pass = (data.get("ig_pass") or os.getenv("IG_PASS") or "").strip() or None
    only_videos = bool(data.get("only_videos", True))
    max_posts = int(data.get("max_posts", 50))
    max_posts = max(1, min(max_posts, 1000))

    job_id = new_job_id()

    start_worker(
        job_id=job_id,
        username=username,
        ig_user=ig_user,
        ig_pass=ig_pass,
        max_posts=max_posts,
        only_videos=only_videos
    )

    return jsonify({"job_id": job_id})

@app.get("/api/status/<job_id>")
def api_status(job_id: str):
    return jsonify(read_status(job_id))

@app.get("/api/results/<job_id>")
def api_results(job_id: str):
    return jsonify({"items": list_media(job_id)})

@app.get("/download/<job_id>.zip")
def download_zip(job_id: str):
    try:
        z = make_zip(job_id)
        return send_file(z, as_attachment=True, download_name=f"{job_id}.zip")
    except Exception:
        abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
