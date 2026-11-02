# Codex Cloud

Checkout: `/workspace/Kalkulator-Konstrukcji-Drewnianych`.
Każde zadanie jest izolowane; korzystaj z istniejącego checkoutu, bez tworzenia worktree.
Node.js 24.19.0 i npm 11.x. Przy innym Node aktywuj wersję z `.nvmrc`
za pomocą menedżera wersji dostępnego w obrazie, zanim uruchomisz setup.

## Install script

```sh
set -eu
cd /workspace/Kalkulator-Konstrukcji-Drewnianych
bash scripts/setup.sh
```

## Start instructions

Przejdź do checkoutu. Sprawdź `node --version` i `npm --version`.
Jeśli brakuje zależności, uruchom install script.
Uruchom `npm run dev -- --port 5173 --strictPort` w sesji długotrwałej.
Sprawdź lokalnie odpowiedź HTTP i tytuł strony; `npm run test:e2e` weryfikuje
interakcję formularza w Chromium, uruchamiając osobny serwer na porcie 4173.
Walidacja całości: `npm run check` i `npm run test:e2e`.
Nie zakładaj przetrwania procesów po odtworzeniu środowiska.

## Sieć i publikacja

Wymagany jest dostęp do github.com (platformowy proxy Git), registry.npmjs.org
oraz, w obrazach bez `/usr/bin/chromium`, hostów dystrybucji Playwright: cdn.playwright.dev i hostów przekierowań wskazanych przez instalator. W zweryfikowanym obrazie używany jest systemowy Chromium, bez dodatkowych domen.
Nie wyłączaj TLS ani weryfikacji pakietów. Zachowaj proxy i zaufane CA platformy.
Brak wymaganych sekretów. Nie umieszczaj tokenów w plikach projektu.
Zapis draftu nie publikuje środowiska; użytkownik przegląda i zapisuje ustawienia,
a następnie publikuje snapshot. Nowe zadanie wymaga osobnej weryfikacji odtworzenia.
