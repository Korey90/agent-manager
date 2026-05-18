# 2026-05-18 - Google Calendar — Activity History, Sync All, Import Multi-Calendars, Stabilność UI

**Status:** Zakończone sukcesem
**Data realizacji:** 2026-05-18
**Czas trwania:** 1 dzień (sesja ciągła)

---

## Cel zadania

Rozszerzenie funkcjonalności kalendarza o:
1. Rejestrowanie akcji w Activity History przy tworzeniu i usuwaniu eventów z leadem
2. Masowy sync eventów do Google Calendar (Sync All)
3. Import eventów ze **wszystkich** kalendarzy Google (nie tylko primary — dotychczas święta, urodziny kontaktów i subskrybowane kalendarze były pomijane)
4. Stabilność widoku kalendarza po akcjach Livewire i nawigacji między miesiącami

---

## Zakres wykonanych prac

### Activity History
- Dodano dwa nowe typy ENUM w kolumnie `lead_activities.type`: `event_scheduled` oraz `event_deleted`
- Napisano dwie oddzielne migracje MySQL (MySQL wymaga osobnych `ALTER TABLE` dla ENUM)
- Uzupełniono `LeadActivity` o ikony i kolory dla nowych typów:
  - `event_scheduled` → `heroicon-m-calendar-days`, `text-cyan-500`, `bg-cyan-100`
  - `event_deleted` → `heroicon-m-calendar`, `text-red-400`, `bg-red-100`
- `ViewLead::createLeadEvent()` — log `event_scheduled` po zapisaniu eventu z tytułem i typem
- `ViewLead::deleteLeadEvent()` — pobranie tytułu PRZED usunięciem → log `event_deleted`

### Google Calendar — Sync All + Auto-sync
- `CalendarPage::syncAllToGoogle()` — masowy push wszystkich eventów bez `google_event_id`; rozróżnia:
  - Wszystkie nieudane → notyfikacja `danger`
  - Część nieudanych → notyfikacja `warning` z licznikami
  - Sukces → notyfikacja `success`
- `CalendarPage::quickCreate()` — po zapisaniu eventu automatyczny push do Google, jeśli konto podłączone
- Poprawione retry logic w `GoogleCalendarService::pushEvent()` — proaktywny refresh tokenu + retry na HTTP 401

### Google Calendar — Import ze wszystkich kalendarzy
- `GoogleCalendarService::fetchCalendarList()` — nowa metoda: `GET /users/me/calendarList` (max 250 kalendarzy)
  - Obsługa wygasłego tokenu + retry na 401
  - Filtruje usunięte kalendarze (`deleted: true`)
  - Loguje listę kalendarzy do `laravel.log` (ułatwia diagnostykę)
- `GoogleCalendarService::fetchEventsFromGoogle()` — dodany opcjonalny param `?string $calendarId = null`
  - **Kluczowy bug fix:** `rawurlencode($calId)` — ID kalendarzy świąt zawierają `#` (np. `pl.polish#holiday@group.v.calendar.google.com`), który w URL był traktowany jako fragment (obcinał żądanie do złego endpointu)
  - Loguje błędy per-kalendarz z `calendar_id` dla łatwej diagnostyki
- `CalendarPage::importFromGoogle()` — całkowite przepisanie pętli importu:
  - Pobiera listę wszystkich kalendarzy (`fetchCalendarList`)
  - Iteruje każdy kalendarz i pobiera eventy (`fetchEventsFromGoogle`)
  - Deduplikuje po `google_event_id` (bezpieczne wielokrotne klikanie)
  - Pomija anulowane eventy (`status = 'cancelled'`)
  - Loguje per-kalendarz ilość pobranych eventów

