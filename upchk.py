#!/usr/bin/env python3

import subprocess
import smtplib
import ssl
import time

ping_targets=["minimoon.duckdns.org","fvpn.bbdo.ua"]
failed_hosts=[]
smtp_server="smtppro.zoho.eu"
smtp_port=587
smtp_login="alex@mooncloud.space"
smtp_password="F4qvD2xLwStr"
mail_from="mooncloud@mooncloud.space"
mail_to="alex@mooncloud.space"
mail_content=""
mail_subject="""\
    Subject: Failed ping targets


    """

timeout=300

def checkifup(host):
    command = ['ping', "-c", '5', "-w10", host]
    if subprocess.run(command).returncode == 0:
        return True
    else:
        return False

def sendmail():
    message = mail_subject+mail_content
    if smtp_port == 25:
        with smtplib.SMTP(smtp_server,smtp_port) as server:
            server.login(smtp_login, smtp_password)
            server.sendmail(mail_from, mail_to, message)
    elif smtp_port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_login, smtp_password)
            server.sendmail(mail_from, mail_to, message)
    elif smtp_port == 587:
        context = ssl.create_default_context()
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls(context=context)
            server.login(smtp_login, smtp_password)
            server.sendmail(mail_from, mail_to, message)
        except Exception as e:
            print(e)
        finally:
            server.quit()
    else:
        print("Not a valid smtp port!")

def upcheck():
    global mail_content
    global failed_hosts
    for i in ping_targets:
        if checkifup(i) == True:
            if failed_hosts.count(i) > 0:
                mail_content+=(f"{i} is online\n")
                failed_hosts.remove(i)
        else:
            if failed_hosts.count(i) == 0:
                mail_content+=(f"{i} is offline\n")
                failed_hosts.append(i)
    if mail_content:
            sendmail()
    mail_content=""

while (True):
    upcheck()
    time.sleep(timeout)
