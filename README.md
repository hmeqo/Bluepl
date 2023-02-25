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

- [ ] ip访问限制
- [ ] 登录重试超次邮箱验证
- [ ] 判断邮箱是否可用
- [ ] 指定连接到某个服务器
- [ ] 上传拉取同步服务器数据
- [ ] 重置密码
