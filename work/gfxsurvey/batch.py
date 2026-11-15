"""python batch.py name:seqbody[:start:step:count] ... -> runs MAME in parallel, sheets sh_<name>.png"""
import subprocess, sys, os, re, glob
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
from vram import render
POKE = 'poke={{2250,function(sp) for a=0x4500,0x4557 do sp:write_u8(a,0xff) end end}}'
def job(name, seq, start, step, count, extra=''):
    dumps = ','.join(str(start+i*step) for i in range(count))
    open('x_%s.lua' % name, 'w').write('seq={{2300,"Button A"},{2600,"Button B"},%s}\ndumps={%s}\nstop=%d\n%s\n%s\n' % (seq, dumps, start+count*step, POKE, extra))
    subprocess.run(['bash', 'run.sh', os.environ.get('ROM', '../../rom/original.ngc'), 'x_%s.lua' % name, 'o_%s' % name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fs = sorted(glob.glob('o_%s/v*.bin' % name), key=lambda f: int(re.findall(r'v(\d+)', f)[0]))
    ims = [render(open(f, 'rb').read()) for f in fs]
    cols = 6; rows = max(1, (len(ims)+cols-1)//cols)
    s = Image.new('RGB', (cols*164, rows*168), (255, 0, 255)); d = ImageDraw.Draw(s)
    for i, (f, im) in enumerate(zip(fs, ims)):
        x, y = (i % cols)*164, (i//cols)*168; s.paste(im, (x, y+14)); d.text((x, y), name+' '+re.findall(r'v(\d+)', f)[0], fill=(0, 0, 0))
    s.save('sh_%s.png' % name); return name, len(ims)
if __name__ == "__main__":
    jobs = []
    for a in sys.argv[1:]:
        p = a.split('|'); jobs.append((p[0], p[1], *map(int, p[2:5])))
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(lambda j: job(*j), jobs): print(r)
