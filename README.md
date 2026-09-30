# B1 Exam Coach – Phase 2

Eine funktionsfähige Streamlit-App zur Vorbereitung auf **Cambridge B1 Preliminary**. Englischsprachige Übungen und Rückmeldungen, englisch-deutsche Vokabelkarten und ein persönlicher Lernplan. Alle Übungsaufgaben sind eigenes Material; die App ist kein offizielles Cambridge-Angebot.

## Funktionen

| Seite | Inhalt |
| --- | --- |
| Dashboard | Gespeicherte Antworten, Genauigkeit, Lernserie, fällige Wörter und Tagesplan |
| Study Plan | Tagesbudget von 5–240 Minuten, adaptive Themenprioritäten, Wiederholung und Writing |
| Reading | Parts 1–6: kurze Mitteilungen, Zuordnung, Textverständnis, Satzlücken, Multiple-Choice-Cloze und Open Cloze |
| Grammar | 48 Fragen mit Erklärungen; adaptive Auswahl oder festes Thema |
| Vocabulary | 56 Karten mit Beispielen und vier Erinnerungsstufen; Wiederholungstermine bleiben gespeichert |
| Writing | Je zwei Aufgaben für Email, Article und Story; Feedback, Entwürfe und Historie |
| My Mistakes | Falsche Antworten, Erklärungen und gezieltes erneutes Üben; richtige Wiederholungen lösen Fehler auf |
| Progress | Aktivität pro Tag, Leistungen pro Thema und Writing-Schätzwerte |
| Settings | Name, Tagesbudget, Prüfungsdatum, optionale KI und JSON-Datenexport |

Reading enthält **12 vollständige Übungssets mit 64 Fragen**. Parts 2 und 4 verwenden jeweils acht Auswahlmöglichkeiten; Parts 5 und 6 haben jeweils sechs Lücken. Open Cloze akzeptiert die hinterlegten gültigen Alternativen sowie Groß-/Kleinschreibung und äußere Leerzeichen.

Listening, Speaking und vollständige Prüfungssimulationen gehören nicht zu Phase 2.

## Lokal starten

Python **3.11 oder 3.12** verwenden. Das Repository herunterladen oder klonen und in den Projektordner wechseln:

```bash
git clone https://github.com/wikifolio-user/b1-exam-coach.git
cd b1-exam-coach
python -m venv .venv
```

Umgebung aktivieren:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Anschließend:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

**`app.py` im Repository-Root ist der Einstiegspunkt.** Die Navigation registriert die Module unter `pages/` ausdrücklich über `st.navigation`. Die SQLite-Datenbank `b1_exam_coach.db` wird beim ersten Start automatisch angelegt. SQLite ist Bestandteil von Python; ein separater Datenbankserver ist nicht nötig.

## Erster Lerndurchlauf

1. In **Settings** Name, Minutenbudget und optional Prüfungsdatum speichern.
2. In **Grammar** einige Fragen beantworten und alle Reading-Formate ausprobieren.
3. In **My Mistakes** eine falsche Antwort erneut üben.
4. In **Vocabulary** Bedeutung aufdecken und Again, Hard, Good oder Easy auswählen.
5. In **Writing** eine Antwort von ungefähr 100 Wörtern schreiben und Feedback speichern.
6. **Dashboard**, **Study Plan** und **Progress** öffnen: Sie verwenden jetzt die gespeicherten Ergebnisse.

Unvollständig beantwortete Reading-Sets werden nicht bewertet. Eine ausgewertete Runde bleibt gesperrt, bis bewusst **Try again** gewählt wird; ein Streamlit-Neuladen zählt die Antwort nicht doppelt.

## SQLite und Datenschutz

Die App verwaltet **ein lokales Lernprofil**. Sie ist für persönliche Nutzung ausgelegt und hat keine Anmeldung oder Trennung mehrerer Nutzer. Für mehrere Lernende getrennte Instanzen oder getrennte Datenbankdateien verwenden.

Die Datenbank speichert Profil, Antworten, Fehler, Vokabeltermine und Writing-Entwürfe samt Feedback. **Settings → Download learning data** exportiert diese Daten als JSON. Ein Import ist nicht implementiert. API-Keys werden weder in SQLite gespeichert noch exportiert.

Ein anderer Datenbankpfad ist über `B1_DB_PATH` möglich, beispielsweise in einer lokalen `.env`:

```env
B1_DB_PATH=/absolute/path/to/persistent/b1_exam_coach.db
```

Der übergeordnete Ordner wird automatisch erstellt. Zum Sichern die App stoppen und die SQLite-Datei kopieren. Datenbankdateien, `.env`, virtuelle Umgebungen und `.streamlit/secrets.toml` werden durch `.gitignore` ausgeschlossen.

**Hosting:** Streamlit Community Cloud garantiert keine dauerhafte lokale Dateispeicherung. SQLite dort kann bei Neustart oder Redeployment verloren gehen. Für dauerhafte Lernfortschritte einen Host mit persistentem Datenträger nutzen und `B1_DB_PATH` auf diesen Datenträger setzen. PostgreSQL und `DATABASE_URL` werden in dieser Umsetzung nicht unterstützt.

## Adaptive Lernlogik

