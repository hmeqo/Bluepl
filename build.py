import sys
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--web", action="store_true")
argparser.add_argument("--pyinstaller", action="store_true")
argparser.add_argument("--nuitka", action="store_true")
argparser.add_argument("--configure", action="store_true")


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
    from pathlib import Path

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
    import os
    from pathlib import Path
    import shutil
    from src.gconfig import Dirs

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
    import os
    from src.gconfig import AppCfg, Dirs, Files

    os.system(
        f'pyinstaller --noconfirm --onedir --windowed --icon "{Files.icon}" --name "{AppCfg.name}" --add-data "./{Dirs.resources};{Dirs.resources}/"  main_windows.py')


def build_windows_with_nuitka():
    import os
    from src.gconfig import AppCfg, Dirs, Files

    dist = "dist"
    os.system(
        f'nuitka --standalone --windows-disable-console --windows-icon-from-ico="{Files.icon}" --include-data-dir="{Dirs.resources}={Dirs.resources}" --product-name="{AppCfg.name}" --file-version="0.0.1.0" --output-dir="{dist}" --output-filename="{AppCfg.name}" main_windows.py')
    os.rename(f"{dist}/main_windows.dist", f"{dist}/{AppCfg.name}")


def main():
    argv = sys.argv[1:]
    if not argv:
        argparser.print_usage()
        return None
    args = argparser.parse_args(argv)
    if args.configure:
        configure()
    if args.web:
        build_web()
    if args.pyinstaller:
        build_windows_with_pyinstaller()
    elif args.nuitka:
        build_windows_with_nuitka()
    return None


if __name__ == "__main__":
    main()
