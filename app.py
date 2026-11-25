from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT = Path(__file__).parent
VIDEO_ROOT = Path(r"C:\Users\DESKTOP\Documents\Codex\2026-11-19\vc\outputs\GTA-VI-23-11\envio")
STATE = ROOT / "state.json"

def state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"interval_minutes": 15, "posted": []}

def save(data):
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class Handler(BaseHTTPRequestHandler):
    def json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/queue":
            current = state()
            files = sorted(VIDEO_ROOT.glob("*.mp4")) if VIDEO_ROOT.exists() else []
            self.json({"interval_minutes": current["interval_minutes"], "posted": current["posted"], "items": [f.stem for f in files]})
            return
        if self.path == "/":
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        current = state()
        if self.path == "/api/settings":
            current["interval_minutes"] = max(15, int(payload.get("interval_minutes", 15)))
        if self.path == "/api/posted" and payload.get("id") not in current["posted"]:
            current["posted"].append(payload["id"])
        save(current)
        self.json(current)

if __name__ == "__main__":
    save(state())
    print("GTA Clip Factory: http://127.0.0.1:8765", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()

