"""python cmpsheet.py name [name...] -> cmp_<name>.png: original run o_<name> (top) vs new run n_<name> (bottom), every dump"""
import sys, glob, re, os
from PIL import Image, ImageDraw
from vram import render
for name in sys.argv[1:]:
    fs = sorted(glob.glob(f'n_{name}/v*.bin'), key=lambda f: int(re.findall(r'v(\d+)', f)[0]))
    s = Image.new('RGB', (len(fs) * 164, 2 * 166 + 14), (40, 40, 40)); d = ImageDraw.Draw(s)
    for i, f in enumerate(fs):
        fr = re.findall(r'v(\d+)', f)[0]; o = f'o_{name}/v{fr}.bin'
        d.text((i * 164, 0), fr, fill='white')
        if os.path.exists(o): s.paste(render(open(o, 'rb').read()), (i * 164, 14))
        s.paste(render(open(f, 'rb').read()), (i * 164, 14 + 166))
    s.save(f'cmp_{name}.png'); print(name, len(fs))
