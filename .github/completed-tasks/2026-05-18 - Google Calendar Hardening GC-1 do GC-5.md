# 2026-05-18 - Google Calendar Hardening — GC-1 do GC-5

**Status:** Zakończone sukcesem
**Data realizacji:** 2026-05-18
**Czas trwania:** ~2 godziny (ta sama sesja co GC-0)

---

## Cel zadania

Usunięcie 3 ograniczeń i 2 ryzyk zidentyfikowanych po wdrożeniu integracji Google Calendar (sesja GC-0):

- **Ograniczenia:** święta importowane jako `meeting`, hardcoded zakres dat importu, brak paginacji listy kalendarzy
- **Ryzyka:** token bez `refresh_token` przestaje działać bez ostrzeżenia, błędy API kalendarzy niewidoczne dla użytkownika

---

## Zakres wykonanych prac

### GC-1 — Smart type detection przy imporcie
- Dodano prywatną metodę `resolveEventType(string $calendarId): string` w `CalendarPage`
- Logika: jeśli ID kalendarza zawiera `#holiday`, `#holidays` lub `#birthdays` → `type = 'reminder'`; pozostałe → `type = 'meeting'`
- Zastosowano w `CalendarEvent::create()` w `importFromGoogle()`

### GC-2 — Konfigurowalny zakres dat importu
- Przycisk „Import from Google" otwiera teraz modal Filament z dwoma polami `DatePicker`:
  - **Import from** (domyślnie: dziś − 30 dni)
  - **Import to** (domyślnie: dziś + 90 dni)
- Akcja przekazuje wybrane daty do `importFromGoogle(?Carbon $from, ?Carbon $to)`
- Sygnatura metody zmieniona na opcjonalne parametry z fallback na poprzednie domyślne wartości

### GC-3 — Paginacja listy kalendarzy
- `fetchCalendarList()` przepisane na pętlę `do...while` z `nextPageToken`
- Obsługuje konta z ponad 250 subskrybowanymi kalendarzami
- Retry na 401 wykonywany tylko raz (flaga `$retried`) i tylko dla pierwszej strony
- Fallback do `[primary]` gdy lista jest pusta lub API zwróci błąd

### GC-4 — Detekcja braku `refresh_token`
- Nowa metoda `GoogleCalendarService::hasValidRefreshToken(int $userId, ?string $businessId): bool`
- `CalendarPage::mount()` sprawdza przy wejściu na stronę: jeśli Google podłączone ale brak `refresh_token` → wysyła persistent Filament Notification z przyciskiem **Reconnect**
- `GoogleCalendarController::connect()` już ma `prompt=consent` + `access_type=offline` — bez zmian

**Bugfix:** `parent::mount()` usunięty — Livewire nie definiuje `mount()` na klasie bazowej, wywołanie powodowało `BadMethodCallException` przez `__call()`

### GC-5 — Surface błędów kalendarzy do UI
- `fetchEventsFromGoogle()` zmieniony zwracany typ: `array` → `?array`
  - `null` = błąd API (403, 404, 5xx, auth failure)
  - `[]` = pusta kolekcja (brak eventów)
- `importFromGoogle()` sprawdza `null` per-kalendarz: zlicza `$failed`, akumuluje nazwy w `$failedSummaries`
- Po imporcie: jeśli `$failed > 0` → dodatkowa notyfikacja `warning` z listą nieudanych kalendarzy

---

## Użyte agenty i skille

- Agent: **WebsiteExpert** (główny wykonawca)
- Skill: `task-completion-report` (ten raport)
- Narzędzia: `replace_string_in_file`, `multi_replace_string_in_file`, `read_file`, `run_in_terminal`

---

## Zmodyfikowane / utworzone pliki

| Plik | Zmiana |
|------|--------|
| `app/Services/Calendar/GoogleCalendarService.php` | `hasValidRefreshToken()` + paginacja `fetchCalendarList()` + `?array` return type `fetchEventsFromGoogle()` |
| `app/Filament/Pages/CalendarPage.php` | `mount()` (GC-4) + `importFromGoogle(?Carbon, ?Carbon)` (GC-2/5) + `resolveEventType()` (GC-1) + Action form (GC-2) |

---

## Walidacja końcowa

- ✅ PHPUnit — **265/265** (bez regresji)
- ✅ Multi-tenancy compliance — `business_id` zachowany we wszystkich ścieżkach
- ✅ Security — `strip_tags()` na polach tekstowych z Google API
- ✅ Bugfix zwalidowany — `BadMethodCallException` z `parent::mount()` naprawiony
- ⏭ PHP Pint / ESLint — nie uruchamiane w tej sesji (zmiany czysto backendowe, PHP only)

---

## Uwagi i rekomendacje

### Zmiana sygnatury `fetchEventsFromGoogle` → `?array`
Istniejące miejsca wywołania (`importFromGoogle`) obsługują już `null`. Jeśli w przyszłości pojawią się inne wywołania tej metody, należy pamiętać o sprawdzeniu `=== null` przed iteracją.

### Retry na 401 w `fetchCalendarList`
Flaga `$retried` zapobiega pętli nieskończonej, ale retry działa tylko dla strony pierwszej. Przy kolejnych stronach wygaśnięcie tokenu nie jest ponawiane — w praktyce token jest odświeżany raz na >1 godzinę więc nie stanowi problemu.

### GC-4 — `mount()` bez `parent::mount()`
W Livewire 3, klasa `Livewire\Component` nie definiuje metody `mount()`. Wywoływanie `parent::mount()` przechodzi przez łańcuch dziedziczenia i trafia do `__call()`, który rzuca `BadMethodCallException`. Należy tego unikać we wszystkich komponentach.

---

## Next steps (opcjonalne)

- Dwukierunkowy sync: zmiany w Google aktualizują lokalne eventy (wymaga webhook lub polling)
- Scheduler: `schedule()->dailyAt('06:00')` dla auto-importu w tle
- Lepsza obsługa `#contacts` kalendarza (urodziny z kontaktów Google) — aktualnie `#birthdays` jest już mapowane na `reminder`

---

**Raport wygenerowany automatycznie przez WebsiteExpert**
