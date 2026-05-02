from flask import Flask, request, send_from_directory, make_response
import subprocess
import os
import uuid

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)
UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
MARKER_BINARY = os.environ.get("MARKER_BINARY", "marker_single")

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
    if request.method == "OPTIONS":
        return make_response("", 204)

    file = request.files.get('file')

    if not file:
        return "No file uploaded", 400

    # basic file type check
    if not file.filename.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        return "Invalid file type", 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    try:
        output_file = path + ".md"
        result = subprocess.run(
            ["./process.sh", path, output_file],
            capture_output=True,
            text=True,
            timeout=500,
        )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or "marker command failed with no output"
            return f"marker error: {details}", 500

        return result.stdout or "Scan complete, but marker returned empty output."

    except FileNotFoundError:
        return (
            f"marker binary not found: '{MARKER_BINARY}'. "
            "Set MARKER_BINARY or ensure marker_single is in PATH.",
            500,
        )
    except subprocess.TimeoutExpired:
        return "marker scan timed out after 300 seconds.", 504
    except Exception as exc:
        return f"unexpected scan failure: {type(exc).__name__}: {exc}", 500

    finally:
        # cleanup: delete file after processing
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3010"))
    app.run(host="0.0.0.0", port=port, debug=True)