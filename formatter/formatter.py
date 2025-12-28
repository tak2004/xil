from lark import Lark, Transformer, Token
from pathlib import Path
import yaml
from typing import List, Dict, Any, Union
from glob import glob

class FormattingTransformer(Transformer):
    """Transformiert den Parse-Tree nach Formatierungsregeln"""
    
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        self.output_lines: List[str] = []
        self.last_section = None
    
    def unit(self, children):
        """Haupt-Einheit"""
        result = []
        for child in children:
            if isinstance(child, str):
                result.append(child)
            elif isinstance(child, list):
                result.extend(child)
            else:
                # Konvertiere Tree-Objekte zu Strings, aber nicht Listen-Repräsentationen
                item_str = str(child)
                if not item_str.startswith('Tree(') and not item_str.startswith('Token('):
                    # Filtere Python-Listen-Repräsentationen aus
                    if item_str.startswith("['") and "']" in item_str:
                        end_idx = item_str.find("']")
                        if end_idx != -1:
                            inner = item_str[2:end_idx]
                            # Entferne auch eventuelles "=" am Ende
                            if inner.endswith("="):
                                inner = inner[:-1]
                            # Dekodiere Escape-Sequenzen (z.B. \\n -> \n)
                            try:
                                inner = inner.encode().decode('unicode_escape')
                            except:
                                pass  # Falls Dekodierung fehlschlägt, verwende Original
                            result.append(inner)
                    else:
                        result.append(item_str)
        
        # Flatten und bereinigen
        flattened = []
        for item in result:
            if isinstance(item, list):
                flattened.extend(item)
            elif item is not None:
                # Nur Strings hinzufügen, keine Tree-Repräsentationen
                if isinstance(item, str):
                    flattened.append(item)
                else:
                    item_str = str(item)
                    if not item_str.startswith('Tree(') and not item_str.startswith('Token('):
                        flattened.append(item_str)
        
        return flattened
    
    def module(self, children):
        """[module name]"""
        name = str(children[0]) if children else ""
        format_str = self.rules.get('sections', {}).get('module', {}).get('format', "[module {name}]")
        line = format_str.format(name=name)
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            return [line, ""]
        return [line]
    
    def use(self, children):
        """[use name]"""
        name = str(children[0]) if children else ""
        format_str = self.rules.get('sections', {}).get('use', {}).get('format', "[use {name}]")
        line = format_str.format(name=name)
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            return [line, ""]
        return [line]
    
    def library(self, children):
        """[lib "name"] import_lines"""
        lib_name = str(children[0])
        imports = []
        for item in children[1:]:
            if isinstance(item, list):
                imports.extend(item)
            elif item:
                imports.append(item)
        
        format_str = self.rules.get('sections', {}).get('lib', {}).get('format', "[lib {name}]")
        result = [format_str.format(name=lib_name)]
        
        # Import-Zeilen
        for imp in imports:
            if isinstance(imp, list):
                result.extend(imp)
            else:
                result.append(imp)
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            result.append("")
        
        return result
    
    def import_line(self, children):
        """ID = (ID | STRLIT)"""
        key = str(children[0])
        value = str(children[1]) if len(children) > 1 else ""
        
        # import_line hat keine Leerzeichen um das Gleichheitszeichen
        return [f"{key}={value}"]
    
    def ffi(self, children):
        """[ffi] cdecl_lines"""
        format_str = self.rules.get('sections', {}).get('ffi', {}).get('format', "[ffi]")
        result = [format_str]
        
        # FFI-Deklarationen
        for cdecl in children:
            if isinstance(cdecl, list):
                result.extend(cdecl)
            elif cdecl:
                result.append(str(cdecl))
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            result.append("")
        
        return result
    
    def type(self, children):
        """[type name] type_statements"""
        type_name = str(children[0])
        statements = []
        for item in children[1:]:
            if isinstance(item, list):
                statements.extend(item)
            elif item:
                # Auch einzelne Strings/Objekte hinzufügen (z.B. von type_statement)
                statements.append(item)
        
        format_str = self.rules.get('sections', {}).get('type', {}).get('format', "[type {name}]")
        result = [format_str.format(name=type_name)]
        
        # Type-Statements
        for stmt in statements:
            if isinstance(stmt, list):
                # Wenn es eine Liste ist, füge alle Elemente hinzu
                for item in stmt:
                    if isinstance(item, str):
                        result.append(item)
                    elif item:
                        result.append(str(item))
            elif stmt:
                # Wenn es ein String ist, füge ihn direkt hinzu
                result.append(str(stmt))
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            result.append("")
        
        return result
    
    def TYPE_KEY(self, token):
        """bytes oder align"""
        return str(token)
    
    def type_statement(self, children):
        """bytes|align = SIGNED_NUMBER"""
        # children: [TYPE_KEY_result, "=", SIGNED_NUMBER] oder [TYPE_KEY_result, SIGNED_NUMBER]
        # TYPE_KEY_result ist bereits ein String ("bytes" oder "align")
        # "=" könnte fehlen, wenn es als Literal behandelt wird
        
        if len(children) < 2:
            return [""]
        
        # Nimm das erste Element als key (bereits transformiert von TYPE_KEY)
        key = str(children[0])
        
        # Prüfe ob key "bytes" oder "align" ist
        if key not in ("bytes", "align"):
            return [""]
        
        # Finde den value (SIGNED_NUMBER), überspringe "=" falls vorhanden
        value = None
        for i in range(1, len(children)):
            val_str = str(children[i])
            if val_str != "=":
                # Prüfe ob es eine Zahl ist
                try:
                    int(val_str)  # Test ob es eine Zahl ist (positiv oder negativ)
                    value = val_str
                    break
                except ValueError:
                    pass
        
        if value is None:
            # Fallback: nimm das letzte Element, das nicht "=" ist
            for i in range(len(children) - 1, 0, -1):
                val_str = str(children[i])
                if val_str != "=":
                    value = val_str
                    break
        
        if value is None:
            return [""]
        
        # type_statement hat keine Leerzeichen um das Gleichheitszeichen
        result = f"{key}={value}"
        return [result]
    
    def cdecl(self, children):
        """ID = (arg_list) return_type"""
        # children: [func_name, arg_list, return_type]
        # arg_list ist bereits eine Liste von arg-Objekten
        func_name = str(children[0])
        
        # Finde return_type (letztes Element, das kein List ist)
        return_type = ""
        args = []
        for i in range(1, len(children)):
            if isinstance(children[i], list):
                args = children[i]
            else:
                return_type = str(children[i])
        
        # Formatiere Argumente
        spacing = self.rules.get('spacing', {})
        comma_after_space = " " if spacing.get('after_comma', True) else ""
        comma_before_space = " " if spacing.get('before_comma', False) else ""
        comma_separator = f"{comma_before_space},{comma_after_space}"
        
        if args:
            args_str = comma_separator.join(str(arg) for arg in args)
        else:
            args_str = ""
        
        # cdecl hat keine Leerzeichen um das Gleichheitszeichen
        return [f"{func_name}=({args_str}){return_type}"]
    
    def arg(self, children):
        """ID : ID"""
        name = str(children[0])
        type_name = str(children[1])
        return f"{name}:{type_name}"
    
    def arg_list(self, children):
        """Liste von Argumenten"""
        return list(children) if children else []
    
    def function(self, children):
        """[fun name] statements"""
        func_name = str(children[0])
        statements = []
        for item in children[1:]:
            if isinstance(item, list):
                statements.extend(item)
        
        format_str = self.rules.get('sections', {}).get('fun', {}).get('format', "[fun {name}]")
        result = [format_str.format(name=func_name)]
        
        # Statements
        for stmt in statements:
            if isinstance(stmt, list):
                # Wenn es eine Liste ist, füge alle Elemente hinzu
                for item in stmt:
                    if isinstance(item, str):
                        result.append(item)
                    elif item:
                        result.append(str(item))
            elif stmt:
                # Wenn es ein String ist, füge ihn direkt hinzu
                result.append(str(stmt))
        
        if self.rules.get('line_breaks', {}).get('after_section_header', True):
            result.append("")
        
        return result
    
    def decl_statement(self, children):
        """decl = (arg_list) return_type"""
        # children: [arg_list, return_type]
        # arg_list ist bereits eine Liste von arg-Objekten
        args = []
        return_type = ""
        
        for child in children:
            if isinstance(child, list):
                args = child
            else:
                return_type = str(child)
        
        spacing = self.rules.get('spacing', {})
        comma_after_space = " " if spacing.get('after_comma', True) else ""
        comma_before_space = " " if spacing.get('before_comma', False) else ""
        comma_separator = f"{comma_before_space},{comma_after_space}"
        
        if args:
            args_str = comma_separator.join(str(arg) for arg in args)
        else:
            args_str = ""
        
        # decl_statement hat keine Leerzeichen um das Gleichheitszeichen
        line = f"decl=({args_str}){return_type}"
        
        # Prüfe Zeilenlänge
        max_length = self.rules.get('formatting', {}).get('max_line_length', 88)
        if len(line) > max_length:
            # Umbrechung (vereinfacht - kann verbessert werden)
            pass
        
        return [line]
    
    def statement(self, children):
        """OP = arg_list"""
        op = str(children[0])
        args = children[1] if len(children) > 1 and isinstance(children[1], list) else []
        
        spacing = self.rules.get('spacing', {})
        comma_after_space = " " if spacing.get('after_comma', True) else ""
        comma_before_space = " " if spacing.get('before_comma', False) else ""
        comma_separator = f"{comma_before_space},{comma_after_space}"
        
        # Normale Statements
        if args:
            args_str = comma_separator.join(str(arg) for arg in args)
            # Für move und label: nur erster Wert
            value_str = str(args[0]) if args else ""
        else:
            args_str = ""
            value_str = ""
        
        format_str = self.rules.get('statements', {}).get(op, {}).get('format', "{op}={args}")
        
        # Unterstütze sowohl {args} als auch {value} im Format-String
        try:
            line = format_str.format(op=op, args=args_str, value=value_str)
        except KeyError:
            # Fallback wenn Format-String andere Platzhalter hat
            line = format_str.format(op=op, args=args_str, value=value_str, declaration=args_str)
        
        # Prüfe Zeilenlänge
        max_length = self.rules.get('formatting', {}).get('max_line_length', 88)
        if len(line) > max_length:
            # Umbrechung (vereinfacht - kann verbessert werden)
            pass
        
        return [line]
    
    def arg_list_statement(self, children):
        """Liste von Argumenten für Statements"""
        # Konvertiere alle Children zu Strings
        return [str(child) for child in children] if children else []
    
    def arg_value(self, children):
        """Einzelnes Argument-Wert"""
        return str(children[0]) if children else ""
    
    def blank_line(self, children):
        """Leerzeile"""
        return [""]
    
    def comment(self, children):
        """Kommentar-Zeile"""
        comment_text = str(children[0]) if children else ""
        return [comment_text]
    
    # Terminal-Tokens
    def ID(self, token):
        return str(token)
    
    def ID_PROPERTY(self, token):
        return str(token)
    
    def NUMBER(self, token):
        return str(token)
    
    def SIGNED_NUMBER(self, token):
        return str(token)
    
    def STRLIT(self, token):
        # Normalisiere Anführungszeichen wenn gewünscht
        quote_style = self.rules.get('formatting', {}).get('quote_style', 'double')
        # Verwende token.value um Escape-Sequenzen korrekt zu behandeln
        if hasattr(token, 'value'):
            value = token.value
        else:
            value = str(token)
        
        if self.rules.get('formatting', {}).get('normalize_quotes', True):
            if quote_style == 'double' and value.startswith("'"):
                value = value.replace("'", '"')
            elif quote_style == 'single' and value.startswith('"'):
                value = value.replace('"', "'")
        
        return value
    
    def OP(self, token):
        return str(token)
    
    def COMMENT(self, token):
        return str(token)


