import os
from pathlib import Path
import shutil
from src import gconfig

web_project_path = Path("web")
webroot = gconfig.Dirs.webroot

os.chdir(web_project_path)
if not Path("node_modules").exists():
    os.system("npm install")
os.system("npm run build")
os.chdir("..")

if webroot.exists():
    shutil.rmtree(webroot)
shutil.move(str(web_project_path.joinpath("dist")), webroot)
