"""Module settings of configure-module, stored in the module environment.

They switch site policies, not fixes: an unset value means the default of
this module, and an omitted request field keeps the current value.
"""
import os

DEFAULTS = {
    # Allow the Keycloak admin console from the node only
    'restrict_admin_console': False,
    # Ignore local Keycloak group memberships; client access policies need it.
    # It has no effect on a writable federation, which LDAP_ONLY would write to
    'directory_groups_only': False,
    # Lead the host root to the account console instead of the admin console
    'account_home_redirect': False,
    # Accept only exact HTTPS or native client endpoints
    'strict_client_uris': False,
}


def env_name(name):
    return 'IDP_' + name.upper()


def get(name, request=None):
    if request is not None and name in request:
        return bool(request[name])
    value = os.getenv(env_name(name), '')
    return DEFAULTS[name] if value == '' else value == '1'


def current(request=None):
    return {name: get(name, request) for name in DEFAULTS}
