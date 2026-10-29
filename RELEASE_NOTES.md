Vierte Vorabversion des angepassten Identity-Provider-Moduls für NethServer 8. Sicherheitsupdate.

- Keycloak 26.8.1 (bisher 26.7.4) mit den Sicherheitskorrekturen von 26.7.5 bis 26.8.1.
- Die Keycloak-Admin-Konsole (`/admin`) ist nur noch vom Knoten selbst erreichbar. Die Verwaltung erfolgt über die NS8-Oberfläche. Anmeldung, Kontoseite und OIDC bleiben öffentlich.
- Gruppenzugriff: Nur noch Mitgliedschaften aus dem AD zählen. Lokale Keycloak-Gruppenmitgliedschaften werden für alle Anwendungen des Realms ignoriert. Die AD-Föderation muss schreibgeschützt sein.
- Eine Anwendung wie Vaultwarden kann eine Gruppenregel verpflichtend machen und an ihre erwartete Gruppe binden. Fehlt die Regel oder weicht sie ab, wird der Zugang gesperrt statt geöffnet.
- Strengere Prüfung der Callback-, Logout- und Origin-Adressen registrierter Anwendungen (HTTPS, exakte Adressen, keine Platzhalter im Hostnamen).
- Ohne genau einen aktiven Realm zeigt die Stamm-URL eine neutrale Hinweisseite statt der Admin-Konsole.
- Stabilerer Start beim Update: längere Startfrist, Abgleich erst nach vollständigem Keycloak-Start, Bereinigung von Clients anhand der Leader-Daten.

Update-Reihenfolge: Den IdP vor Vaultwarden 0.1.0-rc.6 aktualisieren.

Keine Stable- oder Katalogfreigabe; Vorabversion für Testinstallationen. Das Update von rc.3 mit bestehenden Realms, Clients und Gruppen ist im NS8-Test (Debian 13, Rocky 9) abgedeckt. Brute-Force-Schutz (in Planung), vollständige Wiederherstellung, physische Mobilgeräte und MFA sind nicht abgedeckt.
