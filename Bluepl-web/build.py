import os
from pathlib import Path
import shutil

os.system("npm run build")

webpath = Path("../src/web")
if webpath.exists():
    shutil.rmtree(webpath)
shutil.move("./dist", webpath)
