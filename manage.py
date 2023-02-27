import sys
import os
import shutil
from pathlib import Path
import argparse

from src.gconfig import AppCfg, Dirs, Files

argparser = argparse.ArgumentParser()

apg_configure = argparser.add_argument_group(title="Configure")
apg_configure.add_argument("--configure", action="store_true")

apg_build = argparser.add_argument_group(title="Build and distribute")
apg_build.add_argument("--build-web", action="store_true")
apg_build.add_argument("--build-nuitka", action="store_true")
apg_build.add_argument("--build-pyinstaller", action="store_true")
apg_build.add_argument("--build-setup", action="store_true")

apg_server = argparser.add_argument_group(title="Run on server")
apg_server.add_argument("--run-server", action="store_true")
apg_server.add_argument("--stop-server", action="store_true")


class Smtp:
    # Email services provider host url
    host = ""
    # Port
    port = 0
    # Sender email
    sender = ""
    # Smtp password
    password = ""


class Socket:
    # This program use dynamic ip or static ip, if is server, recommended True
    static_ip = False


def configure():
    global Smtp, Socket
    import inspect

    config_path = Path("config.py")
    config_is_exists = config_path.exists()
    if config_is_exists:
        from config import Smtp, Socket  # type: ignore
    code = "".join(inspect.getsource(i) for i in (Smtp, Socket))
    if config_is_exists:
        dist_path = Path("src/gconfig/config.py")
        dist_path.write_text(code)
        print(f"Config saved on {dist_path}")
    else:
        config_path.write_text(code)
        print(f"config.py generated")


def build_web():
    web_project_path = Path("web")
    webroot = Dirs.webroot

    os.chdir(web_project_path)
    if not Path("node_modules").exists():
        os.system("npm install")
    os.system("npm run build")
    os.chdir("..")

    if webroot.exists():
        shutil.rmtree(webroot)
    shutil.move(str(web_project_path.joinpath("dist")), webroot)


def build_windows_with_pyinstaller():
    os.system(
        f'pyinstaller --noconfirm --onedir --windowed --icon "{Files.icon}" --name "{AppCfg.name}" --add-data "./{Dirs.resources};{Dirs.resources}/"  main_windows.py')


def build_windows_with_nuitka():
    distdir = "dist"
    distpath = f"{distdir}/{AppCfg.name}"
    if os.path.exists(distpath):
        shutil.rmtree(distpath)
    os.system(
        f'nuitka --standalone --windows-disable-console --windows-icon-from-ico="{Files.icon}" --include-data-dir="{Dirs.resources}={Dirs.resources}" --product-name="{AppCfg.name}" --file-version="0.0.1.0" --output-dir="{distdir}" --output-filename="{AppCfg.name}" main_windows.py')
    os.rename(f"{distdir}/main_windows.dist", distpath)


def build_setup():
    os.system(f'ISCC setup.iss')


def run_server():
    if not Path("uwsgi.pid").exists():
        os.system("nohup uwsgi --ini uwsgi.ini &")


def stop_server():
    os.system("uwsgi --stop uwsgi.pid")


def main():
    argv = sys.argv[1:]
    if not argv:
        argparser.print_usage()
        return None
    args = argparser.parse_args(argv)
    if args.configure:
        configure()
    if args.build_web:
        build_web()
    if args.build_nuitka:
        build_windows_with_nuitka()
    elif args.build_pyinstaller:
        build_windows_with_pyinstaller()
    if args.build_setup:
        build_setup()
    if args.run_server:
        run_server()
    if args.stop_server:
        stop_server()
    return None


if __name__ == "__main__":
    main()
