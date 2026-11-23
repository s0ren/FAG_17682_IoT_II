export const meta = {
  name: 'undervisningssider',
  description: 'Skriv, faktatjek og ret undervisningssider til IoT-sitet (skribent → faktatjekker → skribent)',
  whenToUse: 'When the teacher wants one or more teaching pages written for Grundlag/ or Features/. Pass args as a list of {emne, fil, noter?}.',
  phases: [
    { title: 'Skriv', detail: 'skribent skriver hver side efter skill\'en undervisningsside' },
    { title: 'Faktatjek', detail: 'faktatjekker gennemgår hver side uafhængigt' },
    { title: 'Ret', detail: 'skribent retter fejl og samler resten i sidens TJEKLISTE' },
  ],
}

// args: [{ emne: "Deep Sleep", fil: "Features/deep_sleep.qmd", noter: "wake-up via knap og timer" }, ...]
// fil er relativ til sitets rod. Siden må ikke findes i forvejen, medmindre noter siger, at den skal skrives om.
const ROOT = '/workspaces/FAG_17682_IoT_II'
const items = Array.isArray(args) ? args : []
if (!items.length) {
  log('Ingen emner. Kør med args: [{emne, fil, noter?}, ...]')
  return { sider: [] }
}

const WRITE_SCHEMA = {
  type: 'object',
  properties: {
    fil: { type: 'string' },
    maalpinde: { type: 'array', items: { type: 'object', properties: { nr: { type: 'integer' }, hvorfor: { type: 'string' } }, required: ['nr', 'hvorfor'] } },
    kilder: { type: 'array', items: { type: 'string' } },
    tjek: { type: 'array', items: { type: 'string' }, description: 'Hver TJEK-kommentar på siden' },
    billeder: { type: 'array', items: { type: 'string' }, description: 'Hver BILLEDE-kommentar på siden' },
    udeladt: { type: 'array', items: { type: 'string' } },
  },
  required: ['fil', 'maalpinde', 'kilder', 'tjek', 'billeder', 'udeladt'],
}

const FINDING = {
  type: 'object',
  properties: {
    linje: { type: 'integer' },
    citat: { type: 'string' },
    problem: { type: 'string' },
    rettelse: { type: 'string' },
    kilde: { type: 'string' },
  },
  required: ['citat', 'problem', 'rettelse'],
}
const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    fejl: { type: 'array', items: FINDING },
    tvivlsomt: { type: 'array', items: FINDING },
    smaating: { type: 'array', items: FINDING },
    korrekt: { type: 'array', items: { type: 'string' } },
  },
  required: ['fejl', 'tvivlsomt', 'smaating', 'korrekt'],
}

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    rettet: { type: 'array', items: { type: 'string' } },
    ikke_rettet: { type: 'array', items: { type: 'object', properties: { punkt: { type: 'string' }, hvorfor: { type: 'string' } }, required: ['punkt', 'hvorfor'] } },
    tjekliste: { type: 'array', items: { type: 'string' }, description: 'Punkterne i sidens TJEKLISTE-kommentar efter rettelserne' },
  },
  required: ['rettet', 'ikke_rettet', 'tjekliste'],
}

const results = await pipeline(
  items,

  // 1. Skriv
  (item) => agent(
    `Write the teaching page on the topic "${item.emne}".\n` +
    `Target file: ${ROOT}/${item.fil}\n` +
    (item.noter ? `Notes from the teacher: ${item.noter}\n` : '') +
    `Other pages are being written at the same time by other agents: only touch your own file.`,
    { agentType: 'skribent', phase: 'Skriv', label: `skriv: ${item.emne}`, schema: WRITE_SCHEMA }
  ),

  // 2. Faktatjek: kun stien, ikke skribentens konklusioner
  (written, item) => agent(
    `Review ${ROOT}/${item.fil}. Write the findings in Danish. ` +
    `The site pins platform = espressif32@8.0.0 (Arduino-ESP32 core 3.3.x) on purpose; check that the page uses it, but don't flag the pin itself.`,
    { agentType: 'faktatjekker', phase: 'Faktatjek', label: `tjek: ${item.emne}`, schema: CHECK_SCHEMA }
  ).then(check => ({ written, check })),

  // 3. Ret
  ({ written, check }, item) => agent(
    `Revise your teaching page ${ROOT}/${item.fil} after an independent fact check. Read the current file first.\n\n` +
    `Rules:\n` +
    `- "fejl": fix every one, unless you can show from an official source that the checker is wrong; then leave it and say why.\n` +
    `- "tvivlsomt": rephrase so the page only claims what is confirmed, or add a <!-- TJEK: ... --> comment at that spot for the teacher.\n` +
    `- "smaating": fix the ones that are quick and clearly right.\n` +
    `- Remove TJEK comments the checker has now confirmed.\n` +
    `- Keep "## Læs videre" (if any) right before "## Kilder".\n` +
    `- Right below the IKKE KOMPILERET comment, keep or create one comment block starting with "TJEKLISTE TIL LÆREREN (afprøves, før draft: true fjernes):", numbering every remaining hardware test, every TJEK point and every BILLEDE point, and ending with a step to remove IKKE KOMPILERET, the checklist and the TJEK/BILLEDE comments.\n` +
    `- Only edit this one file. Keep draft: true.\n\n` +
    `Fact-check result (JSON):\n${JSON.stringify(check, null, 2)}`,
    { agentType: 'skribent', phase: 'Ret', label: `ret: ${item.emne}`, schema: FIX_SCHEMA }
  ).then(fix => ({ emne: item.emne, fil: item.fil, written, check, fix })),
)

const sider = results.filter(Boolean)
const fejlede = items.filter((it, i) => !results[i]).map(it => it.emne)
if (fejlede.length) log(`Ikke færdige: ${fejlede.join(', ')}`)
log(`${sider.length} af ${items.length} sider skrevet, tjekket og rettet. Hovedsessionen skal bygge sitet og gennemgå resultatet.`)

return {
  sider: sider.map(s => ({
    emne: s.emne,
    fil: s.fil,
    maalpinde: s.written ? s.written.maalpinde : [],
    fejl_fundet: s.check ? s.check.fejl.length : null,
    tvivlsomt_fundet: s.check ? s.check.tvivlsomt.length : null,
    rettet: s.fix ? s.fix.rettet : [],
    ikke_rettet: s.fix ? s.fix.ikke_rettet : [],
    tjekliste: s.fix ? s.fix.tjekliste : [],
  })),
  fejlede,
}
