# Huisstijl video's

Afgeleid van de kleuren en het logo van de Magits-app. `montage/monteer.py` past dit automatisch toe.

## Kleuren
| Naam | Hex | Gebruik |
|---|---|---|
| Zwart | `#000000` | achtergrond eindbeeld (altijd) |
| Bosgroen | `#154727` | reserve-accent |
| Limoen | `#8CD742` | gesproken woord in ondertitels, handle |
| Donker | `#0F1A14` | rand rond ondertitels |
| Wit | `#FFFFFF` | ondertitels, tekst bovenaan, slogan, logo |

## Lettertype: Montserrat
- **ExtraBold**: ondertitels (hoofdletters) en handle
- **Bold**: tekst bovenaan in beeld, slogan, website en telefoonnummer
- **Medium**: reserve, voor langere tekst

Bestanden in `huisstijl/fonts/` (Google Fonts, vrije SIL Open Font License).

## Ondertitels
- Hoofdletters, maximaal 3 woorden tegelijk, wit met donkere rand.
- Het woord dat op dat moment gezegd wordt, licht limoengroen op en wordt iets groter.
- Positie: onderste derde, hoog genoeg om niet onder de knoppen van TikTok/Reels te vallen.

## Tekst op het scherm
- Bovenaan, **witte letters met een dunne zwarte rand en een zachte schaduw**, zonder kader en zonder groen.
  (Keuze van Yelte: geen limoengroen kader meer, voor alle video's.)
- Moet duidelijk anders ogen dan de ondertitels (gesproken tekst): **Montserrat Bold, gewone
  hoofd- en kleine letters, wat extra letterafstand**. De ondertitels blijven ExtraBold in hoofdletters.
- Kort: maximaal 4 à 5 woorden. Emoji's worden weggelaten (die horen in de caption).

- **Hooktekst** (bovenaan tijdens de hook): zelfde stijl, maar groter (`"stijl": "hook"`).
- **Belangrijk getal** (bv. 117.000): **alleen het getal**, heel groot (Montserrat Black), wit met
  zwarte rand, met een korte pop-animatie (`"stijl": "groot"`). Geen extra woorden erbij.

- **Reclamevideo's** (zonder ondertitels): **alle** tekst bovenaan in pop-stijl (`"stijl": "pop"`):
  dik, groot, met de pop-animatie; de grootte past zich aan de lengte aan. Lange zinnen opsplitsen
  in korte stukjes die na elkaar verschijnen (bv. "Garage vol" → "Moet leeg").

## Overgangen
- Tussen alle beelden een korte vloeiende overgang (0,25 s, `"overgang"` in het projectbestand).
  Nooit harde wissels waarbij er een beeldje van de take tussen flitst.

## Eindbeeld (4 s)
Altijd een **zwarte** achtergrond met het witte logo (`logo-wit.png`, transparant), daaronder:
- **VAKKUNDIG · NETJES · BETROUWBAAR**
- magitsmultiservices.be
- +32 492 88 44 24
- **Volg @Magitsmultiservices** in limoengroen

## Formaat
1080 × 1920 (9:16), 30 fps, H.264 + AAC, geluid genormaliseerd op -14 LUFS.
