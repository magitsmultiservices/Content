"""Transcribeert alle stemopnames in media/vo*/ (woorden met tijden) naar <naam>.json ernaast.
Gebruik: python3 montage/hulp/transcribeer.py [model]   (standaard: medium)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[2]
m = WhisperModel(sys.argv[1] if len(sys.argv) > 1 else "medium", device="cpu", compute_type="int8")
for wav in sorted(p for p in (ROOT / "media").glob("vo*/*.wav") if p.stem != "stem"):
    uit = wav.with_suffix(".json")
    if uit.exists():
        continue
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="nl", word_timestamps=True, vad_filter=True,
                           initial_prompt="Vandaag heb ik. Magits Multiservices. Ook dat kan u aan ons vragen.")
    woorden = [{"w": w.word.strip(), "start": round(w.start, 2), "eind": round(w.end, 2)} for s in segs for w in s.words]
    uit.write_text(json.dumps(woorden, ensure_ascii=False, indent=0), encoding="utf-8")
    print(wav.parent.name, wav.stem, " ".join(w["w"] for w in woorden), flush=True)
