import os

from flask import Flask, render_template, send_file, send_from_directory, abort

from .. import gconfig

app = Flask(
    __name__,
    template_folder=str(gconfig.Dirs.webroot),
    root_path=str(gconfig.Dirs.root),
)
app.config["JSON_AS_ASCII"] = False


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/<path:name>")
def anyurl(name: str):
    # 发送静态文件
    response = send_from_directory(gconfig.Dirs.webroot, name)
    # 如果是 js 文件, 则更改 Content-Type
    if name.endswith(".js"):
        response.headers["Content-Type"] = "text/javascript;charset=utf-8"
    return response


@app.route("/favicon.ico")
def favicon():
    return send_file(gconfig.Files.icon)


@app.route("/session", methods=["GET", "POST"])
def session():
    """创建会话"""
    pass
