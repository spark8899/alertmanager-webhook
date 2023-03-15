#!/opt/webhook/venv/bin/python3
from flask import Flask, request, jsonify
import time, json
import logging, requests
from logging.handlers import RotatingFileHandler
from logging import Formatter

app = Flask(__name__)
telbot_id = 'xxxx'
chat_id = '-xxx'
wx_key = 'xxxx'
localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
log_path = '/opt/webhook/debug.log'

def send_tel(telbot_id, chat_id, text, parse_mode):
    url = "https://api.telegram.org/%s/sendMessage" % telbot_id
    content = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    req = requests.post(url, content)
    if req.json()['ok']:
        print("send is ok.")
    else:
        print("send is error.")

def send_wx(wx_key, text):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s' % wx_key
    content = {"msgtype" : "markdown", "markdown": {"content": "test" } }
    content["markdown"]["content"] = text
    data = json.dumps(content)
    requests.post(url, data)

@app.route('/')
def home():
    app.logger.warning("client: %s, path: /" % request.remote_addr)
    return "<p>Hello, World!</p>"

@app.route('/alertwebhook', methods=["POST"])
def alertwebhook():
    data = request.get_json()
    if not data:
        app.logger.warning("client: %s, data is null " % request.remote_addr)
        return jsonify({"code": 400, "msg": "data is null"}), 400
    elif "alerts" in data:
        for alert in data['alerts']:
            alertname = alert['labels']['alertname']
            status = alert['status']
            severity = alert['labels']['severity']
            startsAt = alert['startsAt']
            body = "alertname: %s\nstatus: %s\nseverity: %s\nstartsAt: %s" % (alertname, status, severity, startsAt)
            if status == 'resolved':
                endsAt = alert['endsAt']
                body = "%s\nendsAt: %s" % (body, endsAt)
            if 'instance' in alert['labels']:
                instance =  alert['labels']['instance']
                body = "%s\ninstance: %s" % (body, instance)
            if 'description' in alert['annotations']:
                description = alert['annotations']['description']
                body = "%s\ndescription: %s" % (body, description)
            generatorURL = alert['generatorURL']
            body = "%s\ngeneratorURL: %s" % (body, generatorURL)
            #send_tel(telbot_id, chat_id, body, "markdown")
            send_wx(wx_key, body)
            #app.logger.warning("alert: %s" % alert)
            #app.logger.warning("body: %s" % body)
    return jsonify(data)

if __name__ == '__main__':
    log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    handler = RotatingFileHandler(log_path, maxBytes=10000, backupCount=5)
    handler.setFormatter(Formatter(log_format))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='127.0.0.1', port=28081)