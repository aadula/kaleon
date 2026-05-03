from flask import Flask, request, send_from_directory, make_response
import subprocess
import os
import uuid
import shutil


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)
UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
MARKER_BINARY = os.environ.get("MARKER_BINARY", "marker_single")
# OCR on large PDFs can run a long time; override with MARKER_TIMEOUT (seconds).
MARKER_TIMEOUT = int(os.environ.get("MARKER_TIMEOUT", "3600"))

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

    if not file.filename.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        return "Invalid file type", 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    workdir = None 

    try:
        # 1. Setup Workspace
        ram_disk = "/dev/shm" if os.path.exists("/dev/shm") else UPLOAD_FOLDER
        workdir = os.path.join(ram_disk, str(uuid.uuid4()))
        os.makedirs(workdir, exist_ok=True)

        # 2. Move to RAM
        input_in_ram = os.path.join(workdir, "input.pdf")
        shutil.copy(path, input_in_ram)

        # 3. Define High-Accuracy Marker Command
        # This list adds the specific flags for complex transcripts

        base_args = [
            input_in_ram, 
            "--output_dir", workdir, 
            "--force_ocr",                # Forces fresh OCR pass
            "--strip_existing_ocr",       # Cleans up messy PDF text layers
            "--html_tables_in_markdown",  # Better for transcript rows
            # "--use_llm", # Understands transcript layout
            "--highres_image_dpi", "300", # Better for small course codes
            "--add_block_ids"             # Helps identify specific data blocks
        ]

        # On Windows, you might need to call this through 'python -m' 
        # if the binary isn't in your direct PATH
                
        if os.name == 'nt':
            marker_exe = "marker_single.exe"
            if shutil.which(marker_exe):
                marker_command = [marker_exe] + base_args
            else:
                marker_command = ["python", "-m", "marker.convert_single"] + base_args
        else:
            # Raspberry Pi / Linux logic
            # You can explicitly point to /usr/bin/python3 to escape the venv
            marker_command = ["/usr/bin/python3", "-m", "marker.convert_single"] + base_args


        result = subprocess.run(
            marker_command,
            capture_output=True,
            text=True,
            timeout=MARKER_TIMEOUT,
        )

        if result.returncode != 0:
            return f"Marker error: {result.stderr or result.stdout}", 500

        # 4. Find and Read the generated .md file
        md_content = "Scan complete, but no text was extracted."
        for root, dirs, files in os.walk(workdir):
            for f in files:
                if f.endswith(".md"):
                    # Using utf-8-sig handles Windows/Linux encoding variations
                    with open(os.path.join(root, f), "r", encoding="utf-8-sig") as md_file:
                        md_content = md_file.read()
                    break
            if md_content != "Scan complete, but no text was extracted.":
                break

        return md_content

    except subprocess.TimeoutExpired as e:
        return (
            f"Marker timed out after {e.timeout} seconds. "
            "Increase MARKER_TIMEOUT (seconds) or use a smaller PDF / fewer pages.",
            504,
        )
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500

    finally:
        if os.path.exists(path):
            os.remove(path)
        if workdir and os.path.exists(workdir):
            shutil.rmtree(workdir)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3010"))
    app.run(host="0.0.0.0", port=port, debug=True)