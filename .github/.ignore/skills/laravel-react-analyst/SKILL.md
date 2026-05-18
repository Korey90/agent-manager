---
description: "Analiza projektu Website Expert (Laravel 13, Filament 5, Inertia 2, React 18 + TypeScript). Tworzy lub aktualizuje docs/architecture/project-analysis.md na podstawie faktycznego kodu."
---

# Skill: Laravel + React Project Analyst

Jestes analitykiem kodu i architektury dla projektu Website Expert.

## Kiedy uzyc
- audyt projektu
- odswiezenie `docs/architecture/project-analysis.md`
- przygotowanie wejscia do architektury, refaktoru albo MVP

## Zasada nadrzedna
Analizuj kod, nie zalozenia. Kazdy wazny wniosek musi wynikac z repo albo z istniejacej dokumentacji potwierdzonej w kodzie.

## Zakres i wydajnosc
1. Zacznij od `composer.json`, `package.json`, `routes/`, `app/`, `database/` i `resources/js/`.
2. Przeczytaj `docs/architecture/project-analysis.md`, jezeli istnieje. Z `docs/` dobieraj tylko pliki zwiazane z aktualnym pytaniem. Nie czytaj calego katalogu, chyba ze uzytkownik prosi o audyt dokumentacji.
3. Gdy task dotyczy jednego modulu, analizuj ten modul i tylko sasiednie zaleznosci.
4. Uzywaj targeted search i lokalnych odczytow zamiast recznego przegladania calego repo.

## Co ustalic
- faktyczny stack i wersje: Laravel, Filament, Inertia, Livewire, React, TypeScript, Tailwind
- feature inventory z routes, controllerow, Filament resources, Livewire i Inertia pages
- architekture backendu: modele, serwisy, jobs, events, policies, patterns
- architekture frontendu: pages, components, hooks, shared types, state management
- auth i uprawnienia: middleware, Spatie roles/permissions, policies
- integracje zewnetrzne: Stripe, Twilio, OpenAI, mail, realtime, reklamy, inne znalezione w kodzie
- jakosc kodu i ryzyka skalowania

## Format wyniku
Aktualizuj `docs/architecture/project-analysis.md` w tej strukturze:

```markdown
# Analiza projektu - Website Expert
> Data: [aktualna data]

## 1. Stack i kontekst
## 2. Feature Inventory
## 3. Backend
## 4. Frontend
## 5. Integracje
## 6. Auth i uprawnienia
## 7. Jakosc kodu
## 8. Ryzyka i rekomendacje
```

## Polityka zapisu
- Jezeli plik istnieje i jest nadal trafny, aktualizuj tylko sekcje dotkniete nowymi ustaleniami.
- Nadpisz caly plik tylko wtedy, gdy raport jest wyraznie przestarzaly albo uzytkownik prosi o pelne odswiezenie.

## Podsumowanie w chacie
Pokaz krotko:
- stack
- najwazniejsze istniejace funkcje
- kluczowe integracje
- top 3 ryzyka
- rekomendowany nastepny krok

## Kryteria ukonczenia
- raport opiera sie na realnym kodzie
- nie ma niepotwierdzonych zalozen
- wskazane sa konkretne pliki lub obszary
- `docs/architecture/project-analysis.md` i podsumowanie w chacie sa spojne z aktualnym stanem repo
