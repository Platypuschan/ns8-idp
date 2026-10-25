#
# Copyright (C) 2026 Nethesis S.r.l.
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Removal of the federated identity providers of earlier versions.

Version 0.1.0-rc.1, like upstream ns8-idp, could federate a realm with
an external IdP, like Microsoft Entra ID: the realm then had NS8 copies
of the login flows, a writable LDAP federation bound as a service
account of the module, and the federated IdPs. This module no longer
supports external IdPs: the realm gets the built-in flows and the
read-only LDAP federation back, and the service account is removed from
the user domain. Accounts created in LDAP by federated logins stay in
the user domain, without a password.
"""

import json
import os
import sys
import urllib.parse

import agent
import agent.tasks
import cluster.userdomains

# Secrets of the federation, by user domain: the service account and the
# federated IdP credentials
SECRETS_FILE = "federation.json"

MAPPER_TYPE = "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
STORAGE_TYPE = "org.keycloak.storage.UserStorageProvider"
# Login flows created for federated IdPs
FLOWS = ("ns8 browser", "ns8 direct grant", "ns8 first broker login", "ns8 deny direct grant")
FIRST_BROKER_LOGIN_FLOW = "ns8 first broker login"
# LDAP mappers that only a writable federation needs
WRITABLE_MAPPERS = ("cn", "no password change at creation", "ns8_idp", "ns8_idp_id")

def _path(name):
    return urllib.parse.quote(name, safe="")

def _load_secrets():
    try:
        with open(SECRETS_FILE) as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}

def _save_secrets(data):
    if not data:
        try:
            os.unlink(SECRETS_FILE)
        except FileNotFoundError:
            pass
        return
    old_umask = os.umask(0o077)
    try:
        with agent.safe_open(SECRETS_FILE) as fp:
            json.dump(data, fp)
    finally:
        os.umask(old_umask)

def service_account(domain):
    """Return the service account of a formerly writable user domain,
    or None."""
    return _load_secrets().get(domain, {}).get("service_account")

def _domain_provider(domain):
    rdb = agent.redis_connect(use_replica=True)
    return cluster.userdomains.list_domains(rdb)[domain]["providers"][0]["id"]

def _remove_service_account(domain):
    account = service_account(domain)
    if account:
        print(f"Removing service account {account['user']} from user domain {domain}", file=sys.stderr)
        response = agent.tasks.run(agent_id=f"module/{_domain_provider(domain)}", action="remove-user",
            data={"user": account["user"]}, extra={"isNotificationHidden": True})
        if response["exit_code"] != 0:
            # Keep the secret, to try again at the next start
            print(agent.SD_WARNING + f"Cannot remove service account {account['user']}", file=sys.stderr)
            return
    data = _load_secrets()
    if data.pop(domain, None) is not None:
        _save_secrets(data)

def module_idps(kc, realm):
    """The federated IdPs created by the module: they use its first
    broker login flow. IdPs added with the Keycloak console are left
    alone."""
    return [idp for idp in kc.get(f"/{realm}/identity-provider/instances")
        if idp.get("firstBrokerLoginFlowAlias") == FIRST_BROKER_LOGIN_FLOW]

def _ldap_component(kc, realm, name):
    realm_id = kc.get(f"/{realm}")["id"]
    return next((c for c in kc.get(f"/{realm}/components", params={"parent": realm_id, "type": STORAGE_TYPE})
        if c["name"] == name), None)

def needs_cleanup(kc, realm, ldap_component_name):
    if service_account(realm) or module_idps(kc, realm):
        return True
    if any(f["alias"] in FLOWS for f in kc.get(f"/{realm}/authentication/flows")):
        return True
    component = _ldap_component(kc, realm, ldap_component_name)
    return bool(component and component["config"].get("editMode") == ["WRITABLE"])

def remove_federated_idps(kc, realm, ldap_component_name, ensure_federation):
    """Remove the federated IdPs of the module and what they needed from
    a realm. ensure_federation(kc, realm) applies the read-only LDAP
    federation: it runs before the service account is removed, because a
    writable federation binds as that account. Call it with the realms
    lock held."""
    if not needs_cleanup(kc, realm, ldap_component_name):
        ensure_federation(kc, realm)
        return
    print(f"Removing the federated IdPs of realm {realm}: they are no longer supported", file=sys.stderr)
    for idp in module_idps(kc, realm):
        print(f"Removing federated IdP {idp['alias']} from realm {realm}", file=sys.stderr)
        kc.delete(f"/{realm}/identity-provider/instances/{_path(idp['alias'])}")
    # Bind the built-in flows, then remove the NS8 copies: each copy has
    # its own subflows, so the recursive deletion stops there
    kc.put(f"/{realm}", {"browserFlow": "browser", "directGrantFlow": "direct grant"})
    for flow in kc.get(f"/{realm}/authentication/flows"):
        if flow["alias"] in FLOWS:
            print(f"Removing login flow {flow['alias']} from realm {realm}", file=sys.stderr)
            kc.delete(f"/{realm}/authentication/flows/{flow['id']}")
    ensure_federation(kc, realm)
    component = _ldap_component(kc, realm, ldap_component_name)
    if component:
        for mapper in kc.get(f"/{realm}/components", params={"parent": component["id"], "type": MAPPER_TYPE}):
            if mapper["name"] in WRITABLE_MAPPERS:
                kc.delete(f"/{realm}/components/{mapper['id']}")
            elif mapper["config"].get("read.only") == ["false"]:
                mapper["config"]["read.only"] = ["true"]
                kc.put(f"/{realm}/components/{mapper['id']}", mapper)
    _remove_service_account(realm)
