# Self-Healing-Infra-with-Prometheus-Alertmanager-Ansible

## Overview
Objective of this repository is to automatically detect service failures, get the alerts and recover using automation.

## Tools
- [Prometheus](https://prometheus.io/download/#prometheus) 
- [Alertmanager](https://prometheus.io/download/#alertmanager)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pipx-install)
- [Python](https://www.python.org/downloads/source/)
- [Nginx](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/)

### Mini Guide of this Project
Our service ([Nginx](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/)) is running on localhost and API (which is created by using [Flask](https://flask.palletsprojects.com/en/stable/installation/#install-flask)) will automatically run the [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pipx-install) playbook to restart the service. After triggering the webhook through [Alertmanager](https://prometheus.io/download/#alertmanager) and [Prometheus](https://prometheus.io/download/#prometheus).

## Getting Started
**Note: -** You can perform this task on your local machine and any cloud platforms (AWS, Azure, GCP, etc.) we will perform this task in AWS. 

**1. Install required packages**
```
sudo apt-get update
sudo apt-get -y install nginx ansible-core prometheus prometheus-alertmanger 
``` 
**2. Configure prometheus**

###### vim /etc/prometheus/prometheus.yml
```
# Sample config for Prometheus.

global:
  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

  # Attach these labels to any time series or alerts when communicating with
  # external systems (federation, remote storage, Alertmanager).
  external_labels:
      monitor: 'example'

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets: ['localhost:9093']

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
   - "rules/rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s
    scrape_timeout: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'nginx-http'
    metrics_path: /probe
    params:
      module: [http_2xx]  # HTTP GET request expecting a 2xx status

    static_configs:
      - targets:
        - http://localhost  # Change to http://yourdomain.com if needed

    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115  # Blackbox Exporter address
```

**3. Configure alertmanager**
###### vim /etc/alertmanager/alertmanger.yml
```
global:
  resolve_timeout: 1m

route:
  receiver: 'webhook'
  group_wait: 10s
  group_interval: 30s
  repeat_interval: 1m

receivers:
  - name: 'webhook'
    webhook_configs:
      - url: 'http://localhost:5001/'

```

**4. Creating rules file**
###### vim /etc/prometheus/rules/rules.yml

```
groups:
  - name: nginx
    rules:
      - alert: NginxDown
        expr: probe_success{job="nginx-http"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "NGINX is down"
          description: "The NGINX server is not responding to HTTP requests."

```

**5. Create API**
###### vim ~/app.py
```
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
                os.system('ansible-playbook restart_nginx.yml')
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**6. Create Ansible playbook**

###### vim ~/restart_nginx.yml
```
- name: Restart NGINX Service
  hosts: localhost
  become: yes
  tasks:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

**7. Now, Restart services**
```
sudo systemctl restart prometheus alertmanager 
```

**8. Run app.py**

```
python3 app.py
```

## Now, We will test above task

#### Access Prometheus
```
http://<server-ip>:9090
```

#### Stop the Nginx service
```
sudo systemctl stop nginx
```

After Stopping Nginx service, alertmanager get the "NginxDown" alert, we can see in Prometheus dashboard...

After detects "NginxDown" alert, webHook will trigger and app.py will run the Ansible Playbook which will restart the Nginx service.




