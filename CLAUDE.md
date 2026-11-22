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

- `_quarto.yml`: site config: title, navbar, sidebar (built automatically from `emner/`), theme (`cosmo` + `brand`), `styles.css`, TOC, `lang: da`, HTML and Typst (PDF) output
- `index.qmd`: front page. `about.qmd` exists but isn't in the navbar.
- `emner/`: one subfolder per topic, each with an `index.qmd` and any related pages. For example, `emner/afsluttende_opgave/` holds the final assignment and its checklist.
- `styles.css`: extra CSS for the HTML output
- `_fagbeskrivelse/`: the official subject description (målpinde). Not rendered.
- `_site/` and `.quarto/`: build output and cache, ignored by git (as is the old build folder `output/`). Don't edit them by hand.

## Conventions

- Write content in Danish, for apprentices on the Datatekniker programme. Mark English passages with `{lang="en"}` (span or div) so spell checking and hyphenation use the right language.
- Pages render to both HTML and Typst (PDF). Keep content working in both: store images locally (e.g. in an `images/` folder next to the page) rather than linking to remote URLs, since Typst needs local files.
- Give images alt text with `fig-alt="..."` that describes what the picture actually shows.
- New topics go in `emner/<topic>/index.qmd`; the sidebar picks them up automatically. Pages outside `emner/` must be added to `website.navbar` in `_quarto.yml` to appear in the menu.
- Where it helps, state which målpinde a topic or assignment covers.

## Commands

```bash
quarto render              # build the whole site into _site/
quarto render index.qmd    # render one page (HTML and PDF)
quarto preview             # live preview
```

Render after changes to check that both formats build without errors.
