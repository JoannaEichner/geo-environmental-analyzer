# Geo Environmental Analyzer MVP Plan

## Cel

Nowy projekt ma dostarczyć profesjonalne, modularne i testowalne narzędzie do end-to-end analizy środowiskowej. Aplikacja ma wczytywać jeden plik TXT z punktami, interpretować punkty jako jedną trasę i generować raport XLSX gotowy do dalszej pracy.

## Zakres MVP

MVP obejmuje cztery analizy:

1. Analizę działek przecinanych przez trasę.
2. Analizę jednolitych części wód powierzchniowych (JCWP).
3. Analizę jednolitych części wód podziemnych (JCWPd).
4. Analizę form ochrony przyrody i minimalnych odległości.

## Kontrakt wejścia

- Wejściem jest jeden plik TXT.
- Canonical format wiersza: `nr<TAB>nazwa<TAB>x<TAB>y`.
- Parser może tolerować proste alternatywne separatory jako fallback, ale format tab-separated jest obowiązujący.
- Punkty są interpretowane jako jedna trasa w kolejności występowania w pliku.
- Analiza działek działa na polilinii zbudowanej z punktów.
- Analizy wód i ochrony przyrody korzystają z punktów należących do tej samej trasy.

## Kontrakt wyjścia

Wynikiem MVP jest jeden plik `XLSX` z czterema arkuszami:

- `01_Dzialki`
- `02_Wody_Status`
- `03_Wody_Cele`
- `04_Ochrona`

### Arkusz `01_Dzialki`

- Kolumny: `numer_dzialki`, `obreb`, `uwagi`.
- Kolumna `uwagi` pozostaje pusta do ręcznego uzupełnienia.
- Działki są deduplikowane po pełnym identyfikatorze działki.
- Kolejność rekordów odpowiada kolejności przecięcia trasy.

### Arkusz `02_Wody_Status`

Arkusz zawiera dwa bloki dwukolumnowe.

Blok JCWP:

- Scalony nagłówek: kod i nazwa JCWP.
- Wiersze:
  - `status JCWP`
  - `monitorowana`
  - `stan ogólny`
  - `ocena ryzyka`

Blok JCWPd:

- Scalony nagłówek: kod i nazwa JCWPd.
- Wiersze:
  - `monitorowana`
  - `stan chemiczny`
  - `stan ilościowy`
  - `stan JCWPd`
  - `ocena ryzyka`

### Arkusz `03_Wody_Cele`

Arkusz zawiera dwa bloki dwukolumnowe.

Blok JCWP:

- Scalony nagłówek: kod i nazwa JCWP.
- Wiersze:
  - `cel/potencjał ekologiczny`
  - `cel chemiczny`

Blok JCWPd:

- Scalony nagłówek: kod i nazwa JCWPd.
- Wiersze:
  - `cel ilościowy`
  - `cel chemiczny`

### Arkusz `04_Ochrona`

- Kolumny: `forma_ochrony`, `minimalna_odleglosc_km`.
- Zawiera tylko formy ochrony w promieniu maksymalnie 10 km od dowolnego punktu z trasy.
- Wartość w wierszu jest minimalną odległością od całej trasy.
- Odległości są raportowane w kilometrach z dokładnością do 2 miejsc po przecinku.

## Docelowa architektura

Projekt ma być rozwijany jako aplikacja warstwowa:

- `application` odpowiada za orkiestrację pipeline'u.
- `domain` zawiera modele, reguły biznesowe i porty.
- `infrastructure` zawiera wejście/wyjście, konfigurację, adaptery danych i klientów zewnętrznych.
- `analyses` zawiera implementacje poszczególnych analiz oparte o kontrakty domenowe.

Docelowa struktura pakietu:

```text
src/geo_environmental_analyzer/
  cli.py
  application/run_pipeline.py
  domain/models.py
  domain/protocols.py
  domain/services.py
  analyses/parcels.py
  analyses/surface_water.py
  analyses/groundwater.py
  analyses/protected_areas.py
  infrastructure/config.py
  infrastructure/input/points_txt.py
  infrastructure/geodata/jcwp_repository.py
  infrastructure/geodata/jcwpd_repository.py
  infrastructure/geodata/rdos_repository.py
  infrastructure/gateways/uldk_client.py
  infrastructure/gateways/eziudp_client.py
  infrastructure/reporting/xlsx_writer.py
```

## Publiczne interfejsy

- CLI: `gea run --input <points.txt> --output <report.xlsx> --config <settings.toml>`

Docelowe typy domenowe:

- `InputPoint`
- `OrderedRoute`
- `ParcelRecord`
- `SurfaceWaterResult`
- `GroundWaterResult`
- `ProtectedAreaDistance`
- `AnalysisBundle`

Docelowe porty/protokoły:

- `PointReader`
- `ParcelAnalyzer`
- `SurfaceWaterAnalyzer`
- `GroundWaterAnalyzer`
- `ProtectedAreaAnalyzer`
- `ReportWriter`

## Zasady konfiguracji

- Ścieżki do danych, URL-e i parametry środowiskowe nie mogą być zaszyte w kodzie.
- Konfiguracja ma być ładowana z `settings.toml`.
- W konfiguracji powinny znaleźć się m.in.:
  - źródła danych JCWP i JCWPd,
  - lokalizacja danych RDOS,
  - URL ULDK,
  - URL EZiUDP,
  - timeouty,
  - limit odległości 10 km.

## Zasady jakościowe

- Projekt ma przestrzegać zasad SOLID.
- Kod ma być zgodny z PEP 8.
- CLI ma pozostać cienką warstwą bez logiki biznesowej.
- Logika domenowa ma być testowalna niezależnie od adapterów infrastrukturalnych.
- Integracje z zewnętrznymi usługami mają być odseparowane od logiki analitycznej.

## Plan testów MVP

- Testy jednostkowe parsera wejścia.
- Testy jednostkowe detekcji EPSG PL-2000 i normalizacji osi.
- Testy jednostkowe budowania trasy i deduplikacji działek.
- Testy jednostkowe agregacji minimalnych odległości.
- Testy jednostkowe mapowania danych JCWP i JCWPd do modeli domenowych.
- Testy integracyjne pełnego przepływu `TXT -> AnalysisBundle -> XLSX` bez live API.
- Testy kontraktowe parserów odpowiedzi ULDK, EZiUDP, WFS i loadera RDOS na fixture'ach.
- Smoke test CLI.

## Założenia wykonawcze

- MVP jest aplikacją CLI, bez GUI i bez bazy danych.
- Testy automatyczne nie powinny wykonywać wywołań live do usług sieciowych.
- Analiza działek może używać EZiUDP, ULDK i WFS, ale wyłącznie przez adaptery infrastruktury.
- Wiedza projektowa i domenowa ma być utrzymywana na bieżąco w `AGENTS.md`, gdy tylko plik zostanie dodany do repo.
