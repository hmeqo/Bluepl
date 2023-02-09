import os
from pathlib import Path
import shutil
from src import gconfig

dist_dir = Path("Bluepl-web")
webroot = gconfig.Dirs.webroot

os.chdir(dist_dir)
os.system("npm run build")
os.chdir("..")

if webroot.exists():
    shutil.rmtree(webroot)
shutil.move(str(dist_dir.joinpath("dist")), webroot)
