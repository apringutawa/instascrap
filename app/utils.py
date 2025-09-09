import os, shutil, zipfile, uuid
from datetime import datetime

DATA_DIR = os.path.abspath(os.getenv("DATA_DIR", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

def new_job_id() -> str:
    return uuid.uuid4().hex[:12]

def job_dir(job_id: str) -> str:
    d = os.path.join(DATA_DIR, job_id)
    os.makedirs(d, exist_ok=True)
    return d

def write_status(job_id: str, status: str, detail: dict | None = None):
    d = job_dir(job_id)
    with open(os.path.join(d, "status.txt"), "w", encoding="utf-8") as f:
        f.write(status)
    if detail:
        import json
        with open(os.path.join(d, "detail.json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)

def read_status(job_id: str) -> dict:
    d = job_dir(job_id)
    status_path = os.path.join(d, "status.txt")
    detail_path = os.path.join(d, "detail.json")
    status = "unknown"
    detail = {}
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            status = f.read().strip()
    if os.path.exists(detail_path):
        import json
        with open(detail_path, "r", encoding="utf-8") as f:
            detail = json.load(f)
    return {"status": status, "detail": detail}

def list_media(job_id: str) -> list[dict]:
    d = job_dir(job_id)
    results_json = os.path.join(d, "results.json")
    if os.path.exists(results_json):
        import json
        with open(results_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_results(job_id: str, items: list[dict]):
    d = job_dir(job_id)
    import json
    with open(os.path.join(d, "results.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def make_zip(job_id: str) -> str:
    d = job_dir(job_id)
    zip_path = os.path.join(d, f"{job_id}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(d):
            for name in files:
                if name.endswith((".mp4", ".mov", ".mkv", ".m4v", ".webm", ".jpg", ".png")):
                    full = os.path.join(root, name)
                    arc = os.path.relpath(full, d)
                    z.write(full, arcname=arc)
    return zip_path

def clean_job(job_id: str):
    d = job_dir(job_id)
    shutil.rmtree(d, ignore_errors=True)
