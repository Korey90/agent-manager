# Agent Manager — v1.0.1

Desktopowy menedżer agentów AI z graficznym interfejsem (PyQt6).

## Jaki problem rozwiązuje?

Zarządzanie agentami AI w projekcie szybko staje się chaotyczne — dziesiątki promptów, skilli, hooków i reguł rozrzucone w plikach bez struktury, bez walidacji, bez wizualizacji powiązań.

**Agent Manager** daje graficzny interfejs do:
- **definiowania agentów** z rolą, modelem LLM i zestawem zasad,
- **przypisywania im procedur** (skille — kroki, exit criteria, anti-rationalizations),
- **automatycznych akcji** (hooki wyzwalane zdarzeniami cyklu życia),
- **walidacji spójności** — wykrywanie martwych referencji, brakujących pól,
- **uruchamiania agentów** bezpośrednio z aplikacji (via litellm),
- **eksportu** do `AGENTS.md` lub reguł `.cursor/rules/*.mdc`.

Wszystko zapisane jako pliki Markdown w `.github/` — czytelne i wersjonowalne, w pełni kompatybilne z GitHub Copilot.

## Funkcje

| Zakładka | Opis |
|---|---|
| **🤖 Agenci** | Tworzenie i edycja agentów: rola, model LLM, przypisane skille/hooki/instrukcje |
| **⚡ Skille** | Procedury działania agenta: kroki, faza, exit criteria, anti-rationalizations |
| **🔗 Hooki** | Automatyczne akcje wyzwalane zdarzeniami (pre_run, post_run, on_error…) |
| **📋 Instrukcje** | Ogólne zasady i reguły dla agentów |
| **🗺 Diagram** | Wizualizacja połączeń agent → skill → hook |
| **✅ Walidacja** | Przegląd problemów jakości (braki pól, martwe referencje) z nawigacją klik→panel |
| **▶ Uruchom** | Uruchomienie agenta w tle (via litellm) z podglądem wyniku, skill calls, aktywnym modelem, **historią sesji** i **syntezą mowy TTS** |
| **📤 Eksport** | Generowanie pliku `AGENTS.md` lub reguł `.cursor/rules/*.mdc` |
| **⚙ Ustawienia** | Język interfejsu, domyślny model, workspace, **zarządzanie kluczami API** (OpenAI / Anthropic / Gemini) |

### Dodatkowe cechy

- **Dwujęzyczny interfejs** — przełączanie PL/EN w locie (⚙ Ustawienia → Język)
- **Klucze API w GUI** — brak potrzeby ręcznej edycji `.env`; klucze są zapisywane w `~/.agent-manager/api_keys.env` i ładowane przy każdym uruchomieniu
- **Przycisk Zapisz zawsze widoczny** — poza obszarem przewijania, z potwierdzeniem ✔ Zapisano (zielony flash)
- **Sanitizacja nazw narzędzi** — nazwy skilli ze spacjami lub znakami specjalnymi są automatycznie konwertowane do formatu wymaganego przez OpenAI API (`^[a-zA-Z0-9_-]+$`)
- **Historia sesji** — każda rozmowa z agentem jest automatycznie zapisywana w `data/sessions/`; pasek boczny pozwala przeglądać i wznawiać poprzednie sesje
- **TTS (Text-to-Speech)** — każda odpowiedź agenta ma przycisk `▶` do odczytu głosowego przez OpenAI TTS (`tts-1`, głos `alloy`); przycisk sygnalizuje stany: `▶` gotowy, `⏳` ładowanie, `■` odtwarzanie

---

## Wymagania

- Python 3.12+
- PyQt6 >= 6.7.0
- pygame >= 2.5.0 (odtwarzanie TTS)
- Klucz API modelu LLM (OpenAI, Anthropic lub inny obsługiwany przez litellm)
- Klucz `OPENAI_API_KEY` wymagany do funkcji TTS

---

## Instalacja

```bash
git clone https://github.com/Korey90/agent-manager.git
cd agent-manager

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

### Klucze API

Klucze API można ustawić na dwa sposoby:

**Opcja A — przez GUI (zalecana):** Uruchom aplikację, przejdź do ⚙ **Ustawienia → Klucze API**, wpisz klucze i kliknij *Zapisz ustawienia*. Klucze są przechowywane w `~/.agent-manager/api_keys.env` i ładowane automatycznie przy każdym starcie.

**Opcja B — plik `.env`:** Skopiuj i wypełnij plik środowiskowy:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-...          # lub ANTHROPIC_API_KEY, GEMINI_API_KEY
DEFAULT_MODEL=gpt-4o
WORKSPACE_DIR=.                # katalog projektu zawierający .github/
DATA_DIR=data
```

---

## Uruchomienie

```bash
python gui_main.py
```

Dane agentów, skilli i hooków są odczytywane z (i zapisywane do) katalogu `.github/` wskazanego przez `WORKSPACE_DIR`.

---

## Struktura projektu

```
agent-manager/
├── core/               # Modele Pydantic (Agent, Skill, Hook, Instruction, Prompt, Session)
│   └── session.py      # Model sesji (Session, SessionTurn) — historia rozmów
├── data/
│   └── sessions/       # Zapisane sesje rozmów (JSON, auto-tworzone)
├── gui/                # Interfejs PyQt6
│   ├── main_window.py  # Główne okno z zakładkami
│   ├── panels.py       # Panele CRUD (BasePanel + AgentPanel, SkillPanel, …)
│   ├── run_panel.py    # Zakładka uruchamiania agenta (sesje, TTS)
│   ├── export_panel.py # Zakładka eksportu (AGENTS.md / Cursor .mdc)
│   ├── diagram.py      # Wizualizacja grafu
│   └── state.py        # Globalny stan (workspace, registry)
├── runtime/            # Silnik wykonania (litellm, hooks, skill invoker)
├── storage/            # Odczyt/zapis plików Markdown
├── registry/           # Indeks załadowanych obiektów
├── tests/              # Testy pytest
├── gui_main.py         # Punkt wejścia GUI
├── main.py             # Punkt wejścia CLI
└── .env.example        # Przykładowa konfiguracja
```

---

## Model danych

### Agent
Posiada rolę, opis, model LLM, listę przypisanych **skill_ids**, **hook_ids** i **instruction_ids**. Może zawierać `hard_rules` i `preferred_patterns`.

### Skill
Opisuje procedurę działania agenta:
- `phase` — etap (general / define / plan / build / verify / review / ship)
- `steps` — lista kroków do wykonania
- `exit_criteria` — warunek ukończenia
- `anti_rationalizations` — lista typowych wymówek, których należy unikać

### Hook
Automatyczne akcje powiązane ze zdarzeniami cyklu życia (`pre_run`, `post_run`, `on_error`, `on_skill_call`, `on_response`). Zawiera listę `checks` i `actions`.

---

## Walidacja

Panel **✅ Walidacja** wykrywa m.in.:
- skill bez kroków (błąd)
- brak `exit_criteria` lub `when_to_use` (ostrzeżenie)
- agenta bez przypisanych skilli
- referencje do nieistniejących skilli/hooków

Każdy problem ma przycisk **⇗** — klik przenosi bezpośrednio do odpowiedniego panelu i podświetla element pomarańczową ramką.

---

## Eksport

- **AGENTS.md** — czytelny plik z rolami, modelami i regułami wszystkich agentów
- **Cursor .mdc** — reguły w formacie `.cursor/rules/<agent_id>.mdc` z YAML frontmatter i pełną listą skilli

---

## Testy

```bash
python -m pytest tests/ -q
```

---

## Licencja

MIT
