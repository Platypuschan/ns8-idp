# Certificate authentication validation, 2026-10-31

Implementation task: `20261031-codex-x509-login`. No production service was
reconfigured. The companion proxy change is a source patch, not an installed
replacement for stock NS8 Traefik.

## Local protocol and build evidence

At implementation commit `72652cf5ce5035e2acab8c5e83d0e7c562f1a591`:

- 31 unit/action cases, 30 passed and one existing expected skip.
- Existing real Keycloak/Samba suites: 17 client-access, 6 failure, 8 security
  decision cases passed.
- 6 new real TLS/Traefik/Keycloak/Samba cases passed. These use the actual
  patched NS8 route writer, coexisting root/admin routers, the pinned Keycloak
  26.8.1 provider and Traefik 3.6.1 digest pinned in the test driver.
- Certificate key possession; unknown/expired/revoked credentials; forged
  certificate headers over TLS and directly on loopback; mismatched LDAP
  identity; AD account disablement/group removal; SSO-cookie logout; password
  fallback; feature disablement; persistent pins/flow after restart covered.
- Full UI build, module image build and optimized Keycloak image build passed.
  `show-config` confirms persisted Traefik lookup provider / PostgreSQL / scripts.
- NS8 Robot suite dryrun: 36/36. This is syntax/control-flow validation, not a
  live NS8 result. New real NS8 cases enroll/revoke an OpenLDAP user's public
  certificate and check stock-proxy capability rejection with password fallback.

Follow-up `6abef98` preserves rollback on browser-flow failure, allows removal
of a deleted user's denied certificate tombstone and adds the CI-only Rocky
bootstrap described below. Unit/action cases rerun: 30 passed / 1 expected skip.
No Java or authentication-transport changes in that follow-up.

## Physical Android L8

ADB shell and app installation verified on PRITOM L8 / L8_B02, Android 13.
Chrome **156.0.8078.73**, system WebView **156.0.8078.47**. A dedicated disposable
`org.nethserver.x509test` app was built from `tests/x509/android/`, rather than
changing an existing app's accounts or server configuration.

The isolated fixture has Samba AD, the candidate Keycloak provider, real
Traefik TLS and a public native OIDC client with S256 PKCE and live AD group
access policy. Only loopback listeners are published; `adb reverse` connects
the tablet's localhost to that fixture. A test-only self-signed client identity
is imported through Android's normal **VPN and apps** installer. Its private
key never enters an NS8 action or repository. No global server CA is installed;
Chrome's self-signed-server warning is accepted only for the local fixture;
the test app independently pins that exact server certificate for token calls.

Observed on the physical device, without entering an IdP username/password:

| Flow | Result |
|---|---|
| Chrome → native custom-scheme callback → PKCE token exchange | `OIDC PKCE TOKEN SUCCESS` |
| Chrome Custom Tab → native callback → PKCE token exchange | `OIDC PKCE TOKEN SUCCESS` |
| Embedded WebView implementing Android KeyChain callback | System certificate picker, then `OIDC PKCE TOKEN SUCCESS` |
| Remove test user from the app's AD group, repeat Custom Tab login | `accessDenied`; no successful callback/token |
| Restore AD group, revoke enrolled device pin and IdP sessions, repeat | Username/password form; certificate alone no longer signs in |

These are native OIDC integration tests, **not a complete Bitwarden app login**
and not a test of vault unlock/biometrics. Embedded WebViews without a
`ClientCertRequest`/KeyChain implementation are not covered or assumed to work.
Existing Bitwarden/Firefox accounts, configurations and app data were preserved.
Fixture APKs, PKCS#12 files, token responses and unsanitized UI dumps are private
local test material and must not be published as artifacts.

Cleanup completed: the test client certificate/key was removed through Android
user credentials (the existing WLAN identity was preserved), the separate app
was uninstalled, only the fixture's ADB reverse mapping was removed, and the
temporary containers/network and private fixture keys/PKCS#12/APKs/credentials
were deleted. No existing application account or server setting was changed.

## CI and limitations

[Initial protocol CI](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/41199047571)
passed at `72652cf`. The first candidate
[41199046354](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/41199046354)
built successfully, but Rocky failed before module testing: NethServer's BaseOS
mirror advertised metadata files returning HTTP 404. This repeats the verified
Vaultwarden rc.8 CI infrastructure failure, not an authentication failure.

`tests/ns8/bootstrap-rocky.sh` uses a pinned/checksummed NS8 installer, Core
3.23.2, official Rocky packages with signature checking and the pinned/shared
module test runner inside the disposable VM. It changes no installed module or
production OS repositories. Final NS8/CI results are to be recorded after the
follow-up candidate finishes; no green QEMU result is claimed here in advance.

Full NS8 backup/restore and production deployment remain outside this evidence.
The stock NS8 proxy still requires the reviewed companion capability patch
before certificate sign-in can be enabled in an installation.
