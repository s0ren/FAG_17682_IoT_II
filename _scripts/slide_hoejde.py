"""Skøn over hver slides højde i en renderet revealjs-præsentation.

Brug:  python3 _scripts/slide_hoejde.py output/Features/mqtt_intro_slides.html

Scriptet åbner ikke en browser. Det tæller linjer i overskrifter, tekst, punkter,
kode og tabeller og regner dem om til pixels ud fra typiske størrelser i Quartos
revealjs-tema med `smaller: true` ved 1280 x 720. Det er et skøn: brug det til at
finde slides, der er tæt på grænsen, og se dem så i browseren.
"""

import html
import math
import re
import sys

HOEJDE = 720
TILGAENGELIG = 620      # ca. 720 minus revealjs' margen
ADVARSEL = 560          # tæt på grænsen

TITEL = 70              # h2-overskrift
TEKSTLINJE = 34         # brødtekst / punkt (smaller)
TEGN_PR_LINJE = 85      # tegn pr. tekstlinje ved 1280 px
KODELINJE = 27          # kodelinje
KODE_LUFT = 40          # polstring om en kodeblok (+ filnavn)
TABELRAEKKE = 42
TEGN_PR_CELLE = 38
MERMAID = 260           # et lille diagram
AFSTAND = 14            # luft mellem blokke


def tekst(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def linjer(t, bredde=TEGN_PR_LINJE):
    return max(1, math.ceil(len(t) / bredde))


def skøn(sektion):
    h = 0
    if re.search(r"<h2", sektion):
        h += TITEL
    # Kodeblokke
    for kode in re.findall(r"<pre[^>]*>(.*?)</pre>", sektion, re.S):
        n = len(tekst(kode).splitlines()) or 1
        h += KODE_LUFT + n * KODELINJE + AFSTAND
    sektion_uden_kode = re.sub(r"<pre.*?</pre>", "", sektion, flags=re.S)
    # Tabeller
    for tabel in re.findall(r"<table.*?</table>", sektion_uden_kode, re.S):
        for raekke in re.findall(r"<tr.*?</tr>", tabel, re.S):
            celler = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", raekke, re.S)
            n = max([linjer(tekst(c), TEGN_PR_CELLE) for c in celler] or [1])
            h += n * TABELRAEKKE
        h += AFSTAND
    rest = re.sub(r"<table.*?</table>", "", sektion_uden_kode, flags=re.S)
    if "mermaid" in rest or "<svg" in rest:
        h += MERMAID
    # Punkter og afsnit
    for punkt in re.findall(r"<li[^>]*>(.*?)</li>", rest, re.S):
        h += linjer(tekst(punkt)) * TEKSTLINJE + 6
    rest = re.sub(r"<[ou]l.*?</[ou]l>", "", rest, flags=re.S)
    for afsnit in re.findall(r"<p[^>]*>(.*?)</p>", rest, re.S):
        t = tekst(afsnit)
        if t:
            h += linjer(t) * TEKSTLINJE + AFSTAND
    return h


def main(sti):
    s = open(sti, encoding="utf-8").read()
    dele = re.split(r'(?=<section id="[^"]*" class="slide level2)', s)[1:]
    print(f"{'nr':>3}  {'skøn':>5}  slide")
    for nr, sek in enumerate(dele, start=2):
        sek = sek.split("</section>")[0]
        titel = tekst((re.search(r"<h2[^>]*>(.*?)</h2>", sek, re.S) or [None, ""])[1])
        h = skøn(sek)
        mærke = "FOR HØJ" if h > TILGAENGELIG else ("tæt på" if h > ADVARSEL else "")
        print(f"{nr:>3}  {h:>5}  {titel}  {mærke}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/Features/mqtt_intro_slides.html")
