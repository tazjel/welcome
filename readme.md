A minimal app based on the default web2py welcome app.
The app fixes a few odd things the web2py project does and adds logging, app config, DAL connection, access control and event scheduling.
Changes track web2py stable.

Clone the repo and install it or symlink it into the `applications` folder of a set of web2py sources.
Define web2py routes. For 404, add:

    routes_onerror = [('init/404', '/init/error/page_not_found')]

The app provides a layout, but provides views only for auth and 404 pages.

The repo ignores files that aren't explicitly included in the repo.
Build on the app by developing a full app in a separate repo, then clone the app repo to the host and symlink models, views, controllers and other files into the scaffolding app repo, removing links that don't belong.

Provide app config in dict literals in the init app's `private` directory.
At minimum, define `db['uri']` and `db['args']` (`args` are used in the `DAL` constructor), and `mail['settings']` assigned to a mailer object.

In `private/db.cfg`:

    {
        'db': {
            'uri': 'postgres://web2py:web2py@localhost/web2py',
            'args': {
                'lazy_tables': True,
                'pool_size': 50
            }
        }
    }

In `private/mail.cfg`:

    {
        'mail': {
            'settings': {
                'server': 'smtp.example.com:465',
                'sender': 'Host Admin <postmaster@example.com>',
                'login': 'username:password',
                'ssl': True
            }
        }
    }

The app also uses `auth['args']` and `scheduler['args']` in `Auth` and `Scheduler` constructors, respectively.
