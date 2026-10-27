#!/usr/bin/env python3
"""Monteert een verticale video (9:16) in de huisstijl van Magits Multiservices.

Gebruik:
    python3 montage/monteer.py montage/projecten/001-voorstelling.json

Het projectbestand (JSON) beschrijft:
    clips        lijst van {"bestand", "van", "tot"}: de takes, in volgorde (bepalen de tijdlijn)
    broll        optioneel, lijst van {"bestand", "van", "op", "duur"}: beelden over de tijdlijn heen
                 (het geluid van de clips blijft lopen)
    ondertitels  "auto" (spraakherkenning), een pad naar een woordenbestand (JSON), of weggelaten
    teksten      optioneel, lijst van {"tekst", "van", "tot"}: tekst bovenaan in beeld
    eindbeeld    true/false: logo, slogan en handle op het einde (standaard true)
    uitvoer      pad van het eindbestand

Een woordenbestand is een lijst van {"w": "woord", "start": s, "eind": s} in tijdlijntijd.
Paden zijn relatief tegenover de root van deze repository.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUISSTIJL = ROOT / "huisstijl"
FONTS = HUISSTIJL / "fonts"
LOGO = HUISSTIJL / "logo-wit.png"

B, H, FPS = 1080, 1920, 30

# Huisstijlkleuren (zie huisstijl/huisstijl.md). ASS gebruikt &HAABBGGRR.
LIMOEN = "8CD742"
DONKER = "0F1A14"


def ass_kleur(hexkleur, alpha="00"):
    r, g, b = hexkleur[0:2], hexkleur[2:4], hexkleur[4:6]
    return f"&H{alpha}{b}{g}{r}".upper()


WIT = "&H00FFFFFF"
SLOGAN = "VAKKUNDIG · NETJES · BETROUWBAAR"
HANDLE = "Volg @Magitsmultiservices"
WEBSITE = "magitsmultiservices.be"
TELEFOON = "+32 492 88 44 24"
# Helpt de spraakherkenning om namen en vaktermen juist te schrijven.
WOORDENSCHAT = ("Ik ben Yelte van Magits Multiservices: tuinonderhoud en rommelophaling "
                "in Antwerpen, Mechelen en omstreken.")

ASS_KOP = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {B}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Onder,Montserrat ExtraBold,82,{WIT},{WIT},{ass_kleur(DONKER)},{ass_kleur(DONKER, "80")},0,0,0,0,100,100,1,0,1,7,3,2,90,90,560,1
Style: Titel,Montserrat Bold,62,{WIT},{WIT},&H00000000,&H66000000,0,0,0,0,100,100,3,0,1,3,5,8,90,90,250,1
Style: Hook,Montserrat Bold,80,{WIT},{WIT},&H00000000,&H66000000,0,0,0,0,100,100,3,0,1,4,6,8,80,80,250,1
Style: Groot,Montserrat Black,200,{WIT},{WIT},&H00000000,&H66000000,0,0,0,0,100,100,2,0,1,9,7,8,60,60,230,1
Style: Slogan,Montserrat Bold,44,{WIT},{WIT},{ass_kleur(DONKER)},{ass_kleur(DONKER)},0,0,0,0,100,100,2,0,1,0,0,5,60,60,0,1
Style: Info,Montserrat Bold,54,{WIT},{WIT},{ass_kleur(DONKER)},{ass_kleur(DONKER)},0,0,0,0,100,100,1,0,1,0,0,5,60,60,0,1
Style: Handle,Montserrat ExtraBold,58,{ass_kleur(LIMOEN)},{WIT},{ass_kleur(DONKER)},{ass_kleur(DONKER)},0,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Emoji's kan libass niet in kleur tonen: weglaten in tekst op het scherm.
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Fout bij: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def heeft_geluid(bestand):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
               "stream=index", "-of", "csv=p=0", str(bestand)])
    return bool(out.strip())


def tijd(t):
    t = max(t, 0)
    h, rest = divmod(t, 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_tekst(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")")


VULLEN = (f"scale={B}:{H}:force_original_aspect_ratio=increase,crop={B}:{H},"
          f"setsar=1,fps={FPS},format=yuv420p")
VIDEO_OPTS = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", str(FPS)]
AUDIO_OPTS = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def segment(clip, doel):
    """Knipt één take en zet hem om naar 1080x1920, 30 fps, stereo 48 kHz."""
    bron = ROOT / clip["bestand"]
    van, tot = clip.get("van", 0), clip["tot"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(van), "-to", str(tot), "-i", str(bron)]
    if heeft_geluid(bron):
        cmd += ["-map", "0:v:0", "-map", "0:a:0", "-af", "aresample=48000"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    run(cmd + ["-vf", VULLEN, *VIDEO_OPTS, *AUDIO_OPTS, str(doel)])
    return tot - van


def eindbeeld(doel, werk, duur=4.0):
    """Zwart eindbeeld met logo, slogan, website, telefoon en handle."""
    ass = werk / "eind.ass"
    ass.write_text(ASS_KOP
                   + f"Dialogue: 0,{tijd(0.4)},{tijd(duur)},Slogan,,0,0,0,,{{\\pos(540,1230)\\fad(300,0)}}{SLOGAN}\n"
                   + f"Dialogue: 0,{tijd(0.8)},{tijd(duur)},Info,,0,0,0,,{{\\pos(540,1390)\\fad(300,0)}}{WEBSITE}\n"
                   + f"Dialogue: 0,{tijd(0.8)},{tijd(duur)},Info,,0,0,0,,{{\\pos(540,1480)\\fad(300,0)}}{TELEFOON}\n"
                   + f"Dialogue: 0,{tijd(1.2)},{tijd(duur)},Handle,,0,0,0,,{{\\pos(540,1620)\\fad(300,0)}}{HANDLE}\n",
                   encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", f"color=c=black:s={B}x{H}:r={FPS}:d={duur}",
         "-loop", "1", "-i", str(LOGO),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex",
         f"[1:v]scale=620:-1,format=rgba,fade=in:st=0:d=0.4:alpha=1[l];"
         f"[0:v][l]overlay=(W-w)/2:420:shortest=1,"
         f"ass={ass}:fontsdir={FONTS},format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", "-t", str(duur), *VIDEO_OPTS, *AUDIO_OPTS, str(doel)])
    return duur


def transcriberen(clips, model="small"):
    """Woorden met tijden via faster-whisper, omgezet naar tijdlijntijd."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Spraakherkenning ontbreekt: pip install faster-whisper (en zorg dat het model "
                 "gedownload kan worden), of geef een woordenbestand op bij 'ondertitels'.")
    import numpy as np
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    woorden, offset = [], 0.0
    for clip in clips:
        van, tot = clip.get("van", 0), clip["tot"]
        # ffmpeg haalt het geluid van het geknipte stuk op (16 kHz mono), zodat de tijden
        # meteen relatief zijn tegenover het begin van de take.
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(van), "-to", str(tot),
                              "-i", str(ROOT / clip["bestand"]), "-vn", "-ac", "1", "-ar", "16000",
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        segs, _ = wm.transcribe(np.frombuffer(pcm, np.float32), language="nl", word_timestamps=True,
                                vad_filter=True, initial_prompt=WOORDENSCHAT)
        for s in segs:
            for w in s.words:
                woorden.append({"w": w.word.strip(), "start": offset + w.start,
                                "eind": offset + min(w.end, tot - van)})
        offset += tot - van
    return woorden


