# Geo Environmental Analyzer Implementation Tasks

## Zasady pracy

- Realizujemy projekt modułowo, zadanie po zadaniu.
- Nie wdrażamy kodu ani logiki bez Twojej wyraźnej zgody dla konkretnego zadania.
- W każdej sesji bierzemy jedno zadanie, doprecyzowujemy je, a potem przechodzimy do implementacji dopiero po akceptacji.
- Po każdym ukończonym zadaniu aktualizujemy `AGENTS.md` o nowe ustalenia techniczne i domenowe, gdy plik będzie już obecny w repo.

## Faza 1. Fundament projektu

### T01. Uporządkować dokumentację startową repo

- Rozmiar: `XS`
- Cel: przygotować podstawową dokumentację opisującą sens projektu i sposób pracy nad nim.
- Gotowy rezultat: `README.md` i `AGENTS.md` opisują cel projektu, zakres MVP oraz zasadę bieżącej aktualizacji wiedzy.
- Kryterium ukończenia: nowa osoba w projekcie rozumie, czym jest narzędzie, jaki ma input/output i gdzie dopisywać nowe ustalenia.
- Zależności: brak.

### T02. Skonfigurować `pyproject.toml`

- Rozmiar: `S`
- Cel: ustanowić nowoczesną, spójną konfigurację projektu Python.
- Gotowy rezultat: metadane projektu, zależności, skrypt `gea`, konfiguracja `pytest`, `ruff` i `mypy`.
- Kryterium ukończenia: projekt da się zainstalować jako pakiet i uruchomić podstawowe narzędzia jakościowe.
- Zależności: `T01`.

### T03. Ustalić strukturę katalogów pod architekturę warstwową

- Rozmiar: `XS`
- Cel: przygotować szkielet pakietów zgodny z docelową architekturą.
- Gotowy rezultat: puste moduły i pakiety dla `application`, `domain`, `infrastructure` i `analyses`.
- Kryterium ukończenia: repo ma czytelną strukturę, która oddziela orkiestrację, domenę i integracje.
- Zależności: `T02`.

### T04. Przygotować model konfiguracji aplikacji

- Rozmiar: `S`
- Cel: wprowadzić jeden spójny mechanizm konfiguracji źródeł danych i parametrów działania.
- Gotowy rezultat: `settings.toml` oraz loader konfiguracji z podstawową walidacją ścieżek i wartości.
- Kryterium ukończenia: aplikacja nie ma zaszytych ścieżek `C:\\...` ani URL-i w kodzie.
- Zależności: `T02`, `T03`.

## Faza 2. Kontrakt domenowy

### T05. Zdefiniować modele domenowe

- Rozmiar: `S`
- Cel: ustalić wspólny język dla danych wejściowych, wyników analiz i raportu końcowego.
- Gotowy rezultat: typowane modele dla punktów, trasy, działek, wyników wodnych, ochrony i bundla raportowego.
- Kryterium ukończenia: wszystkie kolejne moduły mogą używać tych samych modeli bez własnych lokalnych struktur.
- Zależności: `T03`.

### T06. Zdefiniować porty i protokoły

- Rozmiar: `S`
- Cel: rozdzielić logikę domenową od konkretnych implementacji IO i integracji.
- Gotowy rezultat: interfejsy dla readerów, analyzerów, repository i report writera.
- Kryterium ukończenia: implementacje w `infrastructure` i `analyses` są podpinane pod jasno określone kontrakty.
- Zależności: `T05`.

### T07. Wydzielić wspólne usługi domenowe

- Rozmiar: `S`
- Cel: skupić reguły wspólne dla całego systemu w jednym miejscu.
- Gotowy rezultat: moduł z detekcją EPSG PL-2000, normalizacją osi, agregacją i deduplikacją.
- Kryterium ukończenia: wspólna logika nie jest duplikowana między analizami.
- Zależności: `T05`, `T06`.

## Faza 3. Wejście i normalizacja

### T08. Zaimplementować parser wejściowego TXT

- Rozmiar: `S`
- Cel: bezpiecznie wczytywać dane wejściowe z jednego pliku tekstowego.
- Gotowy rezultat: parser akceptujący format canonical oraz prosty fallback separatorów.
- Kryterium ukończenia: parser zwraca uporządkowaną listę punktów w modelu domenowym.
- Zależności: `T05`, `T06`, `T07`.

### T09. Dodać walidację danych wejściowych

- Rozmiar: `XS`
- Cel: wcześnie wychwytywać błędny format pliku i niepełne dane.
- Gotowy rezultat: czytelne błędy dla braków kolumn, pustych pól i błędnych liczb.
- Kryterium ukończenia: użytkownik dostaje precyzyjny komunikat z kontekstem błędnego wiersza.
- Zależności: `T08`.

