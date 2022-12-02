#!/usr/bin/env python3

import os
import subprocess
import smtplib
import ssl
import time
from dotenv import load_dotenv

load_dotenv()

# configure via .env file
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
smtp_login = os.getenv('SMTP_LOGIN')
smtp_password = os.getenv('SMTP_PASS')
mail_from = os.getenv('MAIL_FROM')
mail_to = os.getenv('MAIL_TO')

# configure here
ping_targets = ["google.com","1.1.1.1"]
mail_subject = """\
    Subject: Failed ping targets


    """
timeout = 300 #time between ping attempts, seconds

# leave empty
mail_content = ""
failed_hosts = []

def checkifup(host):
    command = ['ping', "-c", '1', "-w5", host]
    if subprocess.run(command).returncode == 0:
        return True
    else:
        return False

def sendmail():
    message = mail_subject+mail_content
    if smtp_port == 25:
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.login(smtp_login, smtp_password)
            server.sendmail(mail_from, mail_to, message)
            server.quit()
        except Exception as e:
            print(e)
        finally:
            server.quit()
    elif smtp_port == 465:
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(smtp_login, smtp_password)
                server.sendmail(mail_from, mail_to, message)
                server.quit()
        except Exception as e:
            print(e)
        finally:
            server.quit()
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
