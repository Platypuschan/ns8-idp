Zweite Vorabversion des angepassten Identity-Provider-Moduls für NethServer 8.

- Neue Seite „Zugriff“: die zugelassene AD-Gruppe jeder Anwendung in der Oberfläche wählen, speichern und live prüfen.
- Statusabfrage `get-client-access` mit `live`: LDAP-Erreichbarkeit, Existenz der Gruppe im AD und, für Administratoren, die Prüfung eines einzelnen Benutzers.
- Das Setzen einer Gruppenregel deaktiviert den Client nicht mehr; bei einem Fehler bleibt er unverändert.
- Device-Grant, CIBA und Token-Exchange werden mit der Gruppenregel abgeschaltet und als Problem gemeldet, falls sie wieder eingeschaltet werden. SAML-Anmeldungen sind durch dieselbe Prüfung abgedeckt.
- Externe Identitätsanbieter wie Microsoft Entra ID werden nicht mehr unterstützt. Beim Start nach dem Update entfernt der IdP die vom Modul angelegten externen IdPs samt Anmeldeflows, schreibbarer LDAP-Föderation und Servicekonto; dabei angelegte AD-Konten bleiben ohne Passwort erhalten.
- Korrigierte geerbte Workflows für API-Dokumentation und Registry-Bereinigung.

Keine Stable-/Katalogfreigabe. Vorabversion für Testinstallationen. Die Bereinigung ist gegen Keycloak getestet, ein NS8-Update von 0.1.0-rc.1 nicht. Physische Mobilgeräte, vollständige Cluster-Wiederherstellung und MFA-Szenarien sind nicht abgedeckt.
