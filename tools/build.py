"""Build the English ROM: python tools/build.py [--fastunlock] [--ips]

  script/page.json -> build/tr_page.json         (tools/build_from_revised.py)
                   -> build/tr_page_icons.json   (tools/icon_drafts.py: profile icons, field padding)
                   -> build/neopoke_en.ngc        (tools/insert.py: text, VWF, fonts, graphics from gfx/*.png, icons)
  --fastunlock     -> build/neopoke_en_fastunlock.ngc (tools/fastunlock.py)
  --ips            -> build/patches/<name>.ips    (tools/make_ips.py)
Needs tools/setup.py to have run. Graphics: any gfx/<png> present is imported (make templates with tools/gfx_extract.py);
items without a PNG stay as in the ROM, except the title logo and menu icon text, which get draft lettering."""
import os, subprocess, sys


def run(*args):
    print(">", " ".join(args))
    subprocess.run([sys.executable] + list(args), check=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))


if __name__ == "__main__":
    if not os.path.exists("review/lines.json"):
        sys.exit("run python tools/setup.py first")
    run("tools/build_from_revised.py", "script/page.json", "build/tr_page.json")
    run("tools/icon_drafts.py", "build/tr_page.json", "build/tr_page_icons.json")
    run("tools/insert.py", "rom/original.ngc", "build/tr_page_icons.json", "build/neopoke_en.ngc")
    outs = ["build/neopoke_en.ngc"]
    if "--fastunlock" in sys.argv:
        run("tools/fastunlock.py", "build/neopoke_en.ngc", "build/neopoke_en_fastunlock.ngc")
        outs.append("build/neopoke_en_fastunlock.ngc")
    if "--ips" in sys.argv:
        os.makedirs("build/patches", exist_ok=True)
        for o in outs:
            run("tools/make_ips.py", o, "build/patches/" + os.path.basename(o)[:-4] + ".ips")
