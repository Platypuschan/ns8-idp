# IdP Reworked 0.1.0-rc.1

Veröffentlicht am 25.10.2026 als Vorabversion, kein Stable-/Katalogrelease.

- [Release](https://github.com/Platypuschan/ns8-idp-reworked/releases/tag/0.1.0-rc.1)
- Geprüfter Release-Commit: fb4b4a4fd4562f18dec9efe42014a7c4bac2620e.
- [Build, QEMU und Freigabe](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/40216326408): vollständig erfolgreich; Debian13 und Rocky9 jeweils 29 PASS, 1 erwarteter Upgrade-Skip, 0 FAIL. Core 3.23.2. Kein Produktivrollout.
- [Separate Funktionstests](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/40216319529): erfolgreich.

| Image | Digest |
| --- | --- |
| ghcr.io/platypuschan/idp-reworked:0.1.0-rc.1 | sha256:25d7d88d378652fd6fb7b962793fcccf8fc2f2596c3db8245497c226cbb78ff9 |
| ghcr.io/platypuschan/idp-reworked-keycloak:0.1.0-rc.1 | sha256:5459d9cfa67a067f1c4125400968506b6c907d2e490c2921c0de30560249c0d0 |

Beide Images unabhängig anonym aus GHCR geprüft, amd64. Modul referenziert den Keycloak-Runtime per Digest. RC-Digests entsprechen den QEMU-geprüften Kandidaten. Nur die Konfiguration der Gruppenpolicy ist API-basiert; umfassende MFA-/externe-IdP-/Cluster-DR-Prüfungen sind nicht abgedeckt. Separate geerbte API-Dokumentationsautomation meldete startup_failure; das ist kein erfolgreicher API-Doku-Build und kein Modultestfehler.
