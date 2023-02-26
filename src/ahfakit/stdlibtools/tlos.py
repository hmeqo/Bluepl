import os


def writable(path):
    try:
        os.chmod(path, os.stat(path).st_mode)
    except Exception:
        return False
    return True


def get_desktop_path():
    return os.path.expanduser("~\\Desktop")


def get_mount():
    """获取挂载点(暂时只支持windows)."""
    result = []
    if os.name == "nt":
        for name in os.popen("wmic logicaldisk get Name"):
            name = name.strip()
            if not name:
                continue
            if not name.endswith(os.sep):
                name += os.sep
            if os.path.exists(name):
                result.append(name)
    return result
