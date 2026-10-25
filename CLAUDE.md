# Content Magits Multiservices

Deze repository bevat scripts en ideeën voor video's op sociale media. Claude leest dit bestand bij elke sessie.

## Het bedrijf
- **Naam:** Magits Multiservices
- **Oprichter:** Yelte Magits
- **Diensten:** tuinonderhoud en rommelophaling
- **Regio:** Antwerpen, Mechelen en omstreken
- **Website:** magitsmultiservices.be
- **Telefoon:** +32 492 88 44 24
- **Handle:** Magitsmultiservices (Instagram, Facebook, TikTok, YouTube)
- **Slogan:** Vakkundig · Netjes · Betrouwbaar
- **Boodschap:** tuin en rommel in één keer geregeld
- Het bedrijf is nieuw. Doel nummer één: nieuwe klanten bereiken.

## Twee soorten video's
1. **Reclame** (`scripts/reclame/`): voor mensen in de regio die hulp zoeken.
   Bv. voor/na-beelden, tips, een dag op de werf. Spreek kijkers aan met "u".
   CTA's uit het social-media-overzicht: "Stuur ons een foto voor een prijsinschatting",
   "Stuur ons een bericht voor een offerte", "Ken je iemand die dit nodig heeft? Stuur deze video door." 
2. **Ondernemen** (`scripts/ondernemen/`): voor een breed publiek, vooral jonge mensen
   die zelf een zaak willen starten. Yelte toont hoe hij werkt, met de ups én de downs.
   Natuurlijke spreektaal, "je" mag hier. Geen reeksnaam en geen "aflevering" of "dag":
   de teller is "Week <n>" (week 1, week 2, …); beide ondernemingsvideo's van dezelfde week krijgen hetzelfde weeknummer.
   Invalshoek: Yelte die zijn eigen bedrijf probeert op te bouwen.
   Yelte is 23 en staat er voorlopig alleen voor (nog geen team).
   Yelte heeft zelf al ideeën voor de reeks uitgeschreven in Drive (zie hieronder): vertrek daarvan.

## Planning
Per week: **2 ondernemingsvideo's + 1 reclamevideo**, op Instagram, TikTok en YouTube (Shorts).

## Google Drive
Drive-pad: `07. MARKETING / 1. Social Media /`
- `Ondernemingsvideo's/Video <n>/` en `Reclamevideo's/Video <n>/`
- In elke map `Video <n>`: Claude zet het script (Google Doc "Script - Video <n>") met een
  opnamelijst. Yelte zet er zijn opnames in. Claude monteert en zet het eindresultaat
  er pas in **na goedkeuring** van Yelte (bestandsnaam `FINAAL - Video <n>.mp4`).
- Video <n> in Drive = `scripts/ondernemen/<nnn>-*.md` of `scripts/reclame/<nnn>-*.md` hier.
- Bestaande documenten in `1. Social Media/Content/`: "Ideeën ondernemingsvideo's"
  (uitgewerkte teksten voor de reeks), "Intro dat ik had", "01/2027 - Content planner",
  en in `1. Social Media/`: "SOCIAL MEDIA OVERZICHT MAGITS" (doelgroepen, contentpijlers, CTA's).

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
- Automatische ondertitels: `pip install faster-whisper` aan het begin van een sessie.
- Werkwijze: takes bekijken (beelden + transcript), beste take per scriptblok kiezen,
  versprekingen en stiltes wegknippen, projectbestand maken, renderen, voorbeeldbeelden
  controleren en pas dan aan Yelte voorleggen.
