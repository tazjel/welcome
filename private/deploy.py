""" A script to finalize app deployment.

Run it in a web2py shell in full app context, including models:

    sudo -u www-data -g www-data python /usr/local/web2py/web2py.py \
        -S init -M -R /usr/local/web2py/applications/init/private/deploy.py \
        -A example.com anApp postmaster@example.com

Fixes stuff and sends an email to an address. Expects sys.argv:

    1. Hostname.
    2. Name of the deployed app.
    3. Email address to receive notification message.
"""
import datetime
import sys
import time


def _fix_scheduler():
    """ Fixes 2.14.6 scheduler heartbeat exception. """
    db.scheduler_task.fields()
    db.scheduler_run.fields()
    db.scheduler_worker.fields()
    db.scheduler_task_deps.fields()

def _send_email():
    subject = '%s deployment complete on %s' % (appname, hostname)
    summary = 'Deployment of %s on %s finished %s %s.'
    now = datetime.datetime.now().strftime('on %b %d %Y at %H:%M:%S')
    tz = time.strftime("%Z")
    message = summary % (appname, hostname, now, tz)
    mail.send(to=[notify_addr], subject=subject, message=message)

try:
    hostname = sys.argv[1]
    appname = sys.argv[2]
    notify_addr = sys.argv[3]
    _fix_scheduler()
    _send_email()
    log.info('Deployment finalized and %s notified' % notify_addr)
except:
    log.exception('Error finalizing deployment')
