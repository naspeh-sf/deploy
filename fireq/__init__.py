import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)
root = Path(__file__).resolve().parent.parent


def get_conf():
    path = root / os.environ.get('FIRE_CONFIG', 'config.json')
    if path.exists():
        conf = path.read_text()
        conf = json.loads(conf)
    else:
        conf = {}

    defaults = [
        ('debug', True),
        ('debug_aio', False),
        ('lxc_base', 'base-sd'),
        ('lxc_data', 'data-sd'),
        ('lxc_opts', '-B zfs'),
        ('domain', 'localhost'),
        ('logurl', lambda c: 'http://%s/' % c['domain']),
        ('e2e_chunks', 1),
        ('use_cpus', ''),
        ('no_statuses', True),
        ('url_prefix', ''),
        ('status_prefix', 'fire:'),

        ('github_auth', None),
        ('github_id', None),
        ('github_secret', None),
        ('github_orgs', ['superdesk']),
        ('github_callback', '/oauth_callback/github'),

        ('log_url', lambda c: 'http://%s/logs/' % c['domain']),
        ('log_root', '/tmp/fireq/logs'),
    ]
    for key, value in defaults:
        if callable(value):
            value = value(conf)
        conf.setdefault(key, value)

    # FIRE_UID is specified in web
    uid = os.environ.get('FIRE_UID')
    fmt = (
        '[%(asctime)s]{} %(levelname).3s %(message)s'
        .format(' [%s]' % uid if uid else '')
    )
    logging.basicConfig(
        level=logging.DEBUG if conf['debug'] else logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S %Z',
        format=fmt
    )
    return conf


conf = get_conf()


def pretty_json(obj):
    if isinstance(obj, bytes):
        obj = obj.decode()
    if isinstance(obj, str):
        obj = json.loads(obj)
    return json.dumps(obj, indent=2, sort_keys=True)


def get_restart_url(short_name, ref):
    # TODO: should use cli.Ref
    return (
        'https://{domain}{url_prefix}/{short_name}/{ref}/restart'
        .format(
            domain=conf['domain'],
            url_prefix=conf['url_prefix'],
            short_name=short_name,
            ref=ref
        )
    )