class XilFormatter:
    """Hauptklasse für xil-Code-Formatierung"""
    
    def __init__(self, grammar_path: str = None, rules_path: str = None):
        # Standard-Pfade relativ zum formatter-Verzeichnis
        if grammar_path is None:
            grammar_path = Path(__file__).parent / "grammar.lark"
        if rules_path is None:
            rules_path = Path(__file__).parent / "formatting_rules.yaml"
        
        grammar_path = Path(grammar_path)
        rules_path = Path(rules_path)
        
        # Lade Grammatik
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar = f.read()
        self.parser = Lark(grammar, start='unit', parser='lalr', maybe_placeholders=False)
        
        # Lade Formatierungsregeln
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)
    
    def format(self, code: str) -> str:
        """Formatiert xil-Code nach den Regeln"""
        try:
            # Parse Code
            tree = self.parser.parse(code)
            
            # Transformiere mit Formatierungsregeln
            transformer = FormattingTransformer(self.rules)
            result = transformer.transform(tree)
            
            # Bereinige Ergebnis - entferne Tree- und Token-Objekte
            def clean_result(item):
                """Rekursiv bereinigt Ergebnis von Tree/Token-Objekten"""
                if isinstance(item, str):
                    return item
                elif isinstance(item, list):
                    cleaned = []
                    for subitem in item:
                        cleaned_sub = clean_result(subitem)
                        if cleaned_sub is not None:
                            if isinstance(cleaned_sub, list):
                                cleaned.extend(cleaned_sub)
                            else:
                                cleaned.append(cleaned_sub)
                    return cleaned
                else:
                    # Filtere Tree/Token-Objekte
                    item_str = str(item)
                    if item_str.startswith('Tree(') or item_str.startswith('Token('):
                        return None
                    return item_str
            
            cleaned_result = clean_result(result)
            
            # Konvertiere zu Liste von Zeilen - rekursiv Listen auflösen
            def flatten_lines(items):
                """Rekursiv Listen zu Strings auflösen"""
                result = []
                for item in items:
                    if isinstance(item, list):
                        # Rekursiv auflösen
                        flattened = flatten_lines(item)
                        result.extend(flattened)
                    elif item is not None:
                        # Nur Strings hinzufügen, keine Listen-Repräsentationen
                        item_str = str(item)
                        # Filtere Python-Listen-Repräsentationen aus (z.B. "['text']" oder "['text']=")
                        if item_str.startswith("['") and "']" in item_str:
                            # Extrahiere den Inhalt aus der Listen-Repräsentation
                            # Finde das Ende der Liste (']' oder ']=') 
                            end_idx = item_str.find("']")
                            if end_idx != -1:
                                inner = item_str[2:end_idx]  # Entferne "['" und "']"
                                # Entferne auch eventuelles "=" am Ende
                                if inner.endswith("="):
                                    inner = inner[:-1]
                                # Dekodiere Escape-Sequenzen (z.B. \\n -> \n)
                                try:
                                    inner = inner.encode().decode('unicode_escape')
                                except:
                                    pass  # Falls Dekodierung fehlschlägt, verwende Original
                                result.append(inner)
                            else:
                                result.append(item_str)
                        elif not (item_str.startswith('[') and item_str.endswith(']') and "'" in item_str):
                            result.append(item_str)
                return result
            
            if isinstance(cleaned_result, str):
                lines = cleaned_result.split('\n')
            elif isinstance(cleaned_result, list):
                lines = flatten_lines(cleaned_result)
            else:
                lines = [str(cleaned_result)] if cleaned_result else []
            
            # Entferne mehrfache Leerzeilen (max 2 aufeinanderfolgende Leerzeilen)
            cleaned_lines = []
            blank_count = 0
            for line in lines:
                is_blank = not line.strip()
                if is_blank:
                    blank_count += 1
                    # Erlaube max 2 aufeinanderfolgende Leerzeilen
                    if blank_count <= 2:
                        cleaned_lines.append(line)
                else:
                    blank_count = 0
                    cleaned_lines.append(line)
            
            # Entferne trailing Leerzeilen (aber behalte eine, wenn es eine Sektion war)
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            
            return '\n'.join(cleaned_lines)
        
        except Exception as e:
            raise ValueError(f"Formatting error: {e}")


