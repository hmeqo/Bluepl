import sys
import os
import shutil
from pathlib import Path
import argparse

from src.gconfig import AppConfig, Dirs, Files, versioninfo

argparser = argparse.ArgumentParser()

apg_configure = argparser.add_argument_group(title="Initialization")
apg_configure.add_argument("--init", action="store_true")

apg_build = argparser.add_argument_group(title="Build and distribute")
apg_build.add_argument("--build-web", action="store_true")
apg_build.add_argument("--build-nuitka", action="store_true")
apg_build.add_argument("--build-pyinstaller", action="store_true")
apg_build.add_argument("--build-setup", action="store_true")
apg_build.add_argument('--debug', action='store_true')

apg_server = argparser.add_argument_group(title="Run on server")
apg_server.add_argument("--run-server", action="store_true")
apg_server.add_argument("--stop-server", action="store_true")

apg_dev = argparser.add_argument_group(title='development')
apg_dev.add_argument('--run-dev', action='store_true')

client_project_path = Path("client")
distdir = Path('dist')
distpath = distdir.joinpath(AppConfig.name)


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


def init():
    global Smtp, Socket
    import inspect

    settings_path = Path("src/settings.py")
    code = "\n\n".join(inspect.getsource(i) for i in (Smtp, Socket))
    ask_text = f"{settings_path} is exists, do you want override? (Y/N): "
    if settings_path.exists() and input(ask_text).lower() != "y":
        return None
    settings_path.write_text(code)
    print(f"{settings_path} generated")
    return None


def build_web():
    os.chdir(client_project_path)
    if not Path("node_modules").exists():
        os.system("npm install")
    os.system("npm run build")
    os.chdir("..")

    if Dirs.webroot.exists():
        shutil.rmtree(Dirs.webroot)
    shutil.move(client_project_path.joinpath("dist"), Dirs.webroot)


def build_windows_with_pyinstaller(debug=False):
    debug_param = '' if debug else '--windowed'
    os.system(
        f'pyinstaller {debug_param} --noconfirm --onedir --icon "{Files.icon}" --name "{AppConfig.name}" --add-data "./{Dirs.resources};{Dirs.resources}/"  main_windows.py')


def build_windows_with_nuitka(debug=False):
    debug_param = '' if debug else '--windows-disable-console'
    if distpath.exists():
        shutil.rmtree(distpath)
    os.system(
        f'nuitka {debug_param} --standalone --windows-icon-from-ico="{Files.icon}" --product-name="{AppConfig.name}" --file-version="{versioninfo.full_version}" --noinclude-default-mode="error" --include-data-dir="{Dirs.resources}={Dirs.resources}" --output-dir="{distdir}" --output-filename="{AppConfig.name}" main_windows.py')
    path = Path(f"{distdir}/main_windows.dist")
    if path.exists():
        path.rename(distpath)


def build_setup():
    os.system(f'ISCC setup.iss')


def run_server():
    if not Path("uwsgi.pid").exists():
        os.system("nohup uwsgi --ini uwsgi.ini &")


def stop_server():
    os.system("uwsgi --stop uwsgi.pid")


def run_dev():
    os.chdir(client_project_path)
    os.system('npm run dev')
    os.chdir('..')


def main():
    argv = sys.argv[1:]
    if not argv:
        argparser.print_usage()
        return None
    args = argparser.parse_args(argv)
    if args.init:
        init()

    if args.build_web:
        build_web()
    if args.build_nuitka:
        build_windows_with_nuitka(args.debug)
    elif args.build_pyinstaller:
        build_windows_with_pyinstaller(args.debug)
    if args.build_setup:
        build_setup()

    if args.run_server:
        run_server()
    if args.stop_server:
        stop_server()
    if args.run_dev:
        run_dev()
    return None


if __name__ == "__main__":
    main()
