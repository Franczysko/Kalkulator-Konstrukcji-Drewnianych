# Raport przygotowania środowiska — 2026-11-02

## Stan początkowy i architektura

Repozytorium nie miało plików, commitów ani zdalnych gałęzi (w tym main).
Git HTTPS działa przez platformowy proxy. Utworzono gałąź setup/cloud-foundation
oraz wysłano ją do origin. Nie utworzono main ani pull requestu:
GitHub CLI zgłasza nieprawidłową autoryzację, a próba utworzenia PR przez API
zakończyła się Forbidden. Push Git działa niezależnie od dostępu do API.

Wybrano React + TypeScript + Vite jako lekki fundament aplikacji internetowej.
Domena jest niezależna od React; przygotowano katalogi materiałów, obciążeń,
kombinacji, nośności/stateczności i połączeń. Brak wzorów konstrukcyjnych.
Vitest obsługuje testy domeny i integracji; Playwright sprawdza rzeczywiste UI.

## Narzędzia i zależności zweryfikowane

Node.js 24.19.0, npm 11.9.0, Chromium 154.0.8037.57.
React/React DOM 19.3.1, TypeScript 6.0.3, Vite 8.3.5,
Vitest 5.0.5, ESLint 10.14.0, Playwright 1.64.1,
@vitejs/plugin-react 6.2.0, typescript-eslint 8.72.1.
Komplet dokładnych wersji zawierają package.json i package-lock.json.

## Utworzone pliki

README.md, AGENTS.md, .gitignore, .npmrc, .nvmrc, package.json,
package-lock.json, tsconfig.json, vite.config.ts, eslint.config.js,
playwright.config.ts, index.html, scripts/setup.sh, .github/workflows/ci.yml,
src/main.tsx, src/ui/{App.tsx,styles.css}, src/domain/{modules.ts,project.ts,
project.test.ts}, README.md w pięciu katalogach domenowych,
tests/integration/project.test.ts, tests/e2e/app.spec.ts,
tests/fixtures/project.json, docs/{cloud.md,engineering.md,setup-report.md}.

## Faktyczne wyniki

| Kontrola | Wynik |
| --- | --- |
| Dostęp Git i pusty zdalny repozytorium | Potwierdzone |
| Instalacja z lockfile przez npm ci | Zaliczone; npm ci odtwarza node_modules |
| Ponowne wykonanie scripts/setup.sh | Zaliczone; dwa udane pełne wykonania |
| ESLint | Zaliczone |
| TypeScript | Zaliczone |
| Vitest jednostkowe | 3 zaliczone |
| Vitest integracyjne | 1 zaliczony |
| Build produkcyjny | Zaliczone |
| Chromium E2E | 2 zaliczone, ponowny przebieg również zaliczony |
| Start udokumentowaną komendą na porcie 5173 | Zaliczone |
| HTTP strony i modułu React | Zaliczone |
| Instalacja wszystkich pakietów / npm ls | Bez brakujących zależności |
| git diff --check | Zaliczone |
| Push osobnej gałęzi | Zaliczone |
| Utworzenie PR | Zablokowane: API Forbidden i brak main |
| GitHub Actions na GitHub | Nie uruchamiano; konfiguracja przygotowana |
| Odtworzenie snapshotu w nowym zadaniu | Nie testowano; wymaga publikacji |

Nie wykonano instalacji całego systemu operacyjnego od zera. Sprawdzono czystą
instalację pakietów projektu w dostarczonym obrazie oraz jej powtórzenie.

## Rozwiązane błędy i ograniczenia

Pierwsza próba pobrania Chromium Playwright otrzymała 403 Domain forbidden
z cdn.playwright.dev. Setup i konfigurację poprawiono tak, aby korzystały
z obecnego systemowego /usr/bin/chromium; testy E2E następnie przeszły.
W obrazie bez Chromium instalator próbuje pobrać przeglądarkę Playwright;
wymaga to dopuszczonych domen dystrybucji i bibliotek Linux. CI instaluje biblioteki.
Nie wyłączano TLS, sum integralności ani asercji testów.

Brak wymaganych sekretów i usług. Nie wdrożono obliczeń, trwałego zapisu ani
walidacji metod normowych. GitHub Actions wymaga przyszłego PR lub push na main;
lokalne powodzenie komend nie jest dowodem wykonania workflow na GitHub.

## Ustawienia Codex Cloud

Pełne instrukcje: docs/cloud.md; wykonywalny skrypt: scripts/setup.sh.
Install script: `set -eu`, następnie `cd /workspace/Kalkulator-Konstrukcji-Drewnianych`
i `bash scripts/setup.sh`.
Start: w tym katalogu `npm run dev -- --port 5173 --strictPort`;
kontrole: `npm run check` i `npm run test:e2e`.
Wersja Node: 24.19.0; npm: 11.x. Sieć: obecny preset package_managers,
bez dodatkowych sekretów i bez poszerzania listy domen w zweryfikowanym obrazie.
Procesy trzeba uruchamiać ponownie po odtworzeniu snapshotu.
Publikację wykonuje użytkownik w ustawieniach środowiska po przeglądzie i zapisie.

## Stopień realizacji (wykonanie i weryfikacja)

| Etap | Realizacja | Podstawa / pozostałe działania |
| --- | --- | --- |
| 1 Analiza | 100% | Potwierdzono pusty stan i brak main |
| 2 Technologie | 100% | Zainstalowane i przetestowane |
| 3 Konfiguracja Cloud | 90% | Instalacja sprawdzona; publikacja i nowe zadanie po stronie platformy/użytkownika |
| 4 Struktura | 100% | Pliki, katalogi i instrukcje utworzone |
| 5 Zasady inżynierskie | 100% | Architektura i reguły; bez niezweryfikowanych wzorów |
| 6 Testy środowiska | 100% | Wszystkie wymagane lokalne kontrole wykonane |
| 7 GitHub automation | 50% | Workflow przygotowany, brak wykonania zdalnego i PR |
| 8 Audyt | 90% | Lokalny audyt zaliczony, odtworzenie w nowym zadaniu niezweryfikowane |
| 9 Raport | 100% | Wyniki i ograniczenia udokumentowane |

Procenty opisują zakres działań, nie są miarą pokrycia testami.
