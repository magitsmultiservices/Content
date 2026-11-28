"""Bouwt een ondernemingsvideo uit praat-takes (één take per zin of blok, in volgorde).
Gebruik: python3 montage/hulp/afl_bouwen.py <projectnaam>   (specificatie: AFL[<projectnaam>] hieronder)
Elke take: (naam, van, tot) in seconden in de take; woorden komen uit media/<map>/<naam>.json (transcribeer eerst)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def bouw(naam, titel, map_, takes, hook, pops, broll=(), handmatig={}, vervang={}, overgang=0):
    clips, uit, t, pos = [], [], 0.0, {}
    for i, (n, a, b) in enumerate(takes):
        c = {"bestand": f"media/{map_}/IMG_{n}.mp4", "van": a, "tot": b}
        if i % 2: c["zoom"] = 1.12
        clips.append(c); pos[n] = t
        if n in handmatig:
            ws = [{"w": w, "start": s, "eind": e} for w, s, e in handmatig[n]]
        else:
            ws = json.loads((ROOT / f"media/{map_}/IMG_{n}.json").read_text(encoding="utf-8"))
        eigen = []
        for w in ws:
            if not (w["start"] < b and w["eind"] > a + 0.05):
                print("  ! woord buiten knip:", n, w); continue
            x = {"w": w["w"], "start": round(t + max(w["start"], a) - a, 2), "eind": round(t + min(w["eind"], b) - a, 2)}
            if eigen and (x["w"].startswith("-") or x["w"].startswith(("%", ".000"))):
                eigen[-1]["w"] += x["w"]; eigen[-1]["eind"] = x["eind"]; continue
            eigen.append(x)
        uit += eigen; t += b - a
    for w in uit:
        w["w"] = vervang.get(w["w"], w["w"]).replace("BTW", "btw").replace("PDF", "pdf").replace("B2-", "btw-")

    def zoek(n, woord):
        return next(w for w in uit if w["start"] >= pos[n] - 0.01 and woord in w["w"])
    teksten = []
    for tekst, n, woord, duur in pops:
        w = zoek(n, woord); teksten.append({"tekst": tekst, "van": w["start"], "tot": round(w["start"] + duur, 2), "stijl": "pop"})
    brl = []
    for bestand, van, n, woord, verschuif, duur in broll:
        w = zoek(n, woord); brl.append({"bestand": bestand, "van": van, "op": round(w["start"] + verschuif, 2), "duur": duur})
    P = ROOT / "montage/projecten"
    (P / f"{naam}.woorden.json").write_text(json.dumps(uit, ensure_ascii=False, indent=1), encoding="utf-8")
    (P / f"{naam}.json").write_text(json.dumps({
        "titel": titel, "uitvoer": f"output/{naam}.mp4", "overgang": overgang, "clips": clips, "broll": brl,
        "ondertitels": f"montage/projecten/{naam}.woorden.json", "hook": {"tekst": hook, "tot": round(pos[takes[1][0]] - 0.05, 2)},
        "teksten": teksten, "eindbeeld": True}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{naam}: {t:.1f} s + 4 s eindbeeld")
    print("   ", " ".join(w["w"] for w in uit))

AFL = {
 "007-accountable-en-peppol": lambda: bouw(
    "007-accountable-en-peppol", "Ondernemingsvideo 7 · Aflevering 7", "a007",
    [("3131", 0.45, 2.8), ("3132", 0.75, 4.4), ("3135", 0.6, 4.65), ("3136", 1.0, 2.65), ("3138", 0.8, 5.7),
     ("3139", 0.0, 1.62), ("3142", 0.0, 3.55), ("3146", 1.25, 10.4), ("3152", 0.55, 6.95), ("3153", 1.0, 5.3),
     ("3154", 0.0, 2.1), ("3156", 1.4, 4.7)],
    "Facturen | en Peppol?",
    [("Peppol", "3138", "Peppol", 2.2), ("1 klik", "3152", "klik", 2.0), ("Accountable", "3154", "Accountable", 1.8)],
    handmatig={"3136": [("Vandaag", 1.14, 1.46), ("toon", 1.46, 1.70), ("ik", 1.70, 1.78), ("hoe", 1.78, 1.86),
                        ("ik", 1.86, 1.94), ("dat", 1.94, 2.12), ("doe.", 2.12, 2.4)]},
    vervang={"Yatte,": "Yelte,", "versturen": "verstuurd"}),
 "008-btw-aangifte-invullen": lambda: bouw(
    "008-btw-aangifte-invullen", "Ondernemingsvideo 8 · Aflevering 8", "a008",
    [("3157", 0.77, 2.78), ("3158", 0.25, 4.0), ("3160", 0.62, 4.81), ("3163", 1.36, 6.37), ("3166", 3.44, 6.84),
     ("3169", 0.41, 10.47), ("3172", 0.3, 3.65), ("3174", 0.63, 5.62), ("3175", 1.32, 4.8), ("3176", 1.1, 3.93),
     ("3177", 0.4, 3.73), ("3181", 1.96, 6.85), ("3182", 0.4, 2.65), ("3184", 2.58, 6.93)],
    "Btw-aangifte | zo doe ik het",
    [("Per kwartaal", "3160", "kwartaal", 2.0), ("25 januari", "3166", "25", 1.6), ("Intervat", "3172", "Intervat", 1.8)],
    vervang={"Jelte.": "Yelte.", "film": "dien", "B2": "btw", "25e": "25ste", "wil": "vul"}),

}
if __name__ == "__main__":
    for n in sys.argv[1:]:
        AFL[n]()
