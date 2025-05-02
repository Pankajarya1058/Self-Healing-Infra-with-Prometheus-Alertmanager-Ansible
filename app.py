from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print("Received webhook data:", data)  # Log incoming data
    if data and 'alerts' in data:
        for alert in data['alerts']:
            if alert['status'] == 'firing':
                print("Alert firing:", alert['labels']['alertname'])  # Log which alert is firing
                os.system('ansible-playbook /home/pankajarya/Projects/restart_nginx.yml')
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