### T10. Zbudować obiekt `OrderedRoute`

- Rozmiar: `S`
- Cel: przekształcić punkty wejściowe w jedną spójną trasę roboczą.
- Gotowy rezultat: obiekt domenowy reprezentujący trasę z punktów w kolejności pliku.
- Kryterium ukończenia: dalsze analizy mogą konsumować jeden wspólny model trasy.
- Zależności: `T08`, `T09`.

## Faza 4. Analizy wodne

### T11. Zaimplementować repozytorium JCWP

- Rozmiar: `M`
- Cel: odczytywać dane przestrzenne i atrybutowe potrzebne do analizy JCWP.
- Gotowy rezultat: repozytorium mapujące źródła danych do statusu i celów JCWP.
- Kryterium ukończenia: analiza JCWP nie odwołuje się bezpośrednio do plików źródłowych ani surowych nazw pól.
- Zależności: `T04`, `T05`, `T06`.

### T12. Zaimplementować repozytorium JCWPd

- Rozmiar: `M`
- Cel: odczytywać dane przestrzenne i atrybutowe potrzebne do analizy JCWPd.
- Gotowy rezultat: repozytorium mapujące źródła danych do statusu i celów JCWPd.
- Kryterium ukończenia: analiza JCWPd korzysta z jednego adaptera zamiast lokalnej logiki odczytu tabel.
- Zależności: `T04`, `T05`, `T06`.

### T13. Zaimplementować `SurfaceWaterAnalyzer`

- Rozmiar: `S`
- Cel: policzyć wynik JCWP dla wejściowych punktów i trasy.
- Gotowy rezultat: wynik w modelu domenowym gotowy do zapisania do raportu.
- Kryterium ukończenia: warstwa aplikacyjna może pobrać kompletny wynik JCWP jednym wywołaniem.
- Zależności: `T10`, `T11`.

### T14. Zaimplementować `GroundWaterAnalyzer`

- Rozmiar: `S`
- Cel: policzyć wynik JCWPd dla wejściowych punktów i trasy.
- Gotowy rezultat: wynik w modelu domenowym gotowy do zapisania do raportu.
- Kryterium ukończenia: warstwa aplikacyjna może pobrać kompletny wynik JCWPd jednym wywołaniem.
- Zależności: `T10`, `T12`.

## Faza 5. Ochrona przyrody

### T15. Zaimplementować loader danych RDOS

- Rozmiar: `M`
- Cel: zunifikować wczytywanie danych o formach ochrony z plików archiwalnych i przestrzennych.
- Gotowy rezultat: obsługa ZIP/SHP, wybór pól nazwy i kategorii oraz reprojekcja do CRS roboczego.
- Kryterium ukończenia: dane RDOS są dostępne dla analizy w jednolitym formacie niezależnie od źródłowego pliku.
- Zależności: `T04`, `T05`, `T06`.

### T16. Zaimplementować analizę przecięć i odległości

- Rozmiar: `S`
- Cel: określić, które formy ochrony są istotne dla trasy i jak daleko się znajdują.
- Gotowy rezultat: lista form ochrony do 10 km z minimalną odległością dla całej trasy.
- Kryterium ukończenia: analiza zwraca jeden znormalizowany wynik domenowy dla raportu.
- Zależności: `T10`, `T15`.

### T17. Dodać formatowanie odległości

- Rozmiar: `XS`
- Cel: sfinalizować sposób prezentacji odległości w wynikach użytkowych.
- Gotowy rezultat: odległości raportowane w kilometrach z dokładnością do 2 miejsc po przecinku.
- Kryterium ukończenia: raport zawsze prezentuje odległości w ustalonym standardzie.
- Zależności: `T16`.

## Faza 6. Działki

### T18. Zaimplementować klienty ULDK i EZiUDP

- Rozmiar: `M`
- Cel: odseparować komunikację z usługami zewnętrznymi od logiki analitycznej.
- Gotowy rezultat: adaptery HTTP z timeoutami, logowaniem i parserami odpowiedzi.
- Kryterium ukończenia: analiza działek korzysta wyłącznie z klientów infrastrukturalnych, bez bezpośrednich wywołań sieciowych w domenie.
- Zależności: `T04`, `T05`, `T06`.

### T19. Zaimplementować analizę działek po polilinii

