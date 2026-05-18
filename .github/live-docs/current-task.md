# Current Task

**Status:** Brak aktywnego zadania

**Last completed:** Google Calendar Hardening GC-1–GC-5 — 2026-05-18

**Last Updated:** 2026-05-18

---

## Plan zadań

### GC-1 — Smart type detection przy imporcie
**Co:** Podczas importu z Google przypisywać typ eventu na podstawie rodzaju kalendarza:
- ID zawiera `#holiday` lub `#holidays` → `type = 'reminder'`
- ID zawiera `#birthdays` → `type = 'reminder'`
- Pozostałe → `type = 'meeting'` (jak dotychczas)

**Gdzie:** `CalendarPage::importFromGoogle()` — dodać helper `resolveEventType(string $calendarId): string`

**Szacunek:** ~15 min

---

### GC-2 — Konfigurowalny zakres dat importu
**Co:** Przed importem pokazywać modal z dwiema datami (od / do). Domyślnie: -30 dni / +90 dni.

**Gdzie:** `CalendarPage` — zamienić `Action::make('importFromGoogle')` na akcję z `form()` (Filament Action Form)

**Pola formularza:**
```php
DatePicker::make('from')->label('Od')->default(now()->subDays(30))
DatePicker::make('to')->label('Do')->default(now()->addDays(90))
```

**Szacunek:** ~30 min

---

### GC-3 — Paginacja listy kalendarzy
**Co:** `fetchCalendarList()` obsługuje tylko pierwszą stronę (max 250). Dodać pętlę `nextPageToken` analogicznie do `fetchEventsFromGoogle()`.

**Gdzie:** `GoogleCalendarService::fetchCalendarList()`

**Szacunek:** ~15 min

---

### GC-4 — Detekcja braku refresh_token + wymuszony reconnect
**Co:** Jeśli `$token->refresh_token` jest `null` i token wygasł — połączenie jest jednorazowe. Pokazać użytkownikowi ostrzeżenie z przyciskiem "Reconnect Google Calendar" (force `prompt=consent`).

**Gdzie:**
- `GoogleCalendarService::hasValidRefreshToken(int $userId, ?string $businessId): bool`
- `CalendarPage::mount()` — sprawdzenie i `Notification::make()->warning()->persistent()`
- `GoogleCalendarController::connect()` — już ma `prompt=consent`, bez zmian

**Szacunek:** ~20 min

---

### GC-5 — Surface błędów sync kalendarzy do UI
**Co:** Gdy `fetchEventsFromGoogle()` dla konkretnego kalendarza zwraca błąd, obecnie tylko loguje. Zmienić tak by `importFromGoogle()` zliczał błędy i pokazywał użytkownikowi: "X kalendarzy nie udało się pobrać".

**Gdzie:** `CalendarPage::importFromGoogle()` — zliczanie `$failed`; notyfikacja `warning` gdy `$failed > 0`

**Szacunek:** ~20 min

---

## Kolejność realizacji

1. GC-3 (prosta, fundament dla GC-1 / GC-5)
2. GC-1 (prosta, duża wartość UX)
3. GC-4 (bezpieczeństwo tokenów — wysoki priorytet)
4. GC-5 (surface errorów)
5. GC-2 (UX — konfigurowalny zakres, ostatni bo wymaga Filament Action Form)

**Last Updated:** 2026-05-18

**Implemented:**
- Activity History: nowe typy ENUM `event_scheduled` + `event_deleted` (2 migracje)
- `LeadActivity` icons/colors dla obu nowych typów
- `ViewLead.createLeadEvent()`: log `event_scheduled` po zapisaniu eventu
- `ViewLead.deleteLeadEvent()`: log `event_deleted` po usunięciu
- `CalendarPage.syncAllToGoogle()`: masowy push eventów bez `google_event_id`
- `CalendarPage.importFromGoogle()`: import ze WSZYSTKICH kalendarzy (primary + święta + urodziny)
- `CalendarPage.quickCreate()`: auto-sync do Google gdy konto podłączone
- `GoogleCalendarService.fetchCalendarList()`: pobieranie listy kalendarzy z `GET /users/me/calendarList`
- `GoogleCalendarService.fetchEventsFromGoogle()`: opcjonalny param `calendarId` + `rawurlencode` ID
- `wire:ignore` na divie karty kalendarza (Livewire Morphdom fix)
- Overlay loadingu jako absolute div zamiast `x-show` na `#calendar` (FullCalendar DOM fix)
- Alpine `googleConnected` jako property zamiast Blade `@if` (hydration fix)

**Tests:** 265/265 ✅ (było 260, +5 z nowych funkcji)

**Last Updated:** 2026-05-18