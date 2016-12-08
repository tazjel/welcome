""" A model to provide the basic globals. """
import appcfg
import rsyslog
from gluon.tools import Auth
from gluon.tools import Mail
from gluon.scheduler import Scheduler
from gluon.storage import Storage


def auth_buttons(form):
    if request.args(0) == 'login':
        if 'register' not in auth.settings.actions_disabled:
            url_vars = None
            if request.vars._next:
                url_vars = {'_next': request.vars._next}
            url = URL(args='register', vars=url_vars)
            form.add_button(T('Sign Up'), url, _class='btn btn-default')
        if 'request_reset_password' not in auth.settings.actions_disabled:
            url = URL(args='request_reset_password')
            form.add_button(T('Lost Password'), url, _class='btn btn-default')

def auth_navbar():
    """  Return auth navbar with orphaned link at top level. """

    # Navbar might have been defined elsewhere
    if 'navbar' in globals():
        navbar = globals()['navbar']
    else:
        navbar = auth.navbar(mode='dropdown')

    # Fix orphaned link.
    menu = navbar.element('.dropdown-menu')
    if menu:
       links = menu.elements('a')
       if len(links) == 1:
           navbar = LI(links[0], _class='dropdown')
    return navbar

def auth_title():
    if request.args(0) == 'register':
        return T('Sign Up')
    if request.args(0) == 'login':
        return T('Log In')
    if request.args(0):
        return T(request.args(0).replace('_',' ').title())
    return ''

T.is_writable = False # No language file updates.
log = rsyslog.get()
cfg = Storage(appcfg.get())

# DAL db connection.
db = DAL(cfg.db['uri'], **cfg.db['args'])

# Sessions in db. Require HTTPS.
session.connect(request, response, db)
session.secure()

# Auth in db. Require HTTPS. Decouple auth from default controller.
auth = Auth(
    db, propagate_extension='', controller='auth',
    secure=True, url_index=URL('default', 'index'))
if cfg.auth and 'args' in cfg.auth:
    auth.define_tables(**cfg.auth['args'])
else:
    auth.define_tables(signature=True)
auth.settings.login_onfail.append(
    lambda form: log.warning('Login failure from %s' % request.client))
if 'disabled' in cfg.auth:
    for action in cfg.auth['disabled']:
        auth.settings.actions_disabled.append(action)

# Init cfg.groups. Add server admin group.
cfg.groups = Storage()
cfg.groups.server_admin = 'server admin'
if not auth.id_group(cfg.groups.server_admin):
    auth.add_group(cfg.groups.server_admin, 'Server Administrator')
    log.info('Added server admin role')

# Scheduler in db.
if cfg.scheduler and 'args' in cfg.scheduler:
    scheduler = Scheduler(db, **cfg.scheduler['args'])
else:
    scheduler = Scheduler(db)

# Mailer.
mail = Mail()
mail.settings.update(cfg.mail['settings'])
auth.settings.mailer = mail