# CLI-Interface
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Format xil files or check formatting')
    parser.add_argument('files', nargs='*', help='Specific xil files to check/format (optional)')
    parser.add_argument('--recursive', '-r', action='store_true', 
                       help='Recursively check all xil files in subdirectories')
    parser.add_argument('--format', '-f', action='store_true',
                       help='Format files in-place (default: check only)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed error information (first problem found)')
    
    args = parser.parse_args()
    
    formatter = XilFormatter()
    
    # Wenn keine Dateien angegeben, finde alle .xil Dateien
    if not args.files:
        if args.recursive:
            # Rekursiv: finde alle .xil Dateien, auch in versteckten Ordnern
            # Verwende Path.rglob() für bessere Behandlung versteckter Ordner
            current_dir = Path('.')
            xil_files = [str(p) for p in current_dir.rglob('*.xil')]
        else:
            pattern = "*.xil"
            xil_files = glob(pattern, recursive=False)
    else:
        xil_files = args.files
    
    if not xil_files:
        print("No xil files found.")
        sys.exit(0)
    
    # Standardmäßig Check-Modus, nur wenn --format übergeben wird, wird formatiert
    check_mode = not args.format
    
    errors_found = False
    
    for xil_file in xil_files:
        try:
            file_path = Path(xil_file)
            if not file_path.exists():
                print(f"Warning: File not found: {xil_file}")
                continue

            if file_path.is_dir():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            try:
                formatted_code = formatter.format(original_code)
            except Exception as parse_error:
                # Parsing-Fehler als Syntax-Fehler behandeln
                print(f"❌ {xil_file} has a syntax error", end="")
                if args.verbose:
                    print(f": {parse_error}")
                else:
                    print()
                errors_found = True
                continue
            
            if check_mode:
                # Check-Modus: Vergleiche Original mit formatiertem Code
                if original_code != formatted_code:
                    print(f"❌ {xil_file} is incorrectly formatted", end="")
                    if args.verbose:
                        # Finde erste unterschiedliche Zeile
                        original_lines = original_code.split('\n')
                        formatted_lines = formatted_code.split('\n')
                        
                        # Finde erste unterschiedliche Zeile
                        max_len = max(len(original_lines), len(formatted_lines))
                        for i in range(max_len):
                            orig_line = original_lines[i] if i < len(original_lines) else None
                            fmt_line = formatted_lines[i] if i < len(formatted_lines) else None
                            
                            if orig_line != fmt_line:
                                print(f"\n  First difference at line {i + 1}:")
                                if orig_line is not None:
                                    print(f"    Original: {orig_line}")
                                if fmt_line is not None:
                                    print(f"    Expected: {fmt_line}")
                                break
                    else:
                        print()
                    errors_found = True
                else:
                    print(f"✓ {xil_file} is correctly formatted")
            else:
                # Format-Modus: Schreibe formatierten Code zurück
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_code)
                print(f"Formatted: {xil_file}")
        
        except Exception as e:
            # Andere Fehler (z.B. Dateizugriff)
            print(f"Error processing {xil_file}: {e}")
            errors_found = True
    
    if check_mode and errors_found:
        sys.exit(1)
    elif check_mode:
        print(f"\nAll {len(xil_files)} file(s) are correctly formatted.")
        sys.exit(0)
