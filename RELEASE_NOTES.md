Dritte Vorabversion des angepassten Identity-Provider-Moduls für NethServer 8.

- Die Stamm-URL des IdP-Hosts (`https://<host>/`) führt jetzt zur Kontoseite der Benutzerdomäne (`/realms/<Domäne>/account/`), wenn das Modul genau einen aktiven Realm verwaltet. Bisher führte sie zur Admin-Konsole des master-Realms; eine Anmeldung mit einem Domänenkonto scheiterte dort mit „Invalid username or password“.
- Bei keinem oder mehreren Realms bleibt die Admin-Konsole das Ziel, damit keine Seite die Benutzerdomänen öffentlich auflistet. Die Admin-Konsole ist weiterhin unter `/admin/` erreichbar.
- Sonst unverändert gegenüber 0.1.0-rc.2, weiterhin Keycloak 26.7.4.

Keine Stable-/Katalogfreigabe. Vorabversion für Testinstallationen. Ein NS8-Update von 0.1.0-rc.2 ist nicht automatisiert getestet. Physische Mobilgeräte, vollständige Cluster-Wiederherstellung und MFA-Szenarien sind nicht abgedeckt.
