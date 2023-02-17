import os
from pathlib import Path
import shutil
from src import gconfig

dist_dir = Path("web")
webroot = gconfig.Dirs.webroot

os.chdir(dist_dir)
if not Path("node_modules").exists():
    os.system("npm install")
os.system("npm run build")
os.chdir("..")

if webroot.exists():
    shutil.rmtree(webroot)
shutil.move(str(dist_dir.joinpath("dist")), webroot)
