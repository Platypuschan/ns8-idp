# Gitea an IdP Reworked anbinden – Machbarkeitsprüfung

Stand: 25.10.2026. Gitea-Modul: Platypuschan/ns8-gitea-reworked main d10a86cf54df7d394c67db52c358db8efd992656, Runtime docker.gitea.com/gitea:28.0.0. Nur Code-/Dokumentationsprüfung, keine Änderung an einer laufenden Instanz und kein vollständiger Gitea-OIDC-Test.

## Ergebnis

Ja. Gitea unterstützt OIDC als zusätzliche OAuth2-Anmeldequelle mit Discovery. Ein zentraler Reverse-Proxy-Login ist dafür nicht nötig. Beispiel-Quellenname `ns8-sso`, Callback `https://git.example.org/user/oauth2/ns8-sso/callback`, Discovery `https://sso.example.org/realms/ad.example.org/.well-known/openid-configuration`, Scopes `profile email` (`openid` wird ergänzt).

Der Administrator kann den an die Domäne gebundenen Gitea-Modulclient mit `register-client` (explizites module_id im Administratorkontext) registrieren und optional über `alter-realm-client` auf eine eigene direkte AD-Gruppe beschränken. Client-Secret sicher in der Gitea-OIDC-Quelle hinterlegen. Eine Gruppenregel ist unabhängig von Gruppen-Claims: der IdP beschränkt die Anmeldung, liefert aber derzeit keinen allgemeinen Gruppen-Claim für Gitea-Team-/Adminzuordnungen.

## Vorhandene Konten erhalten

Das Modul verwaltet eine LDAP-BindDN-Quelle und einen Recovery-Administrator. Seine Reconciliation (`imageroot/bin/gitea_auth.py`, managed_source/reconcile) lässt anders benannte OAuth2-Quellen bestehen; der Name der verwalteten LDAP-Quelle darf nicht für OIDC wiederverwendet werden.

Für bestehende LDAP-Benutzer muss OIDC mit genau demselben Gitea-Konto verknüpft werden. Giteas ACCOUNT_LINKING=login verlangt eine Anmeldung zum Verknüpfen und vermeidet eine pauschale automatische Verknüpfung allein anhand Benutzername/E-Mail. Erst anhand existierender IDs, Repository-Besitz und Berechtigungen prüfen, dass keine neuen Parallelkonten entstehen. LDAP-Quelle und Recovery-Administrator während der Einführung erhalten.

## Grenzen

SSO beim Web-Login ersetzt weder Git-SSH-Schlüssel noch persönliche API-Tokens und setzt bestehende Gitea-Websitzungen nicht automatisch außer Kraft. Entzug der IdP-Gruppe allein ist deshalb keine vollständige Sperre eines bestehenden Gitea-Kontos. Gitea-Kontosperre, vorhandene Sessions, Tokens und SSH-Zugang benötigen eine gesonderte Richtlinie.

Automatisierte Modulkonfiguration fehlt derzeit: Metadaten um `idp-reworked@any:clientadm` ergänzen, Domänenbindung und OIDC-Registrierung einbauen, private Secrets sowie optionalen Gruppenstatus verwalten und im Backend/UI konfigurierbar machen. Wiederkonfiguration, Restore/Klon, IdP-Wechsel, Account-Linking und Git-Zugänge testen. Das ist ein möglicher Folgeauftrag, kein hier implementierter Umbau.

Quellen:
- https://docs.gitea.com/administration/authentication/#oauth2-and-openid-connect
- https://docs.gitea.com/administration/config-cheat-sheet/#oauth2-client-oauth2_client
- https://github.com/Platypuschan/ns8-gitea-reworked/blob/d10a86cf54df7d394c67db52c358db8efd992656/imageroot/bin/gitea_auth.py
