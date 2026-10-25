# Lokale Vorbereitung, 25.10.2026

Basis: b82c75c (Client-Gruppenpolicy auf ns8-idp 433fa069). Keine neuen Anwendungs-/Java-Funktionsänderungen; eigenständige Modul-/Runtime-Namen, passende NS8-Umgebungsvariablen, Paketmetadaten und manuell freizugebender RC-Ablauf.

- Vollständiger Keycloak-Runtime lokal gebaut (optimierter PostgreSQL-Runtime, ursprüngliche NS8-Provider plus Required Action/Token-Gate).
- IdP-Modulpaket einschließlich UI lokal gebaut. NODE_OPTIONS übernimmt die vom Original benötigte OpenSSL-Legacy-Buildeinstellung.
- 8 API-/Schema-Tests und 2 Sperr-/Ereignistests grün; optionale Negativkontrolle ohne unmodifizierten Checkout übersprungen.
- Gemeinsame lokale Samba-AD/Keycloak/gepatchter-Vaultwarden-Suite: 15 Tests grün (62.345 s). Verwendet unabhängigen IdP-Quellstand und neuen vollständigen IdP-Runtime. Vaultwarden-Runtime ist das vorhandene unveränderte gepatchte Binary; das neue Runtime-Rezept ändert nur die Repository-Quellkennzeichnung.
- GitHub-Actions-Workflow mit actionlint 1.7.12 geprüft.

Noch nicht: neue Images auf GHCR, NS8-QEMU mit neuen Paketnamen, stabile Veröffentlichung, produktive Installation. QEMU und RC-Promotion sind erst nach konkreter Veröffentlichungsfreigabe vorgesehen. Keine Behauptung alter CI-Läufe als Nachweis der neuen Paketnamen.
