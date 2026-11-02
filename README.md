# Kalkulator konstrukcji drewnianych

Fundament aplikacji React + TypeScript + Vite. Interfejs tworzy wyłącznie szkic
nazwy projektu w pamięci; brak obliczeń konstrukcyjnych i zapisu danych.

## Wymagania i uruchomienie

Linux, Node.js **24.19.0**, npm **11.x** (zweryfikowano 11.9.0).

```sh
bash scripts/setup.sh
npm run dev -- --port 5173 --strictPort
```

Skrypt używa `npm ci`, nie modyfikuje lockfile i korzysta z systemowego `/usr/bin/chromium`, jeśli jest dostępny; w przeciwnym razie instaluje Chromium Playwright.
W minimalnym obrazie Linux mogą być potrzebne biblioteki systemowe:
`npx playwright install-deps chromium` (wymaga uprawnień administratora).

```sh
npm run check       # ESLint, TypeScript, Vitest (unit + integration), build
npm run test:e2e    # Chromium; sam uruchamia i zatrzymuje Vite na porcie 4173
npm run preview -- --port 4174 --strictPort  # po npm run build
```

## Struktura

- `src/domain`: logika niezależna od UI i miejsca na moduły inżynierskie.
- `src/ui`: interfejs React i style.
- `tests/integration`, `tests/e2e`, `tests/fixtures`: integracja, przeglądarka, dane.
- `docs/engineering.md`: źródła norm, jednostki i zasady weryfikacji.
- `docs/cloud.md`: konfiguracja Codex Cloud.
- `.github/workflows/ci.yml`: kontrole PR i zmian na main.

Zależności bezpośrednie mają dokładne wersje; `package-lock.json` utrwala drzewo.
Nie są wymagane sekrety, zewnętrzne usługi ani baza danych.
