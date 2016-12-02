""" A script to finalize app deployment.

Run it in a web2py shell in full app context, including models:

    sudo -u www-data -g www-data python /usr/local/web2py/web2py.py \
        -S init -M -R /usr/local/web2py/applications/init/private/deploy.py \
        -A example.com postmaster@example.com anApp \
        xxxxxTYYYY-MM-DD xxxxxTYYYY-MM-DD xxxxxTYYYY-MM-DD

Fixes stuff and sends an email to a single address. Expects sys.argv:

    1. Hostname.
    2. Name of the deployed app.
    3. Email address to receive notification message.
    4. Playbook repo version and timestamp.
    5. Web framework repo version and timestamp.
    6. Host app repo version and timestamp.
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

def _send_email(hostname, appname, notify_addr, versions):
    subject = '%s deployment complete on %s' % (appname, hostname)
    summary = 'Deployment of %s on %s finished %s %s.'
    now = datetime.datetime.now().strftime('on %b %d %Y at %H:%M:%S')
    tz = time.strftime("%Z")
    summary = P(summary % (appname, hostname, now, tz))
    table = TABLE(
        TR(TD('Playbook'), TD(versions['playbook'])),
        TR(TD('Framework'), TD(versions['framework'])),
        TR(TD(appname, TD(versions['app']))))
    message = '<html>%s</html>' % DIV(summary, table).xml()
    mail.send(to=[notify_addr], subject=subject, message=message)

def deploy():

    def version(data):
        commit, date = data.split('T')
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        return '%s %s' % (commit, date.strftime('%b %d %Y'))

    hostname = sys.argv[1]
    appname = sys.argv[2]
    notify_addr = sys.argv[3]
    versions = {
        'playbook': version(sys.argv[4]),
        'framework': version(sys.argv[5]),
        'app': version(sys.argv[6])}
    _fix_scheduler()
    _send_email(hostname, appname, notify_addr, versions)
    log.info('Deployment finalized and %s notified' % notify_addr)

try:
    deploy()
except:
    log.exception('Error finalizing deployment')
