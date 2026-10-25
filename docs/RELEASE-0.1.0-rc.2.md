# IdP Reworked 0.1.0-rc.2

Veröffentlicht am 25.10.2026 als Vorabversion, kein Stable-/Katalogrelease. Release-Notizen vom Nutzer am 25.10.2026 unverändert freigegeben.

- [Release](https://github.com/Platypuschan/ns8-idp-reworked/releases/tag/0.1.0-rc.2)
- Geprüfter Release-Commit: cfccd5989a049a43170b3c27a528e3c1737c598a (Merge von [PR #1](https://github.com/Platypuschan/ns8-idp-reworked/pull/1); Baum identisch mit 53c89822fd682043f54cf5bfd2543f85f052bada, dem `IDP_REF` von Vaultwarden Reworked 0.1.0-rc.2).
- [Build, QEMU und Freigabe](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/40240445302): vollständig erfolgreich; Debian13 und Rocky9 jeweils 30 PASS, 1 erwarteter Upgrade-Skip, 0 FAIL, darunter „Restrict a client to a group“. Core 3.23.2. Kein Produktivrollout.
- Funktionstests am vorbereiteten Commit 53c8982: [Client access tests](https://github.com/Platypuschan/ns8-idp-reworked/actions/runs/40239987580) erfolgreich (Unit 15, Sperre 3 mit 1 Skip, Protokoll 16 und 6 gegen Keycloak 26.7.4 und Samba AD).

| Image | Digest |
| --- | --- |
| ghcr.io/platypuschan/idp-reworked:0.1.0-rc.2 | sha256:9062a9700f97c8fca57de3d7483fc7a0d2d08680c5f290f61ef58571180a3ac9 |
| ghcr.io/platypuschan/idp-reworked-keycloak:0.1.0-rc.2 | sha256:b2d3b50ed93a3070dafbc1c33ece43e5bdda0bff1d3db86e6864fce4c441c4db |

Beide Images unabhängig anonym aus GHCR geprüft. Das Modul referenziert die Keycloak-Runtime per Digest. RC-Digests entsprechen den QEMU-geprüften Kandidaten (`candidate-cfccd5989a04`). Der GitHub-Release-Text stimmt exakt mit RELEASE_NOTES.md überein. Der API-Dokumentations-Workflow läuft seit 0.1.0-rc.2 erfolgreich.

Nicht geprüft: Update einer NS8-Installation von 0.1.0-rc.1 (die Bereinigung externer IdPs ist im Protokolltest gegen Keycloak abgedeckt), die Seite „Zugriff“ im Browser, physische Mobilgeräte, MFA-Szenarien, vollständige Cluster-Wiederherstellung.
