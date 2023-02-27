# Bluepl

## Build

### Configure

Run the command to initialize this project, will be add settings file

```bash
python manage.py --init
```

Configure the settings file like

```python
# src/settings.py

class Smtp:
    host = "smtp.email.com"
    port = 25
    sender = "123456789@email.com"
    password = "123456789"
...
```

### Build web

```bash
python manage.py --build-web
```

That you can run the main file to use this application

### Build for Windows

Use Nuitka, if you do not have this package, run `pip install nuitka`

```bash
python manage.py --build-windows
```

### Build setup file

Use Inno Setup, if you do not have installed InnoSetup, please install this from <https://jrsoftware.org/isinfo.php>

```bash
python manage.py --build-setup
```

## Run on server

You need the `uwsgi` package

### Run server

```bash
python manage.py --run-server
```

### Stop server

```bash
python manage.py --stop-server
```

## TODO

- [ ] ip访问限制
- [ ] 登录重试超次邮箱验证
- [ ] 判断邮箱是否可用
- [ ] 指定连接到某个服务器
- [ ] 上传拉取同步服务器数据
- [x] 重置密码
