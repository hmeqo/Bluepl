import os

os.system('nuitka --standalone --windows-disable-console --windows-icon-from-ico="web/public/favicon.ico" --include-data-dir="resources=resources" --product-name="Bluepl" --file-version="0.0.1.0" --output-dir="output" --output-filename="Bluepl" main_windows.py')

os.rename("output/main_windows.dist", "output/Bluepl")
