# Agent Manager

Desktopowy menedżer agentów AI z graficznym interfejsem (PyQt6). Pozwala definiować, organizować i uruchamiać agentów opartych na modelu LLM — wraz z ich skilłami, hookami, instrukcjami i promptami. Dane są przechowywane jako pliki Markdown w katalogu `.github/` projektu.

---

## Funkcje

| Zakładka | Opis |
|---|---|
| **🤖 Agenci** | Tworzenie i edycja agentów: rola, model LLM, przypisane skille/hooki/instrukcje |
| **⚡ Skille** | Procedury działania agenta: kroki, faza, exit criteria, anti-rationalizations |
| **🔗 Hooki** | Automatyczne akcje wyzwalane zdarzeniami (pre_run, post_run, on_error…) |
| **📋 Instrukcje** | Ogólne zasady i reguły dla agentów |
| **🗺 Diagram** | Wizualizacja połączeń agent → skill → hook |
| **✅ Walidacja** | Przegląd problemów jakości (braki pól, martwe referencje) z nawigacją klik→panel |
| **▶ Uruchom** | Uruchomienie agenta w tle (via litellm) z podglądem wyniku i skill calls |
| **📤 Eksport** | Generowanie pliku `AGENTS.md` lub reguł `.cursor/rules/*.mdc` |

---

## Wymagania

- Python 3.12+
- PyQt6 >= 6.7.0
- Klucz API modelu LLM (OpenAI, Anthropic lub inny obsługiwany przez litellm)

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

Skopiuj plik konfiguracji środowiska:

```bash
cp .env.example .env
```

Wypełnij `.env`:

```env
OPENAI_API_KEY=sk-...          # lub ANTHROPIC_API_KEY, itp.
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
├── core/               # Modele Pydantic (Agent, Skill, Hook, Instruction, Prompt)
├── gui/                # Interfejs PyQt6
│   ├── main_window.py  # Główne okno z zakładkami
│   ├── panels.py       # Panele CRUD (BasePanel + AgentPanel, SkillPanel, …)
│   ├── run_panel.py    # Zakładka uruchamiania agenta
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
