""" A web2py module to provide app config from cache or dict literal files. """
import ast
import glob
import os
import rsyslog
from gluon import current


def get():
    """ Read a dict from cache.ram or from file in the app's private dir.

    Looks for data first in cache.ram, and returns that if it exists,
    otherwise loads dict literal data from private/*.cfg.

    Put {'debug': True} in a cfg file to decache cfg on every request.
    """

    def load():
        """ Load dict literal data from the current app's private dir. """
        cfg_data = {}
        cfg_dir = os.path.join(current.request.folder, 'private')
        for cfg_file in glob.glob(os.path.join(cfg_dir, '*.cfg')):
            try:
                with open(cfg_file) as cfg_fd:
                    new_data = ast.literal_eval(cfg_fd.read())
                cfg_data.update(new_data)
                msg = 'Loaded %s with keys %s'
                msg = msg % (os.path.basename(cfg_file), new_data.keys())
                rsyslog.get().info(msg)
            except:
                msg = 'Error loading %s' % os.path.basename(cfg_path)
                rsyslog.get().exception(msg)
        return cfg_data

    cfg = current.cache.ram('cfg', lambda: load(), None)
    if cfg.get('debug'):
        current.cache.ram('cfg', None)
        rsyslog.get().info('Decached cfg data for debug')
    return cfg