- Rozmiar: `M`
- Cel: odtworzyć i uporządkować logikę wyznaczania działek przecinanych przez trasę.
- Gotowy rezultat: wykrywanie powiatów, pobieranie WFS lub fallback oraz deduplikacja po identyfikatorze działki.
- Kryterium ukończenia: wynik działek jest zwracany jako uporządkowana lista rekordów domenowych.
- Zależności: `T10`, `T18`, `T07`.

### T20. Zmapować wynik działek do arkusza raportowego

- Rozmiar: `S`
- Cel: przygotować wynik działek do docelowej prezentacji użytkowej.
- Gotowy rezultat: dane raportowe z kolumnami `numer_dzialki`, `obreb`, `uwagi`.
- Kryterium ukończenia: warstwa raportowania nie musi znać szczegółów pośrednich struktur działek.
- Zależności: `T19`.

## Faza 7. Orkiestracja i raport

### T21. Zaimplementować pipeline aplikacyjny

- Rozmiar: `S`
- Cel: spiąć wszystkie moduły w jeden uporządkowany przepływ wykonania.
- Gotowy rezultat: use case, który wczytuje dane, uruchamia analizy i składa wynik końcowy.
- Kryterium ukończenia: jedna komenda aplikacyjna może przejść od inputu do gotowego bundla raportowego.
- Zależności: `T10`, `T13`, `T14`, `T16`, `T19`, `T20`.

### T22. Zaimplementować writer XLSX

- Rozmiar: `M`
- Cel: wygenerować raport zgodny z biznesowym układem arkuszy i sekcji.
- Gotowy rezultat: plik XLSX z czterema arkuszami, blokami i scalonymi nagłówkami.
- Kryterium ukończenia: raport jest gotowy do ręcznego użycia bez dalszej obróbki układu.
- Zależności: `T17`, `T20`, `T21`.

### T23. Zaimplementować CLI

- Rozmiar: `S`
- Cel: dostarczyć cienki interfejs uruchomieniowy dla użytkownika końcowego.
- Gotowy rezultat: `gea run --input ... --output ... --config ...`.
- Kryterium ukończenia: CLI deleguje pracę do pipeline'u i nie zawiera logiki biznesowej.
- Zależności: `T04`, `T21`, `T22`.

## Faza 8. Jakość i bezpieczeństwo zmian

### T24. Dodać testy jednostkowe usług domenowych i parsera

- Rozmiar: `S`
- Cel: zabezpieczyć najważniejsze reguły wejścia i transformacji.
- Gotowy rezultat: testy parsera, detekcji EPSG, normalizacji osi, deduplikacji i agregacji.
- Kryterium ukończenia: krytyczne reguły domenowe są objęte automatyczną weryfikacją.
- Zależności: `T07`, `T08`, `T09`, `T10`.

### T25. Dodać testy integracyjne pipeline bez live API

- Rozmiar: `M`
- Cel: sprawdzić, że system działa jako całość bez zależności od zewnętrznych usług.
- Gotowy rezultat: fixture testujący przepływ `TXT -> bundle -> XLSX`.
- Kryterium ukończenia: pipeline daje przewidywalny wynik na danych testowych.
- Zależności: `T21`, `T22`.

### T26. Dodać testy kontraktowe adapterów danych

- Rozmiar: `S`
- Cel: zabezpieczyć parsery i adaptery integracyjne przed regresjami.
- Gotowy rezultat: testy dla ULDK, EZiUDP, WFS i RDOS na fixture'ach.
- Kryterium ukończenia: adaptery potrafią czytać spodziewane odpowiedzi i struktury danych.
- Zależności: `T15`, `T18`.

### T27. Dodać smoke test CLI

- Rozmiar: `XS`
- Cel: upewnić się, że aplikacja startuje poprawnie z prawidłowymi argumentami.
- Gotowy rezultat: prosty test uruchomienia interfejsu CLI.
- Kryterium ukończenia: wejście do aplikacji jest objęte podstawową kontrolą regresji.
- Zależności: `T23`.

## Sugerowana kolejność wdrażania

1. `T01` -> `T02` -> `T03` -> `T04`
2. `T05` -> `T06` -> `T07`
3. `T08` -> `T09` -> `T10`
4. `T11` -> `T12` -> `T13` -> `T14`
5. `T15` -> `T16` -> `T17`
6. `T18` -> `T19` -> `T20`
7. `T21` -> `T22` -> `T23`
8. `T24` -> `T25` -> `T26` -> `T27`

## Jak będziemy dalej pracować

- Ty wybierasz konkretne zadanie z listy.
- Ja najpierw doprecyzowuję zakres tego jednego zadania.
- Bez Twojej zgody nie przechodzę do implementacji kodu.
- Po zakończeniu zadania wspólnie wybieramy następne.
