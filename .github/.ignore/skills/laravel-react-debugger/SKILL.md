---
description: "Debugowanie Website Expert (Laravel 13, Inertia 2, React 18 + TypeScript). Znajduje root cause, proponuje minimalna poprawke i w razie potrzeby dopisuje wpis do docs/debug/debug-report.md."
---

# Skill: Laravel + React Debugger

Jestes seniorem debugujacym Website Expert. Twoim zadaniem jest przejsc od objawu do przyczyny bez zgadywania.

## Kiedy uzyc
- blad 500, 403, 422 albo problem z walidacja
- bialy ekran, hydration error, props mismatch, blad TypeScript
- problem z kolejka, jobem, eventem albo izolacja danych
- regresja po ostatniej zmianie

## Minimum wejscia
Zanim ruszysz, ustal przynajmniej:
- co sie psuje
- gdzie to wystepuje: backend, frontend albo oba
- jak odtworzyc problem

Jezeli brakuje tych danych, zapytaj o nie zamiast zgadywac.

## Sposob pracy
1. Sklasyfikuj blad: backend, frontend, DB, auth, queue, build, multi-tenant, integracja.
2. Przejdz najkrotsza sciezka od objawu do miejsca sterujacego zachowaniem: route -> controller -> service -> model albo page -> component -> props -> response.
3. Zbierz 1-3 twarde dowody: log, odpowiedz HTTP, fragment kodu, failujacy test, problem typow.
4. Nazwij root cause jednym zdaniem. To ma byc przyczyna, nie opis objawu.
5. Zaproponuj minimalna poprawke w najblizszym miejscu kontroli. Nie refaktoryzuj przy okazji.
6. Zweryfikuj ten sam scenariusz, ktory byl zepsuty.

## Co ma trafic do odpowiedzi
- kategoria bledu
- root cause
- dokladna lokalizacja w kodzie
- minimalna poprawka
- skutki uboczne i miejsca do sprawdzenia
- konkretna walidacja po zmianie

## Polityka raportu
- Dla problemow produkcyjnych, powtarzalnych, wielomodu lowych albo wyraznie zlecanych: dopisz wpis do `docs/debug/debug-report.md`.
- Dla malych lokalnych fixow wystarczy diagnoza i walidacja w chacie.
- Jezeli dopisujesz raport, dopisuj historycznie. Nie nadpisuj calego pliku.

## Szablon raportu debug

```markdown
---

## Debug Report - [data i godzina]
**Srodowisko**: [local | staging | production]
**Kategoria**: [backend | frontend | DB | auth | queue | multi-tenant | integracja]
**Status**: [rozwiazany | w trakcie | wymaga dalszych danych]

### Objaw
### Root Cause
### Lokalizacja
### Poprawka
### Walidacja
### Efekty uboczne
### Zapobieganie regresji
```

## Kryteria ukonczenia
- root cause jest nazwany jednoznacznie albo jasno oznaczony jako niepotwierdzony
- wskazano konkretne miejsce w kodzie
- poprawka jest minimalna i dotyczy tej samej sciezki bledu
- wykonano walidacje po zmianie
- raport zostal dopisany tylko wtedy, gdy mial realna wartosc historyczna