def groepeer(woorden, max_woorden=3, max_tekens=18, max_pauze=0.6):
    """Korte ondertitelregels: hoogstens 3 woorden, splitsen op leestekens en pauzes."""
    groepen, huidig = [], []
    for w in woorden:
        if huidig:
            vorig = huidig[-1]
            lengte = sum(len(x["w"]) + 1 for x in huidig) + len(w["w"])
            if (len(huidig) >= max_woorden or lengte > max_tekens
                    or re.search(r"[.,!?…:;]$", vorig["w"]) or w["start"] - vorig["eind"] > max_pauze):
                groepen.append(huidig)
                huidig = []
        huidig.append(w)
    if huidig:
        groepen.append(huidig)
    return groepen


def ondertitel_regels(woorden):
    """Eén regel per woord: de hele groep in beeld, het gesproken woord in limoengroen."""
    events = []
    for groep in groepeer(woorden):
        for i, w in enumerate(groep):
            eind = groep[i + 1]["start"] if i + 1 < len(groep) else w["eind"] + 0.15
            delen = []
            for j, x in enumerate(groep):
                woord = ass_tekst(x["w"]).upper()
                if j == i:
                    woord = f"{{\\c{ass_kleur(LIMOEN)}\\fscx108\\fscy108}}{woord}{{\\c{WIT}\\fscx100\\fscy100}}"
                delen.append(woord)
            events.append([w["start"], eind, " ".join(delen)])
    # Nooit twee regels tegelijk in beeld: elke regel stopt waar de volgende begint.
    for huidig, volgend in zip(events, events[1:]):
        huidig[1] = min(huidig[1], volgend[0])
    return [f"Dialogue: 1,{tijd(s)},{tijd(e)},Onder,,0,0,0,,{t}" for s, e, t in events if e > s]


