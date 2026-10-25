# Montage

`monteer.py` maakt van losse takes een afgewerkte verticale video in de Magits-huisstijl:
knippen, b-roll, ondertitels woord per woord, tekst in beeld, eindbeeld en genormaliseerd geluid.

## Gebruik
```
python3 montage/monteer.py montage/projecten/<project>.json
```
Nodig: `ffmpeg`. Voor automatische ondertitels ook `pip install faster-whisper`.
Het spraakmodel (`small`, ± 500 MB) wordt bij het eerste gebruik gedownload van huggingface.co;
die domeinen (`huggingface.co`, `*.huggingface.co`, `*.hf.co`) staan toegelaten in de
netwerkinstellingen van de cloudomgeving.

Controleer het transcript altijd: namen en woorden kunnen verkeerd verstaan worden.
Verbeter ze in `output/<video>.woorden.json`, zet `ondertitels` op dat bestand en render opnieuw.

## Projectbestand
Zie `projecten/proef.json` voor een volledig voorbeeld.

| Veld | Betekenis |
|---|---|
| `clips` | takes in volgorde: `bestand`, `van`, `tot` (seconden in het bronbestand) |
| `broll` | beelden over de tijdlijn: `bestand`, `van` (in bron), `op` (op tijdlijn), `duur` |
| `ondertitels` | `"auto"` of pad naar een woordenbestand `[{"w","start","eind"}]` |
| `teksten` | tekst bovenaan: `tekst`, `van`, `tot` (op tijdlijn) |
| `eindbeeld` | `true` (standaard) of `false` |
| `uitvoer` | pad van het eindbestand, bv. `output/001-voorstelling.mp4` |

Bij `"auto"` wordt het transcript ook bewaard naast de video (`.woorden.json`), zodat
foute woorden met de hand verbeterd kunnen worden en daarna opnieuw gerenderd.
