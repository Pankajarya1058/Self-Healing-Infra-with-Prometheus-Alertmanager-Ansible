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
Our service (Nginx) is running on localhost and API (which is created by using Flask) will automatically run the Ansible playbook. After triggering the webhook through alertManager and Prometheus.