Pro Fähigkeit und Thema werden richtige Antworten und Versuche ausgewertet. Die geglättete Beherrschung ist `(richtig + 1) / (Versuche + 2)`; die Schwäche ist `1 − Beherrschung`. Die Grammatik-Auswahl priorisiert schwache Themen, bisher ungeübte Fragen und länger nicht geübte Aufgaben. Kleine Stichproben führen nicht sofort zu vermeintlich perfekter Beherrschung.

Der Study Plan berücksichtigt Schwächen, fällige Vokabeln und bisherige Writing-Praxis. Die Minuten ergeben genau das eingestellte Tagesbudget. Bei einem sehr kleinen Budget sind einzelne Schritte als kurze Wiederholung gedacht; eine vollständige Schreibaufgabe dauert entsprechend länger. Writing-Schätzwerte werden getrennt dargestellt und nicht als objektive Richtig/Falsch-Werte in die Themenbeherrschung eingerechnet. Das Prüfungsdatum dient als Anzeige, nicht als Prognose.

## Vokabelwiederholung

Neue Wörter sind sofort fällig. **Again** setzt die Wiederholungsserie zurück; **Hard** verkürzt das Intervall. **Good** und **Easy** verlängern die Intervalle abhängig von bisheriger Erinnerung und Ease-Faktor. Termine sind UTC-basierte Kalendertage. Reviews werden atomar mit dem Lernversuch gespeichert. Die Intervalle sind auf 365 Tage begrenzt.

Die Fortschrittsanzeige interpretiert Again/Hard als noch unsichere Erinnerung und Good/Easy als erfolgreichen Abruf. Es handelt sich um Selbsteinschätzung, nicht um einen objektiven Vokabeltest.

## Writing ohne API-Key

Offline-Feedback funktioniert vollständig lokal. Die vier Trainingskriterien sind **Content**, **Communicative Achievement**, **Organisation** und **Language** (je 0–5). Hinweise berücksichtigen Wortzahl, Aufgaben-Stichwörter, Begrüßung/Abschluss, Titel, Story-Anfang, Absätze, Verknüpfungen und einige häufige Fehler.

**Die Werte sind heuristische Trainingsschätzungen, keine offiziellen Cambridge-Noten.** Stichwörter beweisen nicht, dass ein Aufgabenpunkt inhaltlich erfüllt wurde. Der Offline-Modus kann Bedeutung und grammatische Korrektheit nicht zuverlässig beurteilen. Er liefert deshalb keine erfundene verbesserte Fassung. Die Zielgröße ist ungefähr 100 Wörter, keine angeblich offizielle starre Wortzahlgrenze.

## Optionale OpenAI-Integration

1. `.env.example` nach `.env` kopieren und `OPENAI_API_KEY` lokal setzen, oder den Key in Streamlit-Secrets hinterlegen.
2. In **Settings** die KI aktivieren und ein für den eigenen OpenAI-Zugang verfügbares Modell einstellen; Standard ist `gpt-4.1-mini`.
3. In **Writing** für die konkrete Abgabe **Send this task and draft to OpenAI for AI feedback** auswählen.

Ohne diese Auswahl wird kein AI-Aufruf ausgeführt. Bei ausgewähltem AI-Feedback werden die Aufgabenstellung und der Entwurf an OpenAI gesendet; dabei können API-Kosten entstehen. Profil, Datenexport und andere Übungen werden nicht mitgesendet.

Die SDK-Anfragen haben ein Timeout von 20 Sekunden und höchstens einen Retry. Eingaben sind auf 12.000 Zeichen begrenzt; Rückgaben werden auf Struktur, Datentypen und endliche Werte von 0–5 geprüft. Bei fehlendem Key, API-Fehlern oder ungültigen Antworten erscheint automatisch das Offline-Feedback. Fehlermeldungen enthalten keine Credentials.

`.streamlit/secrets.toml.example` ist eine Vorlage mit leerem Key. **Echte API-Keys nie committen.**

## Tests und Codeprüfung

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check .
```

Die Tests prüfen Aufgabenintegrität, akzeptierte Antworten, SQLite-Persistenz, doppelte Abgaben, konkurrierende Zugriffe, Fehlerauflösung, adaptive Auswahl, genaue Minutenbudgets, Vokabeltermine, Writing-Heuristiken und gemockte AI-Erfolge/-Fehler. Streamlit-AppTests prüfen Seiten und gespeicherte Bedienabläufe mit isolierten temporären Datenbanken. Es sind keine echten API-Keys oder Netzwerkaufrufe für Tests nötig.

GitHub Actions führt Tests und Codeprüfung bei Push auf `main` und bei Pull Requests für Python 3.11 und 3.12 aus.

## Projektstruktur

```text
app.py                         # Streamlit-Einstiegspunkt
components/common.py           # Quiz, Repository-Zugriff, Secret-Lesen
pages/                         # Neun Seiten
data/                          # Originalaufgaben und öffentliche Content-API
database/repository.py         # SQLite-Schema und atomare Speicherung
services/                      # Adaptive Planung, Scoring, Progress, Writing und AI
tests/                         # Unit- und Streamlit-Integrationstests
.streamlit/config.toml          # Theme
.streamlit/secrets.toml.example # Leere Secret-Vorlage
.env.example                   # Lokale Konfiguration ohne Key
requirements.txt               # Laufzeit und pytest
requirements-dev.txt           # Zusätzliche Codeprüfung
.github/workflows/tests.yml    # CI
```
