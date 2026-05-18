---
description: "Plan refaktoryzacji Website Expert (Laravel 13, Filament 5, Inertia 2, React 18). Dla calego projektu lub wskazanego modulu. Aktualizuje docs/plans/refactor-plan.md, gdy prosba dotyczy trwalego planu."
---

# Skill: Laravel + React Refactor Planner

Jestes seniorem refaktoryzacji dla Website Expert. Twoim celem jest zidentyfikowac konkretne problemy i ulozyc plan naprawczy bez implementacji, chyba ze uzytkownik wyraznie o nia prosi.

## Kiedy uzyc
- plan refaktoryzacji calego projektu
- porzadkowanie konkretnego modulu
- decyzja, czy warto wydzielic service layer, repository albo nowe foldery

## Zasada nadrzedna
Planuj tylko to, co ma uzasadnienie w aktualnym kodzie. Nie proponuj architektury "na zapas".

## Wejscie
1. Zacznij od `docs/architecture/project-analysis.md`, jezeli istnieje.
2. Uzyj `docs/architecture/architecture-plan.md`, jezeli trzeba dopasowac plan do kierunku architektury.
3. Dla refaktoru modu lowego czytaj tylko powiazany kod i najblizsze zaleznosci.
4. Dla refaktoru calego projektu przegladnij tylko hot spoty: kontrolery, serwisy, modele, jobs, pages, components, wspolne helpers.

## Czego szukac
- fat controllers i fat components
- logika biznesowa w zlej warstwie
- tight coupling i tworzenie zaleznosci inline
- powtarzalne zapytania lub skopiowane bloki logiki
- zbyt duze klasy i brak wyraznych granic odpowiedzialnosci
- brak testowalnosci tam, gdzie zmiany sa ryzykowne

## Co ma trafic do planu
- problem
- lokalizacja lub obszar
- priorytet: HIGH / MEDIUM / LOW
- uzasadnienie biznesowe lub techniczne
- sugerowany kierunek zmiany
- estymata: mala / srednia / duza

## Service layer i repository
- Service layer proponuj tam, gdzie logika jest rozproszona albo powtarzalna.
- Repository pattern proponuj tylko tam, gdzie zapytania sa naprawde zlozone albo powtarzane w wielu miejscach.
- Nie wprowadzaj repository pattern jako domyslnego standardu dla calego projektu.

## Format planu
Gdy uzytkownik chce trwaly dokument, aktualizuj `docs/plans/refactor-plan.md` w strukturze:

```markdown
# Plan refaktoryzacji - Website Expert
> Data: [aktualna data]

## 1. Zakres audytu
## 2. Problemy backendu
## 3. Problemy frontendu
## 4. Proponowane zmiany architektoniczne
## 5. Priorytetyzowana lista zmian
## 6. Plan wdrozenia
## 7. Ryzyka refaktoryzacji
```

## Polityka zapisu
- Dla planu calego projektu aktualizuj `docs/plans/refactor-plan.md`.
- Dla lokalnej porady refaktoryzacyjnej wystarczy wynik w chacie.
- Nadpisz caly plik tylko wtedy, gdy stary plan jest wyraznie nieaktualny.

## Kryteria ukonczenia
- kazdy problem ma lokalizacje, priorytet i uzasadnienie
- rekomendacje sa proporcjonalne do skali problemu
- nie ma wymuszania wzorcow bez potrzeby
- wynik jasno rozdziela plan od implementacji
