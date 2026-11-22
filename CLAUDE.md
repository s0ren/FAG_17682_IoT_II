# CLAUDE.md

This file guides Claude Code when working on this Quarto website.

## What this is

A Quarto website (`project: type: website`), written in Danish, for the subject **17682 IoT og Embeddede systemer** on the Datatekniker programme (speciale programmering). It is a portal for teaching materials and learning in the subject. Students use it to find topics, exercises, project assignments and checklists. Teachers use it to collect and structure their material.

It is its own git repository. In the dev container it is mounted at `/workspaces/FAG_17682_IoT_II`. The container setup lives in a separate repo (`claude_quarto_devcont_test`), which has its own CLAUDE.md.

## Learning objectives

The subject's official learning objectives (målpinde) are in [_fagbeskrivelse/17682-IoT og Embeddede systemer.md](_fagbeskrivelse/17682-IoT%20og%20Embeddede%20systemer.md) (the leading underscore keeps Quarto from rendering it as a page), taken from <https://hentdata.stil.dk/uddannelser>. There are 24 målpinde. Roughly:

- 1–8: IoT/IIoT concepts, standards, technologies, risks, use cases and integration with existing systems such as production systems
- 9–16: building and documenting a small IoT solution, sensors and signal validation, fault finding, choice of communication protocols, security and risk analysis, network fault finding, design guidelines
- 17–24: embedded systems (hardware, programming language, tools), prototypes, I/O, sensor integration, data processing and sending data to the network, testing and debugging

The objectives guide the material but are not strictly binding. Use them to:

- find gaps and suggest which topics need material
- connect a topic, exercise or assignment to the målpinde it covers (cite them by number, e.g. "målpind 13")
- set the level of the material: the subject is at niveau 3.0 for apprentices (lærlinge)

Content may go beyond the objectives or leave some out, and the teacher decides. Don't remove or restructure existing material just to match the list.

## Layout

- `_quarto.yml`: site config: title, navbar, sidebar (`contents: auto`, built from all pages), `draft-mode: unlinked`, output to `output/` (`output-dir`). Top-level `lang: da`, `toc: true` and `author` (Søren Magnusson, Data, TEC) apply to every page and every format. `format: html` sets theme (`cosmo` + `brand`), `styles.css` and `lightbox`. There is no site-wide PDF format.
- Settings live in one place: put shared settings in `_quarto.yml` or a folder's `_metadata.yml`, and keep only page-specific settings (title, subtitle, date, `draft`, `bibliography`, `number-sections`, `format` for PDF) in a page's front matter. Don't repeat `format: html`, `lightbox`, `toc`, `lang` or author fields on pages. Never put an email address on the pages.
- `index.qmd`: front page: introduction to the second part of the subject (the first part was on H3), the hardware (ESP32-DEVKIT-V1) and the week plan (Forløb)
- `Features/`: technical guides, e.g. `lokal_mqtt.qmd` (local MQTT broker), with images in `Features/images/`
- `Opgaver/`: exercises and project assignments, e.g. `wifi_pos.qmd`, `Projektopgave_Smiley.qmd`. `Opgaver/afsluttende_opgave/` holds the final assignment and its checklist (both `draft: true` for now). `Opgaver/index.qmd` lists the assignments automatically (a Quarto listing; drafts are left out).
  - An assignment that should also be a PDF adds `format: {html: default, typst: default}` to its front matter. `Opgaver/_metadata.yml` styles the resulting "PDF" link. Typst can't be set in `_metadata.yml`, because a page can't opt out of an inherited format (the listing page would get a PDF too).
- `Referencer/`: references
- `images/`: images for the front page
- `bib/`: bibliography (`.bib`)
- `about.qmd`: "Om sitet": how the site is organised and who is behind it. In the navbar.
- `styles.css`: extra CSS for the HTML output
- `_scripts/`: helper scripts run by Quarto (`git_mtime.py`, see Conventions). Not rendered.
- `_fagbeskrivelse/`: the official subject description (målpinde). Not rendered.
- `output/` and `.quarto/`: build output and cache, ignored by git. Don't edit them by hand. (Older runs built to `_site/`; its pages from part 1, `IOT_del1_prog_tec/`, are kept in commit `247e24e`.)
- The `gh-pages` branch holds the published site (built with `quarto publish gh-pages`). Don't edit it by hand.

## Conventions

- Write content in Danish, for apprentices on the Datatekniker programme. Mark English passages with `{lang="en"}` (span or div) so spell checking and hyphenation use the right language.
- Store images locally next to the page (e.g. an `images/` folder) rather than linking to remote URLs, since Typst needs local files. Avoid spaces in image file names: Typst can't find them.
- Give images alt text with `fig-alt="..."` that describes what the picture actually shows.
- Put new pages in the folder that fits (`Features/`, `Opgaver/`, `Referencer/`). The sidebar picks them up automatically. A folder's `index.qmd` becomes its section page in the sidebar; give new folders one. Mark unfinished pages `draft: true`.
- Every page has `date:` (the date it was created) in its front matter. The modified date comes from `date-modified: last-modified` in `_quarto.yml`. Quarto reads it from the file's modification time, which the pre-render script `_scripts/git_mtime.py` sets to the file's last commit (files with uncommitted changes keep their own time). Don't set it on pages.
- Where it helps, state which målpinde a page or assignment covers.

## Branches

Each course run (skoleforløb) has its own branch, named after month and year (`Marts_2025`, `November_2025`, `maj_2026`, `November_2026`). A new run branches from the latest one. Don't change older run branches.

## Commands

```bash
quarto render              # build the whole site into output/
quarto render index.qmd    # render one page
quarto preview             # live preview
```

Render after changes to check that the site builds without errors.
