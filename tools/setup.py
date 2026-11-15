"""One-time setup from your own ROM: python tools/setup.py [path/to/rom.ngc]

Checks the ROM (CRC32 6DF986A3), copies it to rom/original.ngc if a path is given, then writes the files the
other tools read, all generated from the ROM and all git-ignored:
  script/strings.json   every script string with its Japanese text (tools/extract.py)
  review/lines.json     unique lines with their string ids (tools/mklines.py), plus font and width per line
  review/font.json      the three fonts as bitmaps, for the review page (tools/review_fonts.py)
                        lines.json also gets the current English from script/page.json (tools/page_lines.py)
Run from the repository root."""
import os, shutil, subprocess, sys, zlib

CRC = 0x6DF986A3
ROM = os.path.join("rom", "original.ngc")


def run(*args):
    print(">", " ".join(args))
    subprocess.run([sys.executable] + list(args), check=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))


if __name__ == "__main__":
    if not os.path.isdir("tools"):
        sys.exit("run this from the repository root")
    if len(sys.argv) > 1:
        os.makedirs("rom", exist_ok=True)
        shutil.copyfile(sys.argv[1], ROM)
    if not os.path.exists(ROM):
        sys.exit("put your ROM at rom/original.ngc, or pass its path")
    crc = zlib.crc32(open(ROM, "rb").read())
    if crc != CRC:
        sys.exit("rom/original.ngc has CRC32 %08X, expected %08X (Ganbare Neo Poke-kun, unmodified, 2 MB)" % (crc, CRC))
    os.makedirs("build", exist_ok=True); os.makedirs("review", exist_ok=True)
    run("tools/extract.py", ROM, "script/strings.json")
    run("tools/mklines.py")
    run("tools/review_fonts.py")
    run("tools/page_lines.py", "script/page.json", "review/lines.json")   # current English, widths, V.OFF grouping for the page
    print("setup done. Next: python tools/build.py")
