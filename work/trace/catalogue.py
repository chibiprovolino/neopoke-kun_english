"""Build work/trace/catalogue.html: every room event, visitor, stick-wiggle gag and megaphone reaction,
with its snapshot strip (work/trace/out/<name>/strip.png), what it shows (catalogue_desc.py) and its conditions (ROM tables).
  python work/trace/catalogue.py"""
import os, io, base64, struct, collections, html, sys
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import catalogue_desc as D
rom = open(os.path.join(here, "../../rom/original.ngc"), "rb").read()
R = lambda off, a, b: [(i, rom[off + i * 32: off + i * 32 + 32]) for i in range(a, b)]
room, vis, t45, t46 = R(0x40000, 1, 202), R(0x42000, 1, 263), R(0x45000, 1, 17), R(0x46000, 0, 40)
STATE = rom[0x7c4e:0x7c4e + 0x53]
STATE_NAME = ["standing", "sitting", "lying down", "lying face down", "busy", "in the bathroom", "asleep"]
DIRS = {1: "Up", 2: "Left", 3: "Down", 4: "Right"}
ZONE = {1: "left", 2: "middle", 3: "right"}
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
ALLYEAR = (1, 1, 12, 31)
s8 = lambda b: b - 256 if b > 127 else b
u16 = lambda r, o: struct.unpack_from("<H", r, o)[0]


def uniq(xs):
    out = []
    for x in xs:
        if x not in out: out.append(x)
    return out


def rng(vals, fmt=str):
    lo, hi = min(vals), max(vals)
    return fmt(lo) if lo == hi else fmt(lo) + " to " + fmt(hi)


def signed(v): return "%+d" % v


