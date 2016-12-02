""" Provide rsyslog.local0 from Python.

Rsyslog config in /etc/rsyslog.d/ should look something like:

    $FileOwner {{ app_user }}
    $FileGroup {{ app_group }}
    $template {{ logger_name }},"{{ log_format_string }}"
    local0.info {{ log_dir }}/messages;{{ logger_name }}
    #local0.* {{ log_dir }}/debug;{{ logger_name }}
    & ~
"""
import logging
import logging.handlers


def get(name='rsyslog'):
    """ Return a named rsyslog local0 facility logger. """
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        import inspect
        import os

        # Prep rsyslog handler.
        logger.setLevel(logging.DEBUG)
        local0 = logging.handlers.SysLogHandler(
            address='/dev/log', facility='local0')
        local0.setLevel(logging.DEBUG)
        caller = inspect.stack()[-1]
        if os.path.isfile(caller[1]):
            caller = os.path.basename(caller[1])

        # Add the handler.
        if len(logger.handlers) == 0:
            logger.addHandler(local0)
            info = 'Logger %s %s local0 handler added by %s'
            logger.info(info, name, id(logger), caller)
        else:
            warning = 'Logger %s %s local0 race condition blocked from %s'
            logger.warning(warning, name, id(logger), caller)
    return logger
