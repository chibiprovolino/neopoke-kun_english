"""Run every MAME tour route and build build/tour/index.html.
usage: python tools/tour/run_tour.py <rom> [route ...]"""
import os, sys, glob, shutil, subprocess, json, html
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import idmap
MAME = os.environ.get('MAME', os.path.join(os.environ.get('MAME_DIR', '.'), 'mame.exe'))
ROMPATH = os.environ.get('MAME_ROMPATH', os.path.join(os.environ.get('MAME_DIR', '.'), 'roms'))
OUT = os.path.join(ROOT, 'build', 'tour')
SCALE = 3

def run_route(rom, route, idm, name=None, extra_env=None):
    name = name or os.path.splitext(os.path.basename(route))[0]
    d = os.path.join(OUT, name)
    shutil.rmtree(d, ignore_errors=True)
    raw = os.path.join(d, 'raw'); os.makedirs(raw)
    work = os.path.join(d, 'mame'); os.makedirs(work)   # private cfg/nvram dir: always a cold boot
    env = dict(os.environ, TOUR_OUT=d, TOUR_IDMAP=idm, TOUR_LIB=os.path.join(HERE, 'lib.lua'), **(extra_env or {}))
    cmd = [MAME, 'ngpc', '-cart', os.path.abspath(rom), '-rompath', ROMPATH,
           '-autoboot_script', os.path.abspath(route), '-nothrottle', '-sound', 'none',
           '-skip_gameinfo', '-window', '-nomaximize', '-snapshot_directory', raw,
           '-snapname', '%i', '-cfg_directory', os.path.join(work, 'cfg'),
           '-nvram_directory', os.path.join(work, 'nvram')]
    subprocess.run(cmd, cwd=work, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
    shots = []
    for line in open(os.path.join(d, 'log.txt')):
        p = line.split()
        if p[0] != 'snap': continue
        n, frame, tag = int(p[1]), int(p[2]), p[3]
        ids = [int(x) for x in p[4].split(',')] if len(p) > 4 else []
        src = os.path.join(raw, '%04d.png' % (n - 1))
        if not os.path.exists(src): continue
        im = Image.open(src)
        im = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
        fn = '%03d_f%05d.png' % (n, frame)
        im.save(os.path.join(d, fn))
        shots.append({'file': f'{name}/{fn}', 'frame': frame, 'tag': tag, 'ids': ids})
    shutil.rmtree(raw, ignore_errors=True); shutil.rmtree(work, ignore_errors=True)
    json.dump(shots, open(os.path.join(d, 'shots.json'), 'w'), indent=1)
    return name, shots

def retry_preview(rom, route, idm, name, shots, tries=3):
    """Re-show strings whose preview missed (the prompt sometimes ignores Option while Poke-kun is busy)."""
    for t in range(tries):
        miss = [s for s in shots if s['tag'].startswith('show') and int(s['tag'][4:]) not in s['ids']]
        if not miss: break
        ids = [int(s['tag'][4:]) for s in miss]
        print('  retry', ids, flush=True)
        rn, rshots = run_route(rom, route, idm, name='zz_retry', extra_env={'TOUR_PREVIEW_IDS': ','.join(map(str, ids))})
        good = {s['tag']: s for s in rshots if int(s['tag'][4:]) in s['ids']}
        for s in shots:
            g = good.get(s['tag'])
            if g and int(s['tag'][4:]) not in s['ids']:
                old = os.path.join(OUT, s['file'])
                if os.path.exists(old): os.remove(old)
                fn = os.path.basename(s['file']).split('_')[0] + '_retry_' + os.path.basename(g['file'])
                shutil.move(os.path.join(OUT, g['file']), os.path.join(OUT, name, fn))
                s.update(g, file=f'{name}/{fn}')
        shutil.rmtree(os.path.join(OUT, 'zz_retry'), ignore_errors=True)
    json.dump(shots, open(os.path.join(OUT, name, 'shots.json'), 'w'), indent=1)
    return name, shots

def index(results):
    S = json.load(open(os.path.join(ROOT, 'script', 'strings.json'), encoding='utf8'))
    cats = json.load(open(os.path.join(ROOT, 'review', 'lines.json'), encoding='utf8'))
    cat = {i: l['cat'] for l in cats for i in l['ids']}
    seen = set()
    try: en = json.load(open(os.path.join(ROOT, 'build', 'tr_drafts.json'), encoding='utf8'))
    except Exception: en = {}
    h = ['<!doctype html><meta charset=utf-8><title>Tour contact sheet</title><style>',
         'body{font:13px sans-serif;background:#222;color:#ddd;margin:16px}figure{display:inline-block;margin:6px;vertical-align:top;width:488px}',
         'img{image-rendering:pixelated;border:1px solid #555}figcaption{font-size:12px}code{color:#9cf}</style><h1>MAME tour</h1>']
    body = []
    for name, shots in results:
        body.append(f'<h2 id="{name}">{name}</h2>')
        if name == 'zz_preview':
            body.append('<p>Each string forced into the save-prompt box (real font routine, wrong screen). The box shows only 2 lines; strings with more are marked.</p>')
        lastcat = None
        for s in shots:
            if name == 'zz_preview' and s['tag'].startswith('show'):
                i = int(s['tag'][4:]); c = cat.get(i, 'other')
                if c != lastcat: body.append(f'<h3>{c}</h3>'); lastcat = c
                t = en.get(str(i), '')
                nl = t.count(chr(10)) + 1
                warn = f' <b style="color:#f88">{nl} lines</b>' if nl > 2 else ''
                body.append(f'<figure><img src="{s["file"]}" width=480 loading=lazy><figcaption><code title="{html.escape(S[i]["jp"])}">s{i:03d}</code>{warn}<br>{html.escape(t).replace(chr(10), "<br>")}<br><small>{html.escape(S[i]["jp"]).replace(chr(10), " / ")}</small></figcaption></figure>')
                seen.update(s['ids'])
                continue
            seen.update(s['ids'])
            cap = ', '.join(f'<code title="{html.escape(S[i]["jp"])}">{i}</code>' for i in s['ids']) or '(no new script reads)'
            body.append(f'<figure><img src="{s["file"]}" width=480><figcaption>frame {s["frame"]} ({s["tag"]}) &mdash; ids {cap}</figcaption></figure>')
    # coverage summary per category
    by = {}
    for i, c in cat.items(): by.setdefault(c, [0, 0]); by[c][1] += 1; by[c][0] += i in seen
    h.append('<table><tr><th>category<th>ids seen')
    for c, (a, b) in by.items(): h.append(f'<tr><td>{c}<td>{a}/{b}')
    h.append('</table><p>Routes: ' + ' '.join(f'<a href="#{n}">{n}</a>' for n, _ in results))
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write('\n'.join(h + body))
    return seen

def main():
    rom = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    idm = os.path.join(OUT, 'idmap.lua')
    idmap.build(rom, idm, os.path.join(ROOT, 'script', 'strings.json'))
    routes = sorted(glob.glob(os.path.join(HERE, 'routes', '*.lua')))
    if len(sys.argv) > 2: routes = [r for r in routes if os.path.splitext(os.path.basename(r))[0] in sys.argv[2:]]
    results = []
    for r in routes:
        print('route', r, flush=True)
        results.append(run_route(rom, r, idm))
        if results[-1][0] == 'zz_preview': results[-1] = retry_preview(rom, r, idm, *results[-1])
        print('  shots', len(results[-1][1]), flush=True)
    # keep results of routes not re-run this time
    done = {n for n, _ in results}
    for p in sorted(glob.glob(os.path.join(OUT, '*', 'shots.json'))):
        n = os.path.basename(os.path.dirname(p))
        if n not in done and not n.startswith('show_') and n != 'zz_retry': results.append((n, json.load(open(p))))
    results.sort()
    seen = index(results)
    print('ids seen:', len(seen))
def retry_only(rom):
    idm = os.path.join(OUT, 'idmap.lua'); idmap.build(rom, idm, os.path.join(ROOT, 'script', 'strings.json'))
    shots = json.load(open(os.path.join(OUT, 'zz_preview', 'shots.json')))
    retry_preview(rom, os.path.join(HERE, 'routes', 'zz_preview.lua'), idm, 'zz_preview', shots)

if __name__ == '__main__':
    if '--retry' in sys.argv: sys.argv.remove('--retry'); retry_only(sys.argv[1])
    main()
