# Bluepl

## Build

Make a sender.py file on /src/email/, contents like

```python
# /src/email/sender.py
host = "smtp.email.com"
port = 25
sender = "123456789@email.com"
password = "123456789"
```

cd and run command on Bluple-web

```bash
python build.py
```

## Run

run on main directory

```bash
python main_windows.py
```

## TODO

- [ ] 完善前后端 Account 交互部分
- [ ] 前端 Session 过期时自动申请新的 Session
- [ ] 判断邮箱是否可用, 以及验证表单
