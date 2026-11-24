-- Pandoc-filter til itslearning_cc.py: gør en .qmd-side til simpel HTML,
-- som itslearnings editor kan vise (ingen klasser, CSS-filer eller scripts).
--
-- Miljøvariable (sættes af itslearning_cc.py):
--   CC_SITE     sitets adresse, fx https://s0ren.github.io/FAG_17682_IoT_II/
--   CC_PAGEDIR  sidens mappe i projektet, fx Grundlag
--   CC_PAGES    kommaseparerede stier til de sider, der er med i pakken

local site = os.getenv("CC_SITE") or ""
local pagedir = os.getenv("CC_PAGEDIR") or ""
local included = {}
for p in (os.getenv("CC_PAGES") or ""):gmatch("[^,]+") do included[p] = true end

-- Sti i projektet ud fra sidens mappe, med ".." løst op
local function normalize(path)
  local parts = {}
  local full = pagedir ~= "" and (pagedir .. "/" .. path) or path
  for seg in full:gmatch("[^/]+") do
    if seg == ".." then table.remove(parts)
    elseif seg ~= "." then table.insert(parts, seg) end
  end
  return table.concat(parts, "/")
end

-- Relativ sti fra sidens mappe til en sti i projektet (pakken har samme mappestruktur)
local function relative(path)
  if pagedir ~= "" and path:sub(1, #pagedir + 1) == pagedir .. "/" then
    return path:sub(#pagedir + 2)                       -- samme mappe
  end
  local up = ""
  for _ in pagedir:gmatch("[^/]+") do up = up .. "../" end
  return up .. path
end

-- Kommentarer (TJEK, BILLEDE, tjeklister) skal ikke med
local function is_comment(el)
  return el.format:match("html") and el.text:match("^%s*<!%-%-") ~= nil
end
function RawBlock(el) if is_comment(el) then return {} end end
function RawInline(el) if is_comment(el) then return {} end end

function Link(el)
  local t = el.target
  if t:match("^%a[%w+.-]*:") or t:match("^#") then return el end   -- http:, mailto:, #anker
  local path, frag = t:match("^([^#]*)(.*)$")
  if path == "" then return el end
  local full = normalize(path)
  if full:match("%.qmd$") then
    local html = full:gsub("%.qmd$", ".html")
    if included[full] then
      el.target = relative(html) .. frag
    else
      el.target = site .. html .. frag
    end
  else
    el.target = site .. full .. frag
  end
  return el
end

-- fig-alt er Quartos alt-tekst; i HTML skal den stå i alt
function Image(el)
  local alt = el.attributes["fig-alt"]
  if alt then
    el.attributes["fig-alt"] = nil
    el.caption = pandoc.Inlines(alt)
  end
  return el
end

local CALLOUT = {
  note      = { "Bemærk",   "#0d6efd", "#e7f1ff" },
  tip       = { "Tip",      "#198754", "#e8f5ee" },
  warning   = { "Advarsel", "#b58105", "#fff8e1" },
  caution   = { "Pas på",   "#b58105", "#fff8e1" },
  important = { "Vigtigt",  "#dc3545", "#fdecea" },
}

function Div(el)
  for _, cls in ipairs(el.classes) do
    local kind = cls:match("^callout%-(%a+)$")
    if kind and CALLOUT[kind] then
      local label, color, bg = table.unpack(CALLOUT[kind])
      local blocks = el.content
      -- En overskrift øverst i boksen er boksens titel
      if #blocks > 0 and blocks[1].t == "Header" then
        label = pandoc.utils.stringify(blocks[1].content)
        blocks:remove(1)
      end
      blocks:insert(1, pandoc.Para({ pandoc.Strong(pandoc.Str(label)) }))
      return pandoc.Div(blocks, pandoc.Attr("", {}, {
        style = "border-left:4px solid " .. color .. ";background:" .. bg ..
                ";padding:8px 12px;margin:12px 0" }))
    end
    if cls == "billede-mangler" then
      local blocks = el.content
      blocks:insert(1, pandoc.Para({ pandoc.Strong(pandoc.Str("📷 Foto mangler")) }))
      return pandoc.Div(blocks, pandoc.Attr("", {}, {
        style = "border:2px dashed #999;background:#fafafa;padding:8px 12px;margin:12px 0" }))
    end
  end
end
