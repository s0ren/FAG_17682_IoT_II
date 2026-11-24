#!/usr/bin/env python3
"""Pakker sider fra sitet som en IMS Common Cartridge 1.1 (.imscc) til itslearning.

itslearnings "Course importer" (Ressourcer > Tilføj > Brugsklart indhold) kan læse
Common Cartridge 1.1. Hver side bliver til simpel HTML (Pandoc + itslearning_cc.lua):
ingen CSS-filer eller scripts, kommentarer fjernet, callouts og fotobokse med inline-stil,
links mellem sider i pakken relative, alle andre links til GitHub Pages-sitet.

Brug (fra sitets rod):
    python3 _scripts/itslearning_cc.py                       # standard: 3 testsider
    python3 _scripts/itslearning_cc.py Grundlag/wifi.qmd ... -o _itslearning/wifi.imscc

Pakken kommer i _itslearning/ (ignoreret af git, ikke renderet).
Begrænsninger: mermaid, faneblade, interaktive JavaScript-dele og shortcodes
(include, pagebreak) virker ikke i itslearning og bliver ikke oversat.
"""
import argparse
import datetime as dt
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
LUA = Path(__file__).with_suffix(".lua")
SITE = "https://s0ren.github.io/FAG_17682_IoT_II/"
STANDARD = ["Grundlag/standardopstilling.qmd", "Grundlag/potentiometer.qmd", "Grundlag/esp32_specs.qmd"]

MANIFEST_NS = (
    'xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" '
    'xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" '
    'xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xsi:schemaLocation="'
    "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd "
    "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd "
    'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd"'
)


def ident(prefix: str, path: str) -> str:
    return prefix + re.sub(r"[^A-Za-z0-9_]", "_", path)


def front_matter(qmd: Path) -> dict:
    """Titel og undertitel fra YAML-hovedet (kun simple linjer)."""
    meta = {}
    m = re.match(r"---\n(.*?)\n---", qmd.read_text(encoding="utf-8"), re.S)
    for line in (m.group(1) if m else "").splitlines():
        k, _, v = line.partition(":")
        if k in ("title", "subtitle"):
            meta[k] = v.strip().strip('"')
    return meta


def convert(rel: str, pages: list) -> tuple:
    """Returnerer (titel, html-dokument, billedstier i projektet)."""
    qmd = ROOT / rel
    pagedir = Path(rel).parent.as_posix()
    env = dict(os.environ, CC_SITE=SITE, CC_PAGEDIR="" if pagedir == "." else pagedir,
               CC_PAGES=",".join(pages))
    body = subprocess.run(
        ["quarto", "pandoc", str(qmd), "-f", "markdown", "-t", "html5", "--no-highlight", "--mathml",
         "--wrap=none", "--lua-filter", str(LUA)],
        env=env, check=True, capture_output=True, text=True).stdout

    # Klasser virker ikke uden sitets CSS. Tabeller og kode får inline-stil i stedet
    body = re.sub(r'\sclass="[^"]*"', "", body)
    body = re.sub(r"<table\b", '<table border="1" cellpadding="4" style="border-collapse:collapse"', body)
    body = re.sub(r"<pre\b[^>]*>", '<pre style="background:#f5f5f5;padding:8px;overflow-x:auto">', body)

    images = []
    for src in re.findall(r'<img[^>]*\bsrc="([^"]+)"', body):
        if not re.match(r"[a-z]+:", src):
            p = os.path.normpath(os.path.join(os.path.dirname(rel), src))
            images.append(p)

    meta = front_matter(qmd)
    title = meta.get("title", qmd.stem)
    online = SITE + rel.replace(".qmd", ".html")
    head = f"<h1>{html.escape(title)}</h1>\n"
    if meta.get("subtitle"):
        head += f"<p><em>{html.escape(meta['subtitle'])}</em></p>\n"
    foot = (f'\n<hr>\n<p><small>Siden er genereret fra <a href="{online}">{online}</a> '
            f"den {dt.date.today():%d.%m.%Y}. Ret i Quarto-sitet, ikke her.</small></p>\n")
    doc = ("<!DOCTYPE html>\n<html lang=\"da\">\n<head>\n<meta charset=\"utf-8\">\n"
           f"<title>{html.escape(title)}</title>\n</head>\n<body>\n{head}{body}{foot}</body>\n</html>\n")
    return title, doc, images


