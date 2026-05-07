from flask import Flask, request, send_from_directory, make_response
import subprocess
import os
import sys
import uuid
import shutil
from typing import Optional


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)
UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
CHANDRA_BINARY = os.environ.get("CHANDRA_BINARY", "chandra")
CHANDRA_METHOD = os.environ.get("CHANDRA_METHOD", "hf")
# OCR on large PDFs/images can run a long time; override with CHANDRA_TIMEOUT (seconds).
CHANDRA_TIMEOUT = int(os.environ.get("CHANDRA_TIMEOUT", "3600"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    # Serve the existing static site entrypoint from repo root.
    return send_from_directory(APP_ROOT, "demo.html")


@app.get("/healthz")
def healthz():
    return "ok"


@app.get("/<path:path>")
def static_files(path: str):
    # Serve other static assets (styles.css, images, etc.) from repo root.
    return send_from_directory(APP_ROOT, path)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response



@app.route('/scan', methods=['POST', 'OPTIONS'])
def scan():
    """Accept an uploaded PDF/image; save it, run Chandra once, return markdown."""
    if request.method == "OPTIONS":
        return make_response("", 204)

    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400

    if not file.filename.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        return "Invalid file type", 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    workdir = None

    try:
        # 1. Setup workspace.
        ram_disk = "/dev/shm" if os.path.exists("/dev/shm") else UPLOAD_FOLDER
        workdir = os.path.join(ram_disk, str(uuid.uuid4()))
        os.makedirs(workdir, exist_ok=True)

        # 2. Move input to working dir.
        original_ext = os.path.splitext(file.filename)[1].lower() or ".pdf"
        input_in_ram = os.path.join(workdir, f"input{original_ext}")
        shutil.copy(path, input_in_ram)

        # 3. Run Chandra as soon as this upload is on disk (same request; no separate queue).
        # Chandra expects: chandra <input_file_or_dir> <output_dir> [flags]
        base_args = [input_in_ram, workdir, "--method", CHANDRA_METHOD]

        if shutil.which(CHANDRA_BINARY):
            chandra_command = [CHANDRA_BINARY] + base_args
        else:
            # Fallback for environments where console script is unavailable.
            chandra_command = [sys.executable, "-m", "chandra.cli.main"] + base_args

        result = subprocess.run(
            chandra_command,
            capture_output=True,
            text=True,
            timeout=CHANDRA_TIMEOUT,
        )

        if result.returncode != 0:
            return f"Chandra error: {result.stderr or result.stdout}", 500

        # 4. Find and read the generated markdown output.
        md_content = "Scan complete, but no text was extracted."
        for root, dirs, files in os.walk(workdir):
            for f in files:
                if f.endswith(".md"):
                    # utf-8-sig handles Windows/Linux encoding variations.
                    with open(os.path.join(root, f), "r", encoding="utf-8-sig") as md_file:
                        md_content = md_file.read()
                    break
            if md_content != "Scan complete, but no text was extracted.":
                break

        return md_content

    except subprocess.TimeoutExpired as e:
        return (
            f"Chandra timed out after {e.timeout} seconds. "
            "Increase CHANDRA_TIMEOUT (seconds) or use a smaller file / fewer pages.",
            504,
        )
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500

    finally:
        if os.path.exists(path):
            os.remove(path)
        if workdir and os.path.exists(workdir):
            shutil.rmtree(workdir)


def _delegate_to_platform_launcher() -> Optional[int]:
    """Windows -> PowerShell launcher; macOS -> bash launcher.

    Set CHANDRA_SERVER_NO_DELEGATE=1 (done by the scripts) to run Flask directly.
    """
    if os.environ.get("CHANDRA_SERVER_NO_DELEGATE"):
        return None

    if os.name == "nt":
        ps1 = os.path.join(APP_ROOT, "run_chandra_server_win.ps1")
        if not os.path.isfile(ps1):
            # Backward compatibility with existing script names.
            ps1 = os.path.join(APP_ROOT, "run_marker_server_win.ps1")
        if not os.path.isfile(ps1):
            return None
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                ps1,
            ],
            cwd=APP_ROOT,
        )
        return completed.returncode

    if sys.platform == "darwin":
        sh = os.path.join(APP_ROOT, "run_chandra_server_mac.sh")
        if not os.path.isfile(sh):
            # Backward compatibility with existing script names.
            sh = os.path.join(APP_ROOT, "run_marker_server_mac.sh")
        if not os.path.isfile(sh):
            return None
        completed = subprocess.run(["/bin/bash", sh], cwd=APP_ROOT)
        return completed.returncode

    return None


if __name__ == "__main__":
    delegated = _delegate_to_platform_launcher()
    if delegated is not None:
        sys.exit(delegated)

    port = int(os.environ.get("PORT", "3010"))
    app.run(host="0.0.0.0", port=port, debug=True)