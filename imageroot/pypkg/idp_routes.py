"""Keep the internal Keycloak admin API off the public host route."""
import os
import copy
import time
import agent
import idpcert

def restrict_admin(host, lets_encrypt=False):
    agent.set_route({
        'instance': os.environ['MODULE_ID'] + '-admin',
        'url': 'http://127.0.0.1:' + os.environ['TCP_PORT'],
        'host': host, 'path': '/admin', 'ip_allowlist': ['127.0.0.1/32', '::1/128'],
        'http2https': True, 'lets_encrypt': lets_encrypt,
    })


def certificate_transport(value, host=None, lets_encrypt=None):
    """Require an acknowledged Traefik capability, never trust ignored input.

    Both routers for the hostname must use the same TLS options; otherwise
    Traefik falls back to default options because TLS precedes path routing.
    """
    host = host or os.environ['IDP_HOSTNAME']
    original = []
    try:
        original = [(os.environ['MODULE_ID'] + suffix,
                     agent.get_route(os.environ['MODULE_ID'] + suffix))
                    for suffix in ('', '-admin')]
        for index, (instance, old) in enumerate(original):
            route = copy.deepcopy(old)
            route.update(instance=instance, host=host,
                         url='http://127.0.0.1:' + os.environ['TCP_PORT'],
                         http2https=True, client_certificates=value)
            if lets_encrypt is not None:
                route['lets_encrypt'] = lets_encrypt
            if index:
                route.update(path='/admin', ip_allowlist=['127.0.0.1/32', '::1/128'])
            headers = route.setdefault('headers', {}).setdefault('request', {})
            headers[idpcert.HEADER] = ''
            headers['X-Forwarded-Tls-Client-Cert-Info'] = ''
            headers[idpcert.PROOF_HEADER] = idpcert.proxy_secret() if value else ''
            agent.set_route(route)
        if value:
            # SNI precedes HTTP routing. While only one router has changed,
            # Traefik resolves conflicting TLS options to its defaults. Apply
            # both first, then check their effective capability together.
            deadline = time.monotonic() + 10
            while not all(agent.get_route(instance).get('client_certificates') is True
                          for instance, _ in original):
                if time.monotonic() >= deadline:
                    raise idpcert.CertificateError('traefik_certificate_support_required')
                time.sleep(.2)
    except Exception:
        for instance, old in reversed(original):
            if old:
                agent.set_route({**old, 'instance': instance,
                                 'headers': old.get('headers', {}),
                                 'client_certificates': old.get('client_certificates', False)})
        raise
