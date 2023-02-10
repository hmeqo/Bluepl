# Bluepl

## Build

### Configure

Configure the config file like

```python
# configure.py

class Smtp:

    host = "smtp.email.com"
    port = 25
    sender = "123456789@email.com"
    password = "123456789"
```

Run the python file to configure

```bash
python configure.py
```

### Build web

Run this python file to build: `buildweb.py` (on root path)

```bash
python buildweb.py
```

That you can run the main file to use this application

## Build for Windows

Use pyinstaller

```bash
pyinstaller main_windows.py
```

## Run on server

You need the `uwsgi` package

### Run server

```bash
uwsgi --ini uwsgi.ini
```

### Stop server

```bash
uwsgi --stop uwsgi.pid
```

## TODO

- [ ] 前端 Session 过期时自动申请新的 Session
- [ ] 判断邮箱是否可用, 以及验证表单
