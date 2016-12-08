""" A script to finalize app deployment.

Run it in a web2py shell in full app context, including models:

    sudo -u www-data -g www-data python /usr/local/web2py/web2py.py \
        -S init -M -R /usr/local/web2py/applications/init/private/deploy.py \
        -A example.com anApp postmaster@example.com

Fixes stuff and sends an email to an address. Expects sys.argv:

    1. Hostname.
    2. Name of the deployed app.
    3. Email address of the server admin.
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

def _init_server_admin():
    """ Initialize the server admin. Allow only a single server admin account,
    the one associated with the target email address. Register a new user if
    an account for the email address doesn't yet exist. """
    found = False
    admin_group_id = auth.id_group(cfg.groups.server_admin)
    qry = auth.table_membership().group_id==admin_group_id
    for member in db(qry).select():
        if member.user_id.email==admin_addr:
            found = True
        else:
            auth.del_membership(self, admin_group_id, member.user_id)
            log.info('Removed %s as server admin', member.user_id.email)
    if not found:
        user = auth.table_user()(email=admin_addr)
        if not user:
            user = auth.register_bare(email=admin_addr)
            log.info('Registered %s as server admin', admin_addr)
        auth.add_membership(admin_group_id, user.id)
        log.info('Added %s as server admin', admin_addr)

def _send_update_report():
    """ Email the server admin that an update/install is complete. """
    subject = '%s deployment complete on %s' % (appname, hostname)
    summary = 'Deployment of %s on %s finished %s %s.'
    now = datetime.datetime.now().strftime('on %b %d %Y at %H:%M:%S')
    tz = time.strftime("%Z")
    message = summary % (appname, hostname, now, tz)
    mail.send(to=[admin_addr], subject=subject, message=message)

try:
    hostname = sys.argv[1]
    appname = sys.argv[2]
    admin_addr = sys.argv[3]
    _fix_scheduler()
    _init_server_admin()
    _send_update_report()
    log.info('Deployment complete for %s', sys.argv[1:])
except:
    log.exception('Error finalizing deployment')
