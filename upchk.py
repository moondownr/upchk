#!/usr/bin/env python3

import os
import subprocess
import smtplib
import ssl
import time
import sys
import platform
from dotenv import load_dotenv

load_dotenv()

# configure via .env file
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_login = os.getenv('SMTP_LOGIN')
smtp_password = os.getenv('SMTP_PASS')
mail_from = os.getenv('MAIL_FROM')
mail_to = os.getenv('MAIL_TO')

# configure here
ping_targets = ["google.com","1.1.1.1"]
failed_hosts = set()
mail_subject = """\
    Subject: Failed ping targets


    """
timeout = 300 #time between ping attempts, seconds

def checkifup(host):
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', '1', "-w5", host]
        return result.returncode == 0 and b'TTL=' in result.stdout
    else:
        command = ['ping', '-c', '1', "-w5", host]
        return subprocess.run(command).returncode == 0

def create_smtp_client(port):
    if port == 25:
        return smtplib.SMTP(smtp_server,smtp_port)
    if port == 465:
        return smtplib.SMTP_SSL(smtp_server, smtp_port, context=ssl.create_default_context())
    if port == 587:
        client = smtplib.SMTP(smtp_server, smtp_port)
        client.starttls(context=ssl.create_default_context())
        return client
    raise Exception(f"{port} invalid SMTP port!")

def send_message(message):
    if message:
        try:
            client = create_smtp_client(smtp_port)
            client.login(smtp_login, smtp_password)
            client.sendmail(mail_from, mail_to, mail_subject + message)
        except Exception as e:
            print(e, file=sys.stderr)
        finally:
            client.quit()

def get_status_message(targets):
    mail_content = ""
    for host in targets:
        # target host is offline
        if not checkifup(host):
            if not host in failed_hosts:
                mail_content += f"{host} is offline\n"
                failed_hosts.add(host)
        else:
            # target host went back online
            if host in failed_hosts:
                mail_content += f"{host} is online\n"
                failed_hosts.remove(host)
    return mail_content

def main():
    while (True):
        message = get_status_message(ping_targets)
        send_message(message)
        time.sleep(timeout)

if __name__ == '__main__':
    sys.exit(main())
