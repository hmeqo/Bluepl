from flask import Flask
from ..gconfig import Dirs

app = Flask(
    __name__,
    template_folder=str(Dirs.webroot),
    root_path=str(Dirs.root),
)
app.config["JSON_AS_ASCII"] = False
