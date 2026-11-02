# Zasady pracy
Korzystaj z istniejącego checkoutu; nie twórz worktree bez prośby użytkownika.
Node.js 24.19.0, npm 11.x. Instalacja: `bash scripts/setup.sh`.
Start: `npm run dev -- --port 5173 --strictPort`.
Przed zakończeniem zmian: `npm run check` oraz `npm run test:e2e` dla zmian UI.
Logika domenowa jest w src/domain, UI w src/ui. Każdy moduł obliczeniowy musi mieć testy, w tym przypadki graniczne i niezależnie zweryfikowane przykłady.
Nie implementuj wzorów ani współczynników bez potwierdzonego źródła, wydania, punktu normy, zmian i właściwego polskiego załącznika krajowego.
Jednostki wejścia i wyjścia muszą być jawne. Raportuj założenia, kroki i źródła tak, aby wyniki można było niezależnie odtworzyć.
Nie zapisuj sekretów. Nie zmieniaj lockfile bez potrzeby. Nie deklaruj nieuruchomionych testów jako zaliczonych.
