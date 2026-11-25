"""Bouwt een reclamevideo met ingesproken stem: knipt de stem strak (zonder stiltes en haperingen),
legt per zin het juiste beeld eronder en schrijft het projectbestand + ondertitels + stem.wav.

Gebruik: python3 montage/hulp/stem_bouwen.py reclame-006-klimop [reclame-007-hout ...]
Daarna:  python3 montage/monteer.py montage/projecten/<naam>.json

Per blok: (stemstukken, clips, pop). Een stemstuk = stuk(map, opname, "eerste woorden", "laatste woorden").
Een clip met tot=None wordt automatisch zo lang als de stem in dat blok.
Vereist: media/voN/<opname>.wav + .json (zie transcribeer.py) en de beelden in media/rvN/.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "montage/projecten"
SR = 48000
LOS = 0.12          # ruimte voor/na de stem in een blok
TUSSEN = 0.25       # pauze tussen twee blokken
MAXPAUZE = 0.09     # pauze tussen woordgroepen binnen een zin
ZINPAUZE, KOMMAPAUZE = 0.35, 0.12
STAART = 0.3        # extra ruimte na het laatste woord van een zin (zodat de slotklank niet wegvalt)

FIX = {"beukenhag": "beukenhaag", "smalder": "smaller", "snoeizel": "snoeisel", "snoeibord": "snoeibeurt",
       "snoeibuur": "snoeibeurt", "snoeiber": "snoeibeurt", "warm": "Waarom", "oprammen": "opruimen", "snoeik": "snoei ik",
       "niep": "Knip", "fries": "Fris", "klumop": "klimop", "gekleeft": "gekliefd", "spleit": "splijt", "spijt": "splijt",
       "opkuis": "opkuisen", "opkuizen": "opkuisen", "kuizen": "kuisen", "stelt": "steelt", "overhoekert": "overwoekert",
       "overwokkert": "overwoekert", "gehad": "gehaald", "hoogtwerker": "hoogtewerker", "voila": "Voilà",
       "opgekaasd": "opgekuist", "opgekuisd": "opgekuist", "strakken": "struiken", "spart": "spar"}
VERVANG = [("De plaats waar we hem niet te laten vallen", "Plaats om hem te laten vallen"),
           ("duurder optie,", "duurdere optie,"), ("terecht komen.", "terechtkomen."), ("beneden lag heb", "beneden lag, heb"),
           ("ging er zoals", "hingen er, zoals"), ("mijn ten.", "mijn tuin."), ("Bomen struiken of", "Bomen, struiken of"),
           ("Warmste week in", "Warmste Week in"), ("warmste week in", "Warmste Week in")]


def norm(w):
    return re.sub(r"[^\wà-ÿ']", "", w.lower())


def laad(map_, naam):
    return json.loads((ROOT / f"media/{map_}/{naam}.json").read_text(encoding="utf-8"))


def zoek(woorden, zin, na=0):
    doel = [norm(x) for x in zin.split()]
    for i in range(na, len(woorden) - len(doel) + 1):
        if [norm(w["w"]) for w in woorden[i:i + len(doel)]] == doel:
            return i
    raise ValueError(f"niet gevonden: {zin!r}")


def stuk(map_, naam, van, tot, na="", weg=()):
    """Stemstuk vanaf 'van' t.e.m. 'tot' (eerste keer na 'na'); 'weg' = versprekingen die eruit gaan."""
    w = laad(map_, naam)
    i0 = zoek(w, na) + len(na.split()) if na else 0
    a = zoek(w, van, i0)
    b = zoek(w, tot, a) + len(tot.split()) - 1
    ws = w[a:b + 1]
    for z in weg:
        i = zoek(ws, z)
        ws = ws[:i] + ws[i + len(z.split()):]
    return {"wav": ROOT / f"media/{map_}/{naam}.wav", "woorden": ws}


def stuk_voor(st, extra):
    """Woorden met handmatig bepaalde tijden vóór een stemstuk zetten (als de herkenning ze verkeerd plaatste)."""
    st["woorden"] = [{"w": w, "start": a, "eind": b} for w, a, b in extra] + st["woorden"]
    return st


def los_stuk(map_, naam, woorden):
    """Stemstuk met handmatig gecontroleerde woordtijden (voor een take die de herkenning verkeerd plaatste)."""
    return {"wav": ROOT / f"media/{map_}/{naam}.wav", "woorden": [{"w": w, "start": a, "eind": b} for w, a, b in woorden]}


def c(bestand, van, tot=None, snelheid=1):
    d = {"bestand": bestand, "van": van, "tot": tot}
    if snelheid != 1:
        d["snelheid"] = snelheid
    return d


def slag(bestand, t, voor=1.0):
    """Eén kliefslag op normale snelheid: de zwaai en de klap (t = moment van de klap)."""
    return c(bestand, round(t - voor, 2), round(t + 0.35, 2))


def duur_bron(f, cache={}):
    if f not in cache:
        cache[f] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                         str(ROOT / f)], capture_output=True, text=True).stdout)
    return cache[f]


def lees_wav(p, cache={}):
    if p not in cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        cache[p] = np.frombuffer(raw, np.float32)
    return cache[p]


def inkorten(data, max_stil=0.12, drempel=0.08, staart=0.1):
    """Knipt stiltes binnen een stemstuk in (vooraan/achteraan tot 0,1 s). Geeft (data, tijdkaart)."""
    fr = int(0.01 * SR); n = len(data) // fr
    if n == 0:
        return data, lambda x: x
    rms = np.sqrt(np.mean(data[:n * fr].reshape(n, fr) ** 2, axis=1))
    stil = (rms < drempel * np.percentile(rms, 95)) | (rms < 0.005)
    weg, i = [], 0
    while i < n:
        if stil[i]:
            j = i
            while j < n and stil[j]:
                j += 1
            lang = (j - i) * 0.01
            if i == 0 and lang > 0.1:
                weg.append((0.0, lang - 0.1))
            elif j == n and lang > staart:
                weg.append((i * 0.01 + staart, lang - staart))
            elif 0 < i and j < n and lang > max_stil:
                weg.append((i * 0.01 + max_stil / 2, lang - max_stil))
            i = j
        else:
            i += 1
    delen, vorig = [], 0
    for st, ln in weg:
        delen.append(data[vorig:int(st * SR)]); vorig = int((st + ln) * SR)
    delen.append(data[vorig:])

    def kaart(x):
        af = 0.0
        for st, ln in weg:
            af += ln if x >= st + ln else max(0.0, x - st)
        return x - af
    return np.concatenate(delen), kaart


def schoon(w):
    kern = norm(w)
    if kern in FIX:
        nieuw = FIX[kern]
        voor = re.match(r"^\W*", w).group(0); na = re.search(r"[^\w']*$", w).group(0)
        if w.strip("\"'(")[:1].isupper() and nieuw[:1].islower():
            nieuw = nieuw[:1].upper() + nieuw[1:]
        w = voor + nieuw + na
    return w


def nabewerk(ws):
    for oud, nieuw in VERVANG:
        o, n = oud.split(), nieuw.split()
        for i in range(len(ws) - len(o) + 1):
            if [w["w"] for w in ws[i:i + len(o)]] == o:
                t0, t1 = ws[i]["start"], ws[i + len(o) - 1]["eind"]; st = (t1 - t0) / len(n)
                ws = ws[:i] + [{"w": x, "start": round(t0 + k * st, 2), "eind": round(t0 + (k + 1) * st - 0.02, 2)}
                               for k, x in enumerate(n)] + ws[i + len(o):]
                break
    uit = []
    for w in ws:
        if uit and w["w"] == "'n":
            uit[-1] = dict(uit[-1], w=uit[-1]["w"] + "'n", eind=w["eind"]); continue
        uit.append(dict(w))
    for i, w in enumerate(uit):
        if i and uit[i - 1]["w"].endswith((".", "?")) and w["w"][:1].islower():
            w["w"] = w["w"][:1].upper() + w["w"][1:]
    return uit


def bouw(naam, titel, uitvoer, hook, blokken):
    clips, woorden, teksten, t, hookduur = [], [], [], 0.0, None
    stem = np.zeros(int(SR * 180), np.float32)
    for i, (stukken, cl, pop) in enumerate(blokken):
        pos = t + LOS
        pauze = 0.0
        for s in stukken:
            wav = lees_wav(s["wav"])
            delen = []
            ws = s["woorden"]
            for wi, w in enumerate(ws):
                zinseinde = w["w"][-1:] in ".?!"
                a0, b0 = max(0.0, w["start"] - 0.22), w["eind"] + (STAART if zinseinde else 0.1)
                if zinseinde and wi + 1 < len(ws):
                    b0 = min(b0, max(w["eind"] + 0.05, ws[wi + 1]["start"] - 0.24))  # niet in de aanloop van het volgende woord
                if delen and a0 - delen[-1][1] < 0.02 and delen[-1][2][-1]["w"][-1:] not in ".?!":
                    delen[-1][1] = max(delen[-1][1], b0); delen[-1][2].append(w)
                else:
                    delen.append([a0, b0, [w]])
            for j, (a0, b0, dw) in enumerate(delen):
                einde = dw[-1]["w"][-1:] in ".?!"
                data, k0 = inkorten(wav[int(a0 * SR):int(b0 * SR)].copy(), staart=STAART if einde else 0.1)
                f = int(0.012 * SR); data[:f] *= np.linspace(0, 1, f); data[-f:] *= np.linspace(1, 0, f)
                k = int(pos * SR); stem[k:k + len(data)] += data
                for w in dw:
                    woorden.append({"w": schoon(w["w"]), "start": round(pos + k0(w["start"] - a0), 2),
                                    "eind": round(pos + k0(w["eind"] - a0), 2)})
                eind = dw[-1]["w"][-1:]
                pauze = ZINPAUZE if eind in ".?!" else KOMMAPAUZE if eind in ",:" else MAXPAUZE
                if j + 1 < len(delen) and not einde:
                    pauze = min(pauze, max(delen[j + 1][0] - b0, 0.0) + MAXPAUZE)
                pos += len(data) / SR + pauze
            pos += TUSSEN - pauze
        nodig = pos - TUSSEN + LOS - t
        vast = sum((x["tot"] - x["van"]) / x.get("snelheid", 1) for x in cl if x["tot"] is not None)
        for x in cl:
            if x["tot"] is None:
                sn = x.get("snelheid", 1)
                x["tot"] = round(min(duur_bron(x["bestand"]) - 0.05, x["van"] + max(nodig - vast, 0.5) * sn), 2)
        duur = sum((x["tot"] - x["van"]) / x.get("snelheid", 1) for x in cl)
        if duur < nodig - 0.05:
            x = cl[-1]; deel = (x["tot"] - x["van"]) / x.get("snelheid", 1)
            x["snelheid"] = round((x["tot"] - x["van"]) / (deel + nodig - duur + 0.05), 3)
            duur = sum((y["tot"] - y["van"]) / y.get("snelheid", 1) for y in cl)
            print(f"  ~ {naam} blok {i}: te weinig beeld, laatste clip vertraagd tot x{x['snelheid']}")
        elif duur > nodig + 0.5:
            print(f"  ! {naam} blok {i}: {duur - nodig:.1f} s meer beeld dan stem (stilte)")
        if i == 0:
            hookduur = round(duur - 0.05, 2)
        if pop:
            teksten.append({"tekst": pop, "van": round(t + 0.1, 2), "tot": round(t + duur - 0.15, 2), "stijl": "pop"})
        clips += cl
        t += duur
    woorden = nabewerk(woorden)
    wav = ROOT / f"media/vo{naam[10]}/stem.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(wav)],
                   input=np.clip(stem[:int(t * SR)], -1, 1).astype(np.float32).tobytes(), check=True)
    (P / f"{naam}.woorden.json").write_text(json.dumps(woorden, ensure_ascii=False, indent=1), encoding="utf-8")
    (P / f"{naam}.json").write_text(json.dumps({
        "titel": titel, "uitvoer": uitvoer, "overgang": 0.2, "geluid": True, "stem": str(wav.relative_to(ROOT)),
        "clips": clips, "broll": [], "ondertitels": f"montage/projecten/{naam}.woorden.json",
        "hook": {"tekst": hook, "tot": hookduur}, "teksten": teksten, "eindbeeld": True}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"{naam}: {t:.1f} s + 4 s eindbeeld = {t + 4:.1f} s")
    print("   ", " ".join(w["w"] for w in woorden))


R3, R4, R5, R6, R7 = (f"media/rv{n}/" for n in (3, 4, 5, 6, 7))


def videos():
    N5, N6, N7 = ("vo5", "IMG_3070"), ("vo6", "IMG_3071"), ("vo7", "IMG_3072")
    return {
     "reclame-005-palmbomen": lambda: ("Reclamevideo 5 · Vandaag: palmbomen", "output/reclame-005.mp4", "Vandaag: | palmbomen", [
       ([stuk(*N5, "Vandaag heb ik", "snoeiber nodig.")], [c(R5+"20261116_143134.mp4", 0.0)], None),
       ([stuk(*N5, "Toen ik begon,", "bladeren aan.")], [c(R5+"20261116_130245.mp4", 0.0, 2.6), c(R5+"20261116_133446.mp4", 0.0)], "Voor"),
       ([los_stuk(*N5, [  # laatste (betere) take, tijden gecontroleerd op het geluid
           ("Het", 42.44, 42.62), ("zijn", 42.62, 42.92), ("Chinese", 42.92, 43.26), ("waaierpalmen.", 43.26, 44.04),
           ("Die", 44.26, 44.42), ("kunnen", 44.42, 44.66), ("tegen", 44.66, 44.9), ("de", 44.9, 45.08), ("vorst", 45.08, 45.34),
           ("en", 45.34, 45.5), ("blijven", 45.5, 45.72), ("ook", 45.72, 45.92), ("in", 45.92, 46.02), ("de", 46.02, 46.14),
           ("winter", 46.14, 46.4), ("groen.", 46.4, 46.58),
           ("Daarom", 57.18, 57.6), ("zie", 57.6, 57.72), ("je", 57.72, 57.84), ("ze", 57.84, 58.0), ("zoveel", 58.0, 58.38),
           ("in", 58.38, 58.48), ("Belgische", 58.48, 58.9), ("tuinen.", 58.9, 59.22)])], [c(R5+"20261116_135117.mp4", 0.0)], None),
       ([stuk(*N5, "Ik heb de", "groene kop.")], [c(R5+"20261116_134218.mp4", 1.0, 2.8), c(R5+"20261116_130245.mp4", 3.0, None, 45)], None),
       ([stuk(*N5, "Daarna heb ik", "het containerpark.")],
        [c(R5+"20261116_130834.mp4", 0.0, 1.0), c(R5+"20261116_144216.mp4", 0.0, 3.5, 2.5), c(R5+"20261116_144243.mp4", 0.0)], None),
       ([stuk(*N5, "Voilà, dit is", "het eindresultaat.")], [c(R5+"20261116_130827.mp4", 0.0, 0.9), c(R5+"20261116_144228.mp4", 0.0)], "Na"),
       ([stuk(*N5, "Palmbomen of andere", "ons vragen.")], [c(R5+"20261116_144236.mp4", 0.0, 2.0), c(R5+"foto_20261116_130844.mp4", 0)],
        "Vraag het ons"),
     ]),
     "reclame-006-klimop": lambda: ("Reclamevideo 6 · Vandaag: klimop", "output/reclame-006.mp4", "Vandaag: | klimop weg", [
       ([stuk(*N6, "Vandaag heb ik", "boom getrokken.")], [c(R6+"20261117_113427.mp4", 0.3)], None),
       ([stuk(*N6, "Zoals je ziet", "helemaal ingepakt.")], [c(R6+"20261117_113436.mp4", 0.5)], "Voor"),
       ([stuk(*N6, "Klimop maakt de", "eronder zit.")], [c(R6+"20261117_113746.mp4", 0.0)], None),
       ([stuk(*N6, "En als het", "licht meer.")], [c(R6+"20261117_113427.mp4", 4.5, 7.7), c(R6+"20261117_121004.mp4", 0.0)], None),
       ([stuk(*N6, "Ik heb de", "de boom.")], [c(R6+"20261117_113746.mp4", 8.0, None, 12)], None),
       ([stuk(*N6, "Het was vandaag", "gewoon door.", na="blijft gewoon doorgaan.")],
        [c(R6+"20261117_121033.mp4", 0.0, 1.95), c(R6+"20261117_121001.mp4", 0.0)], None),
       ([stuk(*N6, "Daarna heb ik", "blijft liggen.")], [c(R6+"20261117_123516.mp4", 0.5, None, 8)], None),
       ([stuk(*N6, "Voila, de stammen", "helemaal vrij.")], [c(R6+"20261117_123221.mp4", 0.0)], "Na"),
       ([stuk(*N6, "Bomen strakken of", "ons vragen.")], [c(R6+"20261117_121125.mp4", 0.0)], "Vraag het ons"),
     ]),
     "reclame-007-hout": lambda: ("Reclamevideo 7 · Vandaag: brandhout klieven", "output/reclame-007.mp4", "Brandhout | voor het goede doel", [
       ([stuk(*N7, "Vandaag heb ik", "goede doel.")], [c(R7+"20261118_152311.mp4", 20.0)], None),
       ([stuk(*N7, "Het hout komt", "beneden haalde.")], [c(R4+"IMG_1252_traag2.mp4", 0.0)], None),
       ([stuk(*N7, "Zoals je ziet", "veel hout.")], [c(R4+"20261116_105638.mp4", 17.0)], "Voor"),
       ([stuk(*N7, "Alle stammen en", "mijn ten.")], [c(R4+"20261116_105707.mp4", 0.0)], None),
       ([stuk(*N7, "Hier zie je", "zonder machine.")],
        [slag(R7+"20261118_153931.mp4", 12.13), slag(R7+"20261118_153310.mp4", 13.02), slag(R4+"20261118_162624.mp4", 124.14), slag(R7+"20261118_153931.mp4", 24.33)], None),
       ([stuk(*N7, "Rond het houtblok", "het makkelijkst.")],
        [slag(R7+"20261118_152601.mp4", 55.08, 1.0), slag(R7+"20261118_153310.mp4", 38.01, 1.0), slag(R4+"20261118_162624.mp4", 240.35, 1.0),
         slag(R7+"20261118_153931.mp4", 31.06, 1.0), slag(R7+"20261118_152601.mp4", 164.12, 1.0), slag(R7+"20261118_153310.mp4", 46.8, 1.0), slag(R4+"20261118_162624.mp4", 172.31, 1.0)], None),
       ([stuk(*N7, "Ik klief het", "het opbrandt.")], [c(R7+"20261118_152601.mp4", 2.0, 348.0, 60), c(R7+"20261120_130304.mp4", 0.0, None, 40)], None),
       ([stuk(*N7, "Daarna heb ik", "kan drogen.")], [c(R7+"20261118_162150.mp4", 0.0, 3.0), c(R7+"20261120_123817.mp4", 0.0)], "Na"),
       ([stuk(*N7, "Mijn plan is", "in 2027.")],
        [c(R7+"20261118_162141.mp4", 0.0, 1.8), c(R7+"20261118_162134.mp4", 0.0, 2.2), c(R7+"foto_20261118_160011.mp4", 0)], None),
       ([stuk(*N7, "Heb je een", "goede doel.", na="in 2027.")], [c(R4+"20261118_162624.mp4", 356.0)], "Stuur een bericht"),
     ]),
    }



if __name__ == "__main__":
    alle = videos()
    for naam in sys.argv[1:] or list(alle):
        try:
            spec = alle[naam]()
        except (FileNotFoundError, ValueError) as e:
            if sys.argv[1:]:
                raise
            print(f"  ! {naam} overgeslagen (opname of tekst ontbreekt): {e}")
            continue
        bouw(naam, *spec)
