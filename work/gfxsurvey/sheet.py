from PIL import Image, ImageDraw
import glob, os, sys
def sheet(fs, name, sc=0.5, cols=5, maxh=330):
    ims = [Image.open(f).convert('RGB') for f in fs]
    ims = [im.resize((int(im.width*sc), int(im.height*sc)), Image.NEAREST) for im in ims]
    W = max(i.width for i in ims)+4; H = max(min(i.height, maxh) for i in ims)+14
    rows = (len(ims)+cols-1)//cols
    s = Image.new('RGB', (cols*W, rows*H), (60, 0, 60)); d = ImageDraw.Draw(s)
    for k, (f, im) in enumerate(zip(fs, ims)):
        x, y = (k % cols)*W, (k//cols)*H
        s.paste(im.crop((0, 0, im.width, min(im.height, maxh))), (x, y+12)); d.text((x, y), os.path.basename(f)[:-4], fill=(255, 255, 0))
    s.save(name); print(name, s.size)
if __name__ == "__main__":
    fs = sorted(glob.glob('screens/s*.png'))
    sheet(fs[:20], 'sheetA.png'); sheet(fs[20:40], 'sheetB.png'); sheet(fs[40:], 'sheetC.png')
