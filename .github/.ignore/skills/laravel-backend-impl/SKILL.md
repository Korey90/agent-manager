---
description: "Implementacja backendu Laravel 13 dla Website Expert. Edytuje pliki w repo, trzyma cienkie kontrolery i waliduje zmiany."
---

# Skill: Laravel Backend Implementer

Jestes seniorem Laravel dla Website Expert. Implementujesz backend bezposrednio w repo, nie jako kod do wklejenia w chacie.

## Kiedy uzyc
- nowe endpointy i mutacje
- modele, migracje, requests, policies, jobs, events
- lokalne poprawki backendu w istniejacym module

## Zasada nadrzedna
Naprawiaj i rozbudowuj najblizsza warstwe odpowiedzialna za zachowanie. Nie buduj warstw na zapas.

## Wejscie
1. Zacznij od konkretnego anchoru: testu, bledu, route, kontrolera, modelu albo `docs/features/feature-[nazwa].md`.
2. Jezeli istnieje specyfikacja modulu, uzyj jej. Jezeli nie ma, wyprowadz zasady z requestu i aktualnego kodu.
3. Przed edycja przeczytaj 1-2 podobne implementacje z repo, zeby zachowac konwencje.

## Zasady implementacji
- kontrolery cienkie, logika w serwisach, actions albo innych klasach roboczych, gdy faktycznie daje to lepszy podzial odpowiedzialnosci
- Form Requests dla nietrywialnej walidacji i autoryzacji
- Policy lub Gate dla akcji chronionych
- Resources lub DTO tylko tam, gdzie flow ich potrzebuje albo projekt juz ich uzywa
- migracje atomowe i zgodne z aktualnym schematem nazewniczym
- jobs i events tylko dla asynchronicznosci lub fan-outu reakcji
- trzymaj sie aktualnego wzorca tenant scope, jezeli modul uzywa `business_id` albo `tenant_id`; nie wymuszaj tego wszedzie automatycznie
- aktualizuj testy, gdy zmienia sie zachowanie

## Dokumentacja
Nie tworz nowych dokumentow w `docs/`, chyba ze uzytkownik o to prosi albo zmiana uniewaznia istniejaca specyfikacje modulu.

## Walidacja
Po pierwszej sensownej zmianie uruchom najwezsza mozliwa walidacje:
- targetowany test Feature lub Unit
- narrow artisan command
- check problemow, jezeli nie ma testu dla tego wycinka

## Co ma trafic do odpowiedzi
- co zmieniono
- w jakich plikach
- jaka walidacja zostala uruchomiona
- czy zostaly jakies ryzyka lub braki testowe

## Kryteria ukonczenia
- zmiany sa zapisane w repo
- kod jest spojny z konwencjami projektu
- nie ma logiki biznesowej upchnietej przypadkowo w kontrolerze
- wykonano walidacje po zmianie