STIJLEN = {"titel": "Titel", "hook": "Hook", "groot": "Groot"}
# Groot getal: komt klein op, schiet iets te groot door en zakt terug (pop).
POP = "{\\fad(60,150)\\fscx40\\fscy40\\t(0,170,\\fscx112\\fscy112)\\t(170,290,\\fscx100\\fscy100)}"


def beeldstukken(clips, broll, lengte):
    """Deelt de tijdlijn op in opeenvolgende stukken beeld: (bestand, bronstart, tijdlijnstart, duur).

    Waar b-roll ligt, komt het beeld uit de b-roll; elders uit de take. Zo kan elke overgang
    een vloeiende overgang krijgen en flitst er nooit een beeldje van de take tussen.
    """
    rond = lambda x: round(x * FPS) / FPS
    takes, t = [], 0.0
    for c in clips:
        duur = c["tot"] - c.get("van", 0)
        takes.append((rond(t), rond(t + duur), ROOT / c["bestand"], c.get("van", 0)))
        t += duur
    lengte = rond(lengte)
    grenzen = {0.0, lengte} | {a for a, _, _, _ in takes}
    for br in broll:
        grenzen |= {rond(br["op"]), min(rond(br["op"] + br["duur"]), lengte)}
    grenzen = sorted(g for g in grenzen if 0 <= g <= lengte)
    stukken = []
    for a, b in zip(grenzen, grenzen[1:]):
        if b - a <= 0:
            continue
        br = next((x for x in broll if rond(x["op"]) <= a < rond(x["op"] + x["duur"])), None)
        if br:
            bron = (ROOT / br["bestand"], br.get("van", 0) + a - rond(br["op"]))
        else:
            ta, _, bestand, van = next(x for x in takes if x[0] <= a < x[1])
            bron = (bestand, van + a - ta)
        vorig = stukken[-1] if stukken else None
        if vorig and vorig[0] == bron[0] and abs(vorig[1] + vorig[3] - bron[1]) < 1e-3:
            stukken[-1] = (vorig[0], vorig[1], vorig[2], vorig[3] + b - a)
        else:
            stukken.append((bron[0], bron[1], a, b - a))
    return stukken


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    project = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    uitvoer = ROOT / project.get("uitvoer", "output/video.mp4")
    uitvoer.parent.mkdir(parents=True, exist_ok=True)

    werk = Path(tempfile.mkdtemp(prefix="montage-"))
    try:
        print("1/4 Takes knippen en omzetten…")
        segmenten, lengte = [], 0.0
        for i, clip in enumerate(project["clips"]):
            doel = werk / f"seg{i:03d}.mp4"
            lengte += segment(clip, doel)
            segmenten.append(doel)

        print("2/4 Ondertitels…")
        bron = project.get("ondertitels")
        if bron == "auto":
            woorden = transcriberen(project["clips"], project.get("model", "small"))
            (uitvoer.with_suffix(".woorden.json")).write_text(
                json.dumps(woorden, ensure_ascii=False, indent=1), encoding="utf-8")
        elif bron:
            woorden = json.loads((ROOT / bron).read_text(encoding="utf-8"))
        else:
            woorden = []
        regels = ondertitel_regels(woorden)
        for t in project.get("teksten", []):
            tekst = ass_tekst(EMOJI.sub("", t["tekst"]).strip())
            stijl = STIJLEN[t.get("stijl", "titel")]
            effect = POP if stijl == "Groot" else "{\\fad(150,150)}"
            regels.append(f"Dialogue: 2,{tijd(t['van'])},{tijd(t['tot'])},{stijl},,0,0,0,,{effect}{tekst}")
        ass = werk / "ondertitels.ass"
        ass.write_text(ASS_KOP + "\n".join(regels) + "\n", encoding="utf-8")

        print("3/4 Monteren…")
        lijst = werk / "lijst.txt"
        lijst.write_text("".join(f"file '{s}'\n" for s in segmenten), encoding="utf-8")
        romp = werk / "romp.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lijst),
             "-c", "copy", str(romp)])

        invoer, filters = ["-i", str(romp)], []
        stukken = beeldstukken(project["clips"], project.get("broll", []), lengte)
        overgang = min(project.get("overgang", 0.25), *(st[3] for st in stukken))
        totaal = 0.0
        for k, (bestand, bron_van, _, duur) in enumerate(stukken, start=1):
            # Elk stuk (behalve het eerste) begint 'overgang' vroeger: dat deel loopt over in het vorige.
            extra = overgang if k > 1 else 0.0
            start = max(bron_van - extra, 0.0)
            beelden = round((duur + extra) * FPS)
            invoer += ["-ss", f"{start:.3f}", "-t", f"{duur + extra + 1:.3f}", "-i", str(bestand)]
            filters.append(f"[{k}:v]{VULLEN},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2,"
                           f"trim=end_frame={beelden},setpts=PTS-STARTPTS,settb=1/{FPS}[s{k}]")
            if k == 1:
                laatste = "s1"
            else:
                filters.append(f"[{laatste}][s{k}]xfade=transition=fade:duration={overgang}:"
                               f"offset={totaal - overgang:.4f}[x{k}]")
                laatste = f"x{k}"
            totaal += duur
        filters.append(f"[{laatste}]ass={ass}:fontsdir={FONTS},format=yuv420p[v]")
        hoofd = werk / "hoofd.mp4"
        run(["ffmpeg", "-y", "-v", "error", *invoer, "-filter_complex", ";".join(filters),
             "-map", "[v]", "-map", "0:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             *VIDEO_OPTS, *AUDIO_OPTS, str(hoofd)])

        print("4/4 Eindbeeld en export…")
        delen = [hoofd]
        if project.get("eindbeeld", True):
            delen.append(werk / "eind.mp4")
            lengte += eindbeeld(delen[-1], werk)
        lijst.write_text("".join(f"file '{d}'\n" for d in delen), encoding="utf-8")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lijst),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             *AUDIO_OPTS, "-movflags", "+faststart", str(uitvoer)])
        print(f"Klaar: {uitvoer.relative_to(ROOT)} ({lengte:.1f} s)")
    finally:
        shutil.rmtree(werk, ignore_errors=True)


if __name__ == "__main__":
    main()
