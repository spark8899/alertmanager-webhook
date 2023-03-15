# alertmanager-webhook
alertmanager's webhook send alert to qiye weixin and telegram.

# init
```shell
mkdir /opt/webhook && cd /opt/webhook
apt-get install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

copy main.py to /opt/webhook/main.py

change value for telbot_id, chat_id, wx_key.

# install webhook service
vim /etc/systemd/system/webhook.service
```
[Unit]
Description=webhook
After=network.target

[Service]
ExecStart=/opt/webhook/venv/bin/gunicorn -b 127.0.0.1:28081 -w 4 --error-logfile - --access-logfile - main:app
WorkingDirectory=/opt/webhook
StandardOutput=inherit
StandardError=inherit
Restart=always
User=alertmanager
StandardOutput=file:/opt/webhook/info.log
StandardError=file:/opt/webhook/info.log

[Install]
WantedBy=multi-user.target
```

start webhook service
```shell
systemctl daemon-reload
systemctl start webhook
systemctl enable webhook
```

# test
```
curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:28081/alertwebhook -d '{"text": "testtttt"}'
```

# alertmanager configure
vi /etc/alertmanager/alertmanager.yml
```
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'web.hook'
receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:28081/alertwebhook'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```