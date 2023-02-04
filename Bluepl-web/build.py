import os
import shutil

os.system("npm run build")

shutil.rmtree("../src/web")
shutil.move("./dist", "../src/web")
