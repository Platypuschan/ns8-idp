Erste Vorabversion des angepassten Identity-Provider-Moduls für NethServer 8.

- Gemeinsame Realm-Sperre für Clientänderungen und Ereignisabgleich.
- Optionale direkte LDAP-Gruppenfreigabe pro OIDC-Client, geprüft bei Anmeldung sowie Token-Ausgabe und Refresh.
- Statusabfrage `get-client-access` und optionale Access-Token-Laufzeit pro Client.
- Eigenständige Pakete `idp-reworked` und `idp-reworked-keycloak`.

Konfiguration der Gruppenregel erfolgt per API. Keine Stable-/Katalogfreigabe und keine automatische Migration bestehender IdP-Instanzen. Vorabversion für Testinstallationen; physische Mobilgeräte, vollständige Cluster-Wiederherstellung und sämtliche externen IdP-/MFA-Szenarien sind nicht abgedeckt.
