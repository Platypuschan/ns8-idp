# Vorabversion 0.1.0-rc.2 vorbereiten

Arbeitsbranch: `claude/reworked-hardening` ([PR #1](https://github.com/Platypuschan/ns8-idp-reworked/pull/1)). Getestete Anwendungsstände unverändert: Keycloak 26.7.4, Vaultwarden 1.37.2 mit API-Key-Patch; keine pauschalen Abhängigkeitsupgrades. Der vorige Ablauf für 0.1.0-rc.1 ist in [RELEASE-0.1.0-rc.1.md](RELEASE-0.1.0-rc.1.md) belegt.

Nach ausdrücklicher Nutzerfreigabe der Release-Notizen:

1. PR #1 mit einem Merge-Commit nach `main` übernehmen, nicht per Squash: Vaultwarden pinnt in `IDP_REF` den Branch-Commit, der dabei erreichbar bleiben muss.
2. `Prepare prerelease` auf dem Merge-Commit von `main` manuell starten. VERSION erlaubt ausschließlich RC-Versionen.
3. Der Workflow baut Kandidaten (`candidate-<commit>`), veröffentlicht zunächst diese Testimages und referenziert die Keycloak-Runtime im Modul per Digest.
4. NS8-QEMU muss auf Debian 13 und Rocky 9 erfolgreich sein.
5. Erst nach grünen Prüfungen werden die geprüften Digests auf `0.1.0-rc.2` kopiert und ein GitHub-Prerelease mit RELEASE_NOTES.md erstellt. Vorhandene Versionstags werden nicht überschrieben. Kein `latest`, keine Katalogaufnahme und kein Produktivrollout.
6. Danach die Prüfnachweise in `docs/RELEASE-0.1.0-rc.2.md` festhalten und den Kopf der README auf „veröffentlicht“ ändern.

Reihenfolge: zuerst IdP, anschließend Vaultwarden, dessen Prüfungen das veröffentlichte `idp-reworked:0.1.0-rc.2` installieren. Die Pakete `idp-reworked` und `idp-reworked-keycloak` sind bereits öffentlich; neue Tags erben diese Sichtbarkeit.

IdP-QEMU führt die Realm-, Gruppenregel- und Entfernungs-Suite als Neuinstallation aus. Ein Update von 0.1.0-rc.1 (Bereinigung externer IdPs) prüft der Workflow nicht; die Bereinigung ist im Protokolltest gegen Keycloak abgedeckt.

Die Release-Notizen sind keine Behauptung bereits abgeschlossener RC-Tests. Testberichte und lokale Prüfungen werden getrennt dokumentiert.
