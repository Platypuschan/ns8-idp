# 0001: Client access hardening and no external IdPs

Date: 2026-10-25. Status: implemented on branch `claude/reworked-hardening`,
not released. Base: 0.1.0-rc.1 (`fb4b4a4`), Keycloak 26.7.4.

User requests (chat, 25.10.2026): configure the group of an application in
the idp UI; implement a live status check; change the failure handling;
test whether SAML logins are covered; remove the possibility to add Entra
ID or similar external IdPs; correct the inherited workflows.

## Decisions

- **No external IdPs.** The federated IdP actions (`add-`, `alter-`,
  `remove-federated-idp`), the login modes, the writable LDAP federation
  with its service account, `register-service-account` and the link
  authenticator are removed. `keycloak-post-start` removes them from realms
  of earlier versions (`idplegacy.py`): only IdPs that use the module's
  first broker login flow, the `ns8 *` flow copies, the writable mappers and
  the service account. The built-in flows are bound first, then each copy
  is deleted: a copy only contains its own subflows, so Keycloak's
  recursive deletion stops there. The `domadm` authorizations stay for now:
  the cleanup removes the service account with the `remove-user` action of
  the account provider. Drop them when no 0.1.0-rc.1 installation is left.
- **No disabled clients.** The checks pass for clients without the policy
  attribute, so `set_policy` installs the required action and the token
  mapper first and sets the attribute and grant flags with one client
  update. Every failure leaves the client enabled, either unrestricted as
  before or restricted. The old procedure disabled the client and left it
  disabled on a failure.
- **Grants.** The device grant, CIBA and standard token exchange are
  switched off with the other grants and reported as issues if switched on
  again. Tests show that device logins and token exchanges of non-members
  are denied anyway (required action, token mapper).
- **SAML.** Tested hypothesis, confirmed: the required action denies SAML
  logins, SP- and IdP-initiated, also with an SSO cookie of another client.
  Modules register only OIDC clients, so `set_policy` refuses other
  protocols (`protocol_not_supported`); no SAML policy API is added.
- **Live status.** `get-client-access` with `live` tests the LDAP bind of
  the federation (`testLDAPConnection` with the stored credential), looks
  the group up in the user domain (`agent.ldapclient`), and, for
  administrators only, runs the token mapper for one user with the
  example-token endpoint. That endpoint creates a user session and removes
  it in the same request; the test checks that none is left. `enforced`
  keeps its structural meaning.
- **Callers.** NS8 sets `AGENT_TASK_USER` to the UI user ID: only callers
  `module/*` are restricted to their own client; any other caller passed
  the API server role check and selects the client.
- **UI.** A new Access page lists the clients of each realm with a group
  selection from `list-domain-groups`, saves with `alter-realm-client` and
  checks with `get-client-access` (live).
- **Workflows.** `build-apidoc` and `clean-apidoc` grant `contents: write`
  to the called reusable workflows (the fork token is read-only, which made
  every run fail at startup). `clean-registry` deletes the `idp-reworked`
  and `idp-reworked-keycloak` packages (it named the upstream packages and
  failed with HTTP 404).
