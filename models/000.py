""" A model to provide the basic globals. """
import appcfg
import rsyslog
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

if cfg.db:

    # DAL db connection.
    db = DAL(cfg.db['uri'], **cfg.db['args'])

    # Sessions in db. Require HTTPS.
    session.connect(request, response, db)
    session.secure()

    # Auth in db. Require HTTPS. Decouple auth from default controller.
    from gluon.tools import Auth
    auth = Auth(
        db, propagate_extension='', controller='auth',
        secure=(request.controller!='appadmin'),
        url_index=URL('default', 'index'))
    if cfg.auth:
        auth.define_tables(**cfg.auth['args'])
    else:
        auth.define_tables(signature=True)
    auth.settings.login_onfail.append(
            lambda form: log.warning('Login failure from %s' % request.client))

    # Scheduler in db.
    from gluon.scheduler import Scheduler
    if cfg.scheduler:
        scheduler = Scheduler(db, **cfg.scheduler['args'])
    else:
        scheduler = Scheduler(db)

if cfg.mail:

    # Mailer.
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.update(cfg.mail['settings'])

    # Auth mailer.
    if cfg.db:
        auth.settings.mailer = mail
