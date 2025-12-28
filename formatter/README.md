# xil Code Formatter

Regelwerkbasierter Code-Formatter für xil-Dateien, implementiert mit Lark.

## Features

- **Externe Regel-Dateien**: Grammatik (`grammar.lark`) und Formatierungsregeln (`formatting_rules.yaml`) sind getrennt
- **Konfigurierbar**: Alle Formatierungsoptionen über YAML-Datei
- **Erweiterbar**: Einfach neue Regeln hinzufügen

## Installation

```bash
pip install lark pyyaml
```

Oder über das Projekt:
```bash
uv sync  # wenn uv verwendet wird
```

## Verwendung

### Als Python-Modul

```python
from formatter import XilFormatter

formatter = XilFormatter()
formatted_code = formatter.format(code_string)
```

### Als CLI-Tool

```bash
python formatter/formatter.py input.xil output.xil
```

Oder in-place:
```bash
python formatter/formatter.py input.xil
```

## Konfiguration

Die Formatierungsregeln können in `formatting_rules.yaml` angepasst werden:

- **spacing**: Leerzeichen um Operatoren
- **line_breaks**: Leerzeilen zwischen Sektionen
- **formatting**: Zeilenlänge, Anführungszeichen, etc.
- **sections**: Format für Sektions-Header
- **statements**: Format für verschiedene Statement-Typen

## Struktur

```
formatter/
├── grammar.lark          # Lark-Grammatik für xil
├── formatting_rules.yaml # Formatierungsregeln
├── formatter.py          # Hauptformatter
└── __init__.py          # Package-Init
```

## Beispiel

**Input:**
```xil
[module app]
[lib "KERNEL32.DLL"]
writeConsoleA="WriteConsoleA"
[ffi]
writeConsoleA=(ConsoleOutput:ptr, Buffer:ptr, NumberOfCharsToWrite:u32, NumberOfCharsWritten:ptr, Reserved:ptr)i32
```

**Output (formatiert):**
```xil
[module app]

[lib "KERNEL32.DLL"]
writeConsoleA = "WriteConsoleA"

[ffi]
writeConsoleA = (ConsoleOutput:ptr, Buffer:ptr, NumberOfCharsToWrite:u32, NumberOfCharsWritten:ptr, Reserved:ptr)i32
```