def common(recs):
    """Condition lines shared by all four tables (bytes 0-15)."""
    L = []
    hours = uniq("%02d:%02d–%02d:%02d" % (r[4], r[5], r[6], r[7]) for _, r in recs)
    L.append(("Hours", "any" if hours == ["00:00–23:59"] else ", ".join(sorted(hours))))
    dated = [r for _, r in recs if tuple(r[0:4]) != ALLYEAR]
    if dated:
        dates = uniq("%s %d – %s %d" % (MON[r[0] - 1], r[1], MON[r[2] - 1], r[3]) for r in dated)
        L.append(("Dates", ", ".join(dates) + ("" if len(dated) == len(recs) else ", or any day")))
    moods = uniq((s8(r[8]), s8(r[9])) for _, r in recs)
    L.append(("Mood", "any" if moods == [(-100, 100)] else ", ".join("%d to %d" % m for m in sorted(moods))))
    L.append(("Counter A needed", rng([u16(r, 11) for _, r in recs])))
    ch = sorted(set(r[15] for _, r in recs), reverse=True)
    L.append(("Chance per check", ", ".join(("%d%%" % (c * 100 // 256)) if c else "only as a follow-up" for c in ch)))
    L.append(("Gives", "counter A +" + rng([u16(r, 13) for _, r in recs]) + ", mood " + rng([s8(r[10]) for _, r in recs], signed)))
    return L


def strip(name):
    im = Image.open(os.path.join(here, "out", name, "strip.png")).convert("RGB")
    im = im.quantize(48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), im.size


entries = collections.OrderedDict()   # section -> list of dict(id, title, tag, desc, lines, img)

# room events
sec = entries["room"] = []
by = collections.defaultdict(list)
for i, r in room: by[r[17]].append((i, r))
for eid in sorted(by):
    recs = by[eid]; L = common(recs)
    need = []
    held = sorted(set(r[20] for _, r in recs)); zone = sorted(set(r[18] for _, r in recs)); inp = sorted(set(r[19] for _, r in recs))
    if held != [0]: need.append("hold " + " or ".join(DIRS[h] for h in held if h) + (" (some versions need nothing held)" if 0 in held else ""))
    if zone != [0]: need.append("Poke-kun at the " + " or ".join(ZONE[z] for z in zone if z) + " of the room" + (" (some versions anywhere)" if 0 in zone else ""))
    if inp != [0]: need.append("stick used in the last " + rng([x for x in inp if x]) + " s" + (" (some versions: stick untouched)" if 0 in inp else ""))
    else: need.append("stick untouched")
    L.append(("Player input", "; ".join(need)))
    extra = []
    if any(r[21] for _, r in recs): extra.append("once per menu visit")
    nx = sorted(set(r[24] for _, r in recs if r[24]))
    if nx: extra.append("leads to event " + ", ".join(map(str, nx)))
    par = sorted(set(q[17] for _, q in room if q[24] == eid))
    if par: extra.append("follows event " + ", ".join(map(str, par)))
    w = max(r[22] for _, r in recs); b = max(r[23] for _, r in recs)
    if w: extra.append("can send him to work (%d%%)" % (w * 100 // 256))
    if b: extra.append("can cause a bad reaction (%d%%)" % (b * 100 // 256))
    if extra: L.append(("Also", "; ".join(extra)))
    nums = ", ".join(str(i) for i, _ in recs[:8]) + ("…" if len(recs) > 8 else "")
    sec.append(dict(id="r%02d" % eid, title="Room event %d" % eid, tag=STATE_NAME[STATE[eid]], desc=D.ROOM[eid],
                    lines=[("Records", "%d (numbers %s)" % (len(recs), nums))] + L))

# visitors
sec = entries["visitor"] = []
by = collections.defaultdict(list)
for i, r in vis: by[r[19]].append((i, r))
fam = {}
for ids, label, guess in D.VISITOR_FAMILIES:
    for v in ids: fam[v] = (label, guess, ids)
for vid in sorted(by):
    recs = by[vid]; L = common(recs); label, guess, ids = fam[vid]
    met = sorted(set(r[18] for _, r in recs)); prev = sorted(set(r[17] for _, r in recs)); rr = sorted(set(r[27] for _, r in recs))
    if met != [0]: L.append(("Must already have met", "visitor " + " or ".join(str(m) for m in met if m) + (" (some versions: nobody)" if 0 in met else "")))
    if prev != [0]: L.append(("Previous visitor", "visitor " + " or ".join(str(p) for p in prev if p) + ", within " + rng([r[16] for _, r in recs if r[17]]) + " s" + (" (some versions: any)" if 0 in prev else "")))
    if rr != [0]: L.append(("Last room event", "record " + ", ".join(str(x) for x in rr if x) + (" (some versions: any)" if 0 in rr else "")))
    blocked = [STATE_NAME[k] for k in range(6) if all(r[21 + k] for _, r in recs)]
    if blocked: L.append(("Never while", ", ".join(blocked)))
    L.append(("Reaction type", str(recs[0][1][28])))
    sec.append(dict(id="v%02d" % vid, title="Visitor %d" % vid, tag=(guess + "?") if guess else "", desc=label + ". " + D.VISITOR[vid],
                    lines=[("Records", str(len(recs))), ("Same character", ", ".join(str(x) for x in ids if x != vid) or "none")] + L))

# stick wiggle
sec = entries["wiggle"] = []
for i, r in sorted(t45, key=lambda x: x[1][22]):
    L = common([(i, r)]); L.append(("Wiggle score needed", str(r[24]))); L.append(("Position", "Poke-kun in the middle" if r[23] == 2 else "anywhere"))
    sec.append(dict(id="w%02d" % r[22], title="Wiggle gag %d" % r[22], tag="", desc=D.WIGGLE[r[22]], lines=L))

# megaphone
sec = entries["mega"] = []
by = collections.defaultdict(list)
for i, r in t46: by[r[16]].append((i, r))
for mid in sorted(by):
    sec.append(dict(id="m%02d" % mid, title="Megaphone reaction %d" % mid, tag="", desc=D.MEGA[mid], lines=[("Records", str(len(by[mid])))] + common(by[mid])))

total = 0
for s in entries.values():
    for e in s:
        e["img"], e["size"] = strip(e["id"]); total += len(e["img"])
print({k: len(v) for k, v in entries.items()}, "image bytes", total)

SEC = [("room", "Room events", "What Poke-kun does on his own. The game checks for one every few seconds while nothing else is happening. The chip shows the state the event leaves him in."),
       ("visitor", "Visitors", "Who comes in when you ring the bell with A. Ids 70 to 89 are the same characters calling while Poke-kun is in the bathroom: their records are only allowed in that state. The snapshots were forced with him in the room, so they show him standing and watching. Scenes that end in a screen of static are break-ins: the door is knocked down and put back afterwards."),
       ("wiggle", "Stick-wiggle gags", "Triggered by changing direction quickly on the stick without letting go."),
       ("mega", "Megaphone reactions", "How Poke-kun reacts when you press A while the megaphone hangs on the door. The megaphone has no picture of its own, so the snapshots show his reaction.")]
esc = html.escape


def card(e):
    w, h = e["size"]
    rows = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(k), esc(v)) for k, v in e["lines"])
    tag = '<span class="chip">%s</span>' % esc(e["tag"]) if e["tag"] else ""
    return ('<article class="ev" id="%s" data-t="%s"><header><h3>%s</h3>%s</header><p class="desc">%s</p>'
            '<div class="strip" tabindex="0"><img src="%s" width="%d" height="%d" alt="Snapshots of %s" loading="lazy"></div><dl>%s</dl></article>'
            % (e["id"], esc((e["title"] + " " + e["tag"] + " " + e["desc"]).lower()), esc(e["title"]), tag, esc(e["desc"]), e["img"], w, h, esc(e["title"].lower()), rows))


body = "".join('<section id="%s"><h2>%s <span class="n">%d</span></h2><p class="lead">%s</p>%s</section>'
               % (k, esc(t), len(entries[k]), esc(lead), "".join(card(e) for e in entries[k])) for k, t, lead in SEC)
nav = "".join('<a href="#%s">%s <span class="n">%d</span></a>' % (k, esc(t), len(entries[k])) for k, t, _ in SEC)
page = open(os.path.join(here, "catalogue_tpl.html"), encoding="utf-8").read()
page = page.replace("{{NAV}}", nav).replace("{{BODY}}", body).replace("{{COUNT}}", str(sum(len(v) for v in entries.values())))
open(os.path.join(here, "catalogue.html"), "w", encoding="utf-8", newline="\n").write(page)
print("catalogue.html", len(page) // 1024, "KB")
