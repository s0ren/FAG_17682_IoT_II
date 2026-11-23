---
name: undervisningsside
description: Write or revise a teaching page (undervisningsside) for the IoT site — a topic page in Grundlag/ or Features/ with explanation, ESP32 code examples and exercises. Use when asked to write material on an IoT/ESP32 topic, e.g. "skriv en side om deep sleep".
---

# Undervisningsside

How to write a teaching page for the 17682 IoT og Embeddede systemer site. Read the site's CLAUDE.md first; this skill adds the rules for teaching content.

## Readers and tone

- Apprentices (lærlinge) on the Datatekniker programme, speciale programmering, niveau 3.0. They can program, but embedded and electronics may be new.
- Danish, plain and direct. Short paragraphs. Explain a term the first time it is used.
- English technical terms are fine where Danish has no common word. Mark them the first time: `[pull-up]{lang="en"}`.
- No filler and no marketing tone. Every section should help the student do or understand something.

## Where the page goes

- `Grundlag/`: basics from part 1 of the subject (PlatformIO, Hello World, C++, ESP32 specs, debouncing, WiFi).
- `Features/`: what is new in part 2 (deep sleep, file system, MESH/ESP-NOW, MQTT …).
- One page per topic: `<folder>/<emne>.qmd`, file name in lower case without spaces or æøå (e.g. `debouncing.qmd`, `deep_sleep.qmd`).
- Images go in `<folder>/images/`, with `fig-alt` describing what the picture shows.

## Front matter

```yaml
---
title: "Debouncing"
subtitle: "Stabil aflæsning af knapper"   # optional
date: 2026-11-22                          # the day the page is created
maalpinde: [11, 19, 23]                   # numbers from _fagbeskrivelse/
draft: true                               # always; the teacher removes it after review
---
```

- `maalpinde`: the målpinde (1–24) the page actually helps with. Read `_fagbeskrivelse/17682-IoT og Embeddede systemer.md`. Two to four is typical; don't list every loosely related one.
- Don't add `author`, `lang`, `toc`, `lightbox` or `format: html`; they come from `_quarto.yml`. Add `format: {html: default, typst: default}` only if the teacher asks for a PDF.

## Structure

Use these sections, in this order, with these headings. Leave a section out only if it has nothing to say.

1. Intro paragraph (no heading): what the topic is and why it matters, in two to four sentences, with a concrete situation.
2. `## Formål`: what the student can do after the page, as a short list ("Du kan …").
3. `## Målpinde`: one line linking to the Læringsmål page, e.g. `Siden arbejder med målpind 11, 19 og 23 (se [Læringsmål](../laeringsmaal.qmd)).` Use the same numbers as `maalpinde`.
4. `## Forudsætninger`: what the student must know or have (pages, hardware, wiring). Link to other site pages only if they exist; otherwise name the topic in plain text.
5. `## <Forklaring>`: one or more sections with the concepts. Use a heading that names the content, not the word "Forklaring". Diagrams or tables where they help.
6. `## Eksempel` (or several `## Eksempel: …`): complete code that the student can paste into a new PlatformIO project (see Code).
7. `## Øvelser`: numbered, from easy to harder. The last one may be marked *Ekstra*. Each exercise says what to observe or hand in.
8. `## Typiske fejl`: short list of mistakes and how to spot them.
9. `## Læs videre` (optional): one or two good tutorials (e.g. Random Nerd Tutorials, ESP32IO) that add something, with a `###` per article. Read them first and point out errors in them. Exercises may refer to this section.
10. `## Kilder`: links to the documentation the page is based on.

## Code

- **Arduino framework in PlatformIO** on the **ESP32-DEVKIT-V1**. Every example shows both files:
  - `platformio.ini` with `[env:esp32doit-devkit-v1]`, `platform = espressif32@8.0.0`, `board = esp32doit-devkit-v1`, `framework = arduino`, `monitor_speed = 115200`, plus `lib_deps` if a library is used (pin the major version, e.g. `@^1.0.6`).
  - The platform is pinned to `espressif32@8.0.0`, which ships Arduino-ESP32 core 3.3.x. Check facts against core 3.x (the `master` branch of arduino-esp32), not 2.x. Change the pin only when the teacher decides to, and then on all pages.
  - `src/main.cpp` starting with `#include <Arduino.h>`.
- Code blocks get a language and a file name: ```` ```{.cpp filename="src/main.cpp"} ```` and ```` ```{.ini filename="platformio.ini"} ````.
- Follow the requirements the assignments set for the students' own code: configuration (pins, times, thresholds) as named constants at the top, short functions, Danish comments that explain *why*.
- Avoid `delay()` in `loop()` unless the point is to show why it is a problem; prefer `millis()`. Be precise about why: on the ESP32, `delay()` is `vTaskDelay()`, so only the task running `loop()` pauses; WiFi and other tasks keep running.
- `Serial.begin(115200)` to match `monitor_speed`.
- GPIO choice on the DEVKIT-V1: prefer 18, 19, 21, 22, 23, 25, 26, 27, 32, 33. Don't use 6–11 (internal flash; on some modules also 16–17). 34–39 are input only and have no internal pull-up/pull-down. 0, 2, 5, 12 and 15 are the strapping pins that affect boot (Espressif's ESP32 datasheet; Random Nerd Tutorials wrongly adds GPIO 4). With a button to GND, only GPIO 0 actually breaks boot (it enters download mode). ADC2 pins can't be read as analog while WiFi is on. The on-board LED is GPIO 2. (Sources: Espressif ESP32 datasheet, esptool boot mode docs, ESP-IDF GPIO page and Random Nerd Tutorials' pinout reference, checked 2026-11-23.)

## Checking the facts

The code can't be compiled in the dev container (no PlatformIO there, by the teacher's choice). So:

- Check every library name, function signature, default value and pin fact against official sources: the library's own repo/source, Arduino-ESP32 docs (<https://docs.espressif.com/projects/arduino-esp32/en/latest/>), PlatformIO docs and registry, and ESP-IDF docs where they say more (e.g. which GPIOs can wake from deep sleep). Use the web-fetch agent; don't rely on memory.
- Put the sources you used in `## Kilder`.
- Anything you could not confirm gets an HTML comment for the teacher right where it matters: `<!-- TJEK: lib_deps-navnet kunne ikke bekræftes i PlatformIO-registret -->`. These comments don't show on the site.
- At the top of the body, add `<!-- IKKE KOMPILERET: eksemplerne er tjekket mod dokumentationen, men ikke kompileret eller testet på hardware. -->` until the teacher has tested them.
- Right below it, keep one comment block that starts with `TJEKLISTE TIL LÆREREN (afprøves, før draft: true fjernes):` and numbers every hardware test, TJEK point and BILLEDE point on the page, ending with a step to remove IKKE KOMPILERET, the checklist and the TJEK/BILLEDE comments. Update it whenever the page changes.
- Where the teacher's own screenshot would help, add `<!-- BILLEDE: what it should show -->` (3–5 per page at most), and link to official pages with screenshots instead of copying images.

## When several agents write pages at the same time

- Only create or edit the files you were asked to write (your page and its `images/`).
- Don't edit `_quarto.yml`, `CLAUDE.md`, index pages or other pages.
- Don't run `quarto render` or `quarto preview`; parallel builds collide in `output/`. The main session builds afterwards.
- Report back: files written, målpinde chosen and why, sources used, and every TJEK comment.

## Finishing (main session)

- `quarto render` the page and fix warnings.
- Leave `draft: true`. Tell the teacher what to check, especially the TJEK comments and that the code is not compiled.
