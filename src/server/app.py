from flask import Flask
from .. import gconfig

app = Flask(
    __name__,
    template_folder=str(gconfig.Dirs.webroot),
    root_path=str(gconfig.Dirs.root),
)
app.config["JSON_AS_ASCII"] = False
