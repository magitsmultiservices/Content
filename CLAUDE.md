# Content Magits Multiservices

Deze repository bevat scripts en ideeën voor video's op sociale media. Claude leest dit bestand bij elke sessie.

## Het bedrijf
- **Naam:** Magits Multiservices
- **Oprichter:** Yelte Magits
- **Diensten:** tuinonderhoud, rommelophaling en klusjes
- **Regio:** Antwerpen, Mechelen en omstreken
- **Website:** magitsmultiservices.be
- **Handle:** Magitsmultiservices (Instagram, Facebook, TikTok, YouTube)
- **Slogan:** Vakkundig · Netjes · Betrouwbaar
- **Boodschap:** tuin, rommel en klusjes in één keer geregeld
- Het bedrijf is nieuw. Doel nummer één: nieuwe klanten bereiken.

## Twee soorten video's
1. **Klanten** (`scripts/klanten/`): voor mensen in de regio die hulp zoeken.
   Bv. voor/na-beelden, tips, een dag op de werf. Spreek kijkers aan met "u".
2. **Ondernemen** (`scripts/ondernemen/`): voor een breed publiek, vooral jonge mensen
   die zelf een zaak willen starten. Yelte toont hoe hij werkt, met de ups én de downs.
   Natuurlijke spreektaal, "je" mag hier.

## Schrijfregels
- Altijd Nederlands (Vlaams), in natuurlijke spreektaal: korte zinnen, zoals je praat.
- Toon: professioneel, eerlijk en duidelijk. Geen overdreven verkooptaal.
- Weinig emoji's (enkele) en 3 tot 5 hashtags per post.
- **Verzin geen feiten.** Prijzen, telefoonnummers, data, cijfers en persoonlijke verhalen
  die je niet kent, krijgen een invulplek: `[prijs]`, `[telefoonnummer]`, `[waarom gestart]`.
- Geen gespeelde emotie of verzonnen tegenslagen. Toon alleen wat echt gebeurd is.
- Geen klantgegevens of herkenbare klanten zonder toestemming.

## Opbouw van een script
Gebruik de sjablonen in `sjablonen/`. Elk script bevat:
- een hook (eerste 1 tot 3 seconden) met 2 à 3 alternatieven,
- de tekst per blok, met regieaanwijzingen (beeld, tekst op scherm),
- een call-to-action,
- een caption en hashtags per platform.

## Bestandsnamen
`scripts/<soort>/<nummer>-<onderwerp>.md`, bv. `scripts/ondernemen/001-voorstelling.md`.
Nieuwe ideeën gaan in `ideeen.md`.

## Montage
- Huisstijl voor video: `huisstijl/huisstijl.md` (Montserrat, bosgroen `#154727`, limoen `#8CD742`).
- Montage gebeurt met `montage/monteer.py` (ffmpeg) op basis van een projectbestand in
  `montage/projecten/`. Zie `montage/README.md`.
- Ruwe beelden staan in `media/<nummer>/`, eindbestanden in `output/`. Beide gaan niet in git
  (te groot); ze worden via Google Drive uitgewisseld.
- Werkwijze: takes bekijken (beelden + transcript), beste take per scriptblok kiezen,
  versprekingen en stiltes wegknippen, projectbestand maken, renderen, voorbeeldbeelden
  controleren en pas dan aan Yelte voorleggen.
