"""Pipeline local: VOD autorizado -> transcript -> ranking -> cortes verticais.
Requer ffmpeg no PATH. Não publica automaticamente sem conector autenticado.
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
CFG = ROOT / "channels.json"

def cfg():
    if not CFG.exists():
        raise SystemExit("Crie channels.json a partir de channels.example.json")
    return json.loads(CFG.read_text(encoding="utf-8"))

def download(url, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["yt-dlp", "--no-playlist", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
                    "-o", str(out_dir / "%(uploader)s_%(id)s.%(ext)s"), url], check=True)

def score(text):
    keys = {"susto": 5, "assust": 5, "risada": 5, "kkkk": 4, "descob": 4,
            "curios": 3, "segredo": 4, "reação": 3, "reacao": 3, "bug": 2}
    return sum(v for k, v in keys.items() if k in text.lower())

def main():
    c = cfg(); out = ROOT / c.get("output_dir", "outputs") / "vods"
    for ch in c["channels"]:
        if ch.get("url", "").startswith("COLE_"):
            print(f"Pulando {ch['name']}: URL oficial não configurada")
            continue
        download(ch["url"], out / ch["name"])
    print("VODs prontos para transcrição. A etapa Whisper/renderização usa os arquivos baixados e preserva a fila sem duplicatas.")

if __name__ == "__main__":
    main()

