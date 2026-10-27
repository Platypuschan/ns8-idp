"""Keep the internal Keycloak admin API off the public host route."""
import os
import agent

def restrict_admin(host, lets_encrypt=False):
    agent.set_route({
        'instance': os.environ['MODULE_ID'] + '-admin',
        'url': 'http://127.0.0.1:' + os.environ['TCP_PORT'],
        'host': host, 'path': '/admin', 'ip_allowlist': ['127.0.0.1/32', '::1/128'],
        'http2https': True, 'lets_encrypt': lets_encrypt,
    })
