# Optional personal device certificates

Date: 2026-10-31. User request: research, implement and test LXD-style certificate
authentication in ns8-idp-reworked; use the physical L8 tablet where available.
Implementation decision by Codex; no release/production deployment authorization.

## Decision

Use the existing Traefik TLS boundary, Keycloak browser flow and LDAP federation.
Maintain administrator-managed SHA-256 pins of public certificates in realm
attributes. Each pin binds a Keycloak user ID and the LDAP_ID (AD objectGUID /
LDAP entryUUID), not an email/CN or a user-editable attribute. Self-signed client
certificates work. TLS authenticates possession of their private key; a PEM
uploaded to the module never suffices for login. A new Keycloak Authenticator
consumes the pinned runtime's Traefik X509 lookup provider.

The standard X509 subject/email mapper is unsuitable for independent per-device
enrollment/revocation and does not by itself provide the desired immutable
directory binding. A module CA would add CA private key custody, issuance and
CRL/OCSP operations. Explicit device pins avoid that additional service while
matching the LXD enrollment model. Client keys and PKCS#12 passwords are created
on the workstation and never enter NS8 action input/output or Redis task history.

NS8 Traefik needs the accompanying API patch: optional RequestClientCert,
strip-before-PassTLSClientCert, roundtrip capability flag and identical TLS
options on both host routers. Keycloak remains published only on loopback.
Because other local applications may reach that listener, the module generates
a 256-bit proof in its private state file; Traefik overwrites the proof header
and Keycloak requires a constant-time match against the realm's administrative
attribute. A public PEM plus forged headers, remotely or on loopback, is denied.
The proxy proof necessarily travels through the administrative `set-route`
tasks and is persisted in Traefik route configuration as well as realm
attributes. Treat those internal task/configuration records as credentials;
the public certificate management action never returns the proof.
Traefik administrators/routeadm modules remain inside the trust boundary: they
can already redirect routes and intercept authentication. Never publish the
route API or Keycloak backend to untrusted clients. Never log the proof header.

Certificate login is opt-in per realm. A copied standard browser flow adds an
alternative after SSO cookies and before password forms. Password login remains.
Custom browser flow bindings are rejected for manual review. Like LXD, this is a
possession-based login method, **not an additional second factor**: it bypasses
the password/form branch, including conditional OTP there. Sites requiring MFA
must not enable it without a reviewed flow enforcing their second factor.
Required actions and client token gates still check live LDAP_ONLY groups.

## Lifecycle and failure behavior

Enrollment accepts exactly one current client certificate with clientAuth EKU,
rejects private keys/bundles/CAs and only binds enabled federated users. At login,
check validity, key usage, EKU, exact pin, current enabled directory user and both
immutable identifiers. Unknown certificates can fall back to password login;
invalid registered certificates and directory errors never produce a certificate
login. Attributes are administrative, not user profile mappings.

Revoke first writes a denied tombstone, then logs out all IdP sessions of that
user, then removes the record. A logout failure keeps a visible denied record
which can be retried. Revocation logs out the user's other devices as well.
Already-issued app tokens, application sessions and offline data have their
existing lifetimes and revocation mechanisms; no new immediate app-wide logout
guarantee. Certificate expiry/feature disablement only prevents new certificate
authentication, not all existing SSO/app sessions. Existing SSO cookies run first.

All mutations use the existing realms lock. Enabling configures/checks transport
before binding the flow; disabling unbinds the realm before removing unneeded
transport. Unsupported proxy capability is an error with route rollback.
Registration and ordinary module configuration preserve other realm attributes.
Public pins are in the Keycloak database, already in the postgres backup; the
proof is in persistent module state (existing state backup). Restore/reconfigure
must recreate both routes with identical TLS options and the same proof. Lost
proof state requires re-enabling realms to bind the new proof. Do not claim a
full NS8 backup/restore validation from protocol persistence tests.

## Sources

- [Pinned NS8 route API](https://github.com/NethServer/ns8-traefik/blob/21fa9f2e0b14ac84caed6fb4b68bb962d364a5b7/imageroot/actions/set-route/validate-input.json)
- [Pinned Keycloak 26.8.1 Traefik certificate lookup](https://github.com/keycloak/keycloak/blob/26.8.1/services/src/main/java/org/keycloak/services/x509/TraefikProxySslClientCertificateLookup.java)
- [Keycloak reverse proxy trust boundary](https://www.keycloak.org/server/reverseproxy)
- [Traefik PassTLSClientCert](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/passtlsclientcert/)
- [Traefik TLS options](https://doc.traefik.io/traefik/reference/routing-configuration/http/tls/tls-options/)
- [Android KeyChain](https://developer.android.com/reference/android/security/KeyChain)