def weblink_xml(title: str, url: str) -> str:
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<webLink xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imswl_v1p1" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imswl_v1p1 '
            'http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imswl_v1p1.xsd">\n'
            f"  <title>{escape(title)}</title>\n"
            f'  <url href={quoteattr(url)} target="_blank"/>\n'
            "</webLink>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sider", nargs="*", default=STANDARD, help=".qmd-filer, relativt til sitets rod")
    ap.add_argument("-o", "--out", default="_itslearning/iot_test.imscc")
    ap.add_argument("-t", "--titel", default="IoT II (test af import)", help="navnet på mappen i itslearning")
    a = ap.parse_args()

    pages = [str(Path(p)) for p in a.sider]
    for p in pages:
        if not (ROOT / p).exists():
            sys.exit(f"Findes ikke: {p}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        items, resources, all_images = [], [], set()
        for rel in pages:
            title, doc, images = convert(rel, pages)
            out = tmp / rel.replace(".qmd", ".html")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(doc, encoding="utf-8")
            all_images.update(images)
            rid = ident("res_", rel)
            href = rel.replace(".qmd", ".html")
            items.append(f'        <item identifier="{ident("itm_", rel)}" identifierref="{rid}">'
                         f"<title>{escape(title)}</title></item>")
            dep = '\n      <dependency identifierref="res_images"/>' if images else ""
            resources.append(f'    <resource identifier="{rid}" type="webcontent" href="{href}">\n'
                             f'      <file href="{href}"/>{dep}\n    </resource>')
            print(f"  {rel} -> {href}" + (f" ({len(images)} billede(r))" if images else ""))

        # Billeder: én fælles ressource, som siderne afhænger af
        if all_images:
            files = []
            for img in sorted(all_images):
                src = ROOT / img
                if not src.exists():
                    sys.exit(f"Billede findes ikke: {img}")
                (tmp / img).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, tmp / img)
                files.append(f'      <file href="{img}"/>')
            resources.append('    <resource identifier="res_images" type="webcontent">\n'
                             + "\n".join(files) + "\n    </resource>")

        # Link til hele sitet
        (tmp / "weblinks").mkdir()
        (tmp / "weblinks/site.xml").write_text(weblink_xml("Hele sitet (GitHub Pages)", SITE), encoding="utf-8")
        items.append('        <item identifier="itm_site" identifierref="res_site"><title>Hele sitet (GitHub Pages)</title></item>')
        resources.append('    <resource identifier="res_site" type="imswl_xmlv1p1">\n'
                         '      <file href="weblinks/site.xml"/>\n    </resource>')

        manifest = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<manifest identifier="iot_cc_{dt.date.today():%Y%m%d}" {MANIFEST_NS}>\n'
            "  <metadata>\n    <schema>IMS Common Cartridge</schema>\n    <schemaversion>1.1.0</schemaversion>\n"
            "    <lomimscc:lom>\n      <lomimscc:general>\n        <lomimscc:title>\n"
            f'          <lomimscc:string language="da">{escape(a.titel)}</lomimscc:string>\n'
            "        </lomimscc:title>\n      </lomimscc:general>\n    </lomimscc:lom>\n  </metadata>\n"
            '  <organizations>\n    <organization identifier="org_1" structure="rooted-hierarchy">\n'
            '      <item identifier="root">\n'
            f'      <item identifier="itm_mappe"><title>{escape(a.titel)}</title>\n'
            + "\n".join(items) + "\n      </item>\n      </item>\n    </organization>\n  </organizations>\n"
            "  <resources>\n" + "\n".join(resources) + "\n  </resources>\n</manifest>\n")
        (tmp / "imsmanifest.xml").write_text(manifest, encoding="utf-8")

        out = ROOT / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(tmp / "imsmanifest.xml", "imsmanifest.xml")   # manifestet først
            for f in sorted(tmp.rglob("*")):
                if f.is_file() and f.name != "imsmanifest.xml":
                    z.write(f, f.relative_to(tmp).as_posix())
    print(f"Skrev {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
