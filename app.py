from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re

ROOT = Path(__file__).parent
VIDEO_ROOT = Path(r"C:\Users\DESKTOP\Documents\Codex\2026-11-19\vc\outputs\GTA-VI-23-11\envio")
STATE = ROOT / "state.json"

def state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"interval_minutes": 15, "posted": []}

def save(data):
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

KEYWORDS = {
    "susto": 5, "assust": 5, "risada": 5, "rindo": 4, "kkkk": 4,
    "descob": 4, "curios": 3, "reacao": 3, "reação": 3, "inedit": 3,
    "segredo": 4, "bug": 2, "npc": 2, "louco": 2, "plot": 2,
}

def score(name):
    text = name.lower()
    points = sum(v for k, v in KEYWORDS.items() if k in text)
    # Penaliza arquivos genéricos, que normalmente não têm contexto suficiente.
    if re.search(r"(teste|test|sem[-_ ]?titulo|clip[-_ ]?\d+$)", text):
        points -= 4
    return max(0, points)

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
            items = [{"id": f.stem, "score": score(f.stem)} for f in files]
            items.sort(key=lambda x: (-x["score"], x["id"]))
            self.json({"interval_minutes": current["interval_minutes"], "posted": current["posted"], "items": [x["id"] for x in items], "scores": {x["id"]: x["score"] for x in items}, "minimum_score": 4})
            return
        if self.path == "/api/next":
            current = state()
            files = [f for f in VIDEO_ROOT.glob("*.mp4") if f.stem not in current["posted"]]
            ranked = sorted(((score(f.stem), f.stem) for f in files), reverse=True)
            self.json({"item": ranked[0][1] if ranked and ranked[0][0] >= 4 else None,
                       "score": ranked[0][0] if ranked else 0, "minimum_score": 4})
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

