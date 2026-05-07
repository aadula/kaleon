# Kaleon

A simple Kaleon landing page with a cyber-space visual theme.

Open `index.html` in a browser to preview the site.

## OCR Demo Server (Chandra)

The transcript scanner endpoint (`POST /scan`) is powered by `chandra-ocr`.

### Install

```bash
pip install chandra-ocr
```

If you prefer HuggingFace local inference explicitly:

```bash
pip install "chandra-ocr[hf]"
```

### Run

macOS:

```bash
./run_chandra_server_mac.sh
```

Windows:

```powershell
.\run_chandra_server_win.ps1
```

The server defaults to `http://127.0.0.1:3010`.

### Environment variables

- `CHANDRA_BINARY` (default: `chandra`)
- `CHANDRA_METHOD` (default: `hf`)
- `CHANDRA_TIMEOUT` in seconds (default: `3600`)