### Stabilność widoku kalendarza
- **`wire:ignore`** na zewnętrznym `div` karty kalendarza — Livewire Morphdom przestał niszczyć DOM FullCalendara po akcjach (dodanie eventu, sync, import)
- **Loading overlay** jako `position: absolute` zamiast `x-show="!loading"` na `#calendar` — div `#calendar` zawsze w DOM, FullCalendar nie traci kontekstu przy nawigacji poprzedni/następny miesiąc
- **`googleConnected`** jako Alpine.js property zamiast `@if($googleConnected)` w Blade — poprawna hydration po każdej akcji Livewire (przycisk sync w modalach nie znikał)

---

## Użyte agenty i skille

- Agent: **WebsiteExpert** (główny wykonawca)
- Skill: `task-completion-report` (ten raport)
- Narzędzia: `multi_replace_string_in_file`, `read_file`, `grep_search`, `run_in_terminal`

---

## Zmodyfikowane / utworzone pliki

| Plik | Typ zmiany |
|------|-----------|
| `app/Models/LeadActivity.php` | Modyfikacja — nowe typy ENUM + ikony/kolory |
| `app/Filament/Resources/LeadResource/Pages/ViewLead.php` | Modyfikacja — log event_scheduled + event_deleted |
| `app/Services/Calendar/GoogleCalendarService.php` | Modyfikacja — `fetchCalendarList()`, `rawurlencode`, retry logic |
| `app/Filament/Pages/CalendarPage.php` | Modyfikacja — syncAllToGoogle, importFromGoogle (multi-cal), auto-sync |
| `resources/views/filament/pages/calendar.blade.php` | Modyfikacja — `wire:ignore`, overlay, Alpine googleConnected |
| `database/migrations/2026_05_17_224200_add_event_scheduled_type_to_lead_activities.php` | Nowy plik — ENUM migration |
| `database/migrations/2026_05_17_224500_add_event_deleted_type_to_lead_activities.php` | Nowy plik — ENUM migration |

---

## Walidacja końcowa

- ✅ Testy PHPUnit — **265/265** (było 260 przed sesją)
- ✅ Migracje uruchomione na MySQL (`php artisan migrate`)
- ✅ Multi-tenancy compliance — `business_id` w imporcie i syncach
- ✅ Brak regresji — wszystkie poprzednie testy zielone
- ✅ Security — `strip_tags()` na wszystkich polach tekstowych pobieranych z Google API

---

## Uwagi i rekomendacje

### Bug który warto zapamiętać
Identyfikatory kalendarzy Google typu `pl.polish#holiday@group.v.calendar.google.com` zawierają znak `#`, który w URL bez enkodowania jest traktowany jako delimiter fragmentu. Guzzle/Laravel Http Facade nie enkoduje automatycznie gotowych URL-i — trzeba ręcznie `rawurlencode()` segment ścieżki z ID kalendarza.

### Ograniczenia obecnej implementacji
- Importowane eventy zawsze dostają `type = 'meeting'` — święta wyglądają jak spotkania. Można poprawić: jeśli `calendar['id']` zawiera `#holiday`, ustawić `type = 'reminder'`
- Zakres importu jest hardcoded: ostatnie 30 dni + następne 90 dni — można wyeksponować jako konfigurowalny
- Przy dużej liczbie kalendarzy (>10) import może być wolny — brak paginacji na liście kalendarzy (Google API: max 250 per request)

### Potencjalne ryzyka
- Tokeny OAuth mogą wygasnąć bez refresh_tokenu (gdy user nie zaakceptował `access_type=offline`). Obsłużone przez retry z `refreshAccessToken()`, ale bez refresh tokenu połączenie jest jednorazowe
- `fetchEventsFromGoogle` loguje ostrzeżenie gdy kalendarz zwraca błąd — warto monitorować logi po wdrożeniu

---

## Next steps (opcjonalne)

- Dodać filtr `type` przy imporcie (święta → `reminder`, urodziny → `reminder`, inne → `meeting`)
- Rozważyć dwukierunkowy sync (zmiany z Google aktualizują lokalne eventy)
- Dodać scheduler do auto-importu (np. `schedule()->dailyAt('06:00')`)

---

**Raport wygenerowany automatycznie przez WebsiteExpert**
