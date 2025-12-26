import ctypes

def _map_type_to_ctypes(xil_type):
    """Map XIL type to ctypes type"""
    type_map = {
        'i8': ctypes.c_int8,
        'i16': ctypes.c_int16,
        'i32': ctypes.c_int32,
        'i64': ctypes.c_int64,
        'u8': ctypes.c_uint8,
        'u16': ctypes.c_uint16,
        'u32': ctypes.c_uint32,
        'u64': ctypes.c_uint64,
        'f32': ctypes.c_float,
        'f64': ctypes.c_double,
        'void': None,
        'bool': ctypes.c_bool,
        'ptr': ctypes.c_void_p,
    }
    return type_map.get(xil_type, ctypes.c_void_p)

def _generate_ffi_functions(module):
    """Generate Python FFI functions for all FFI declarations"""
    ffi_functions = {}
    loaded_libs = {}
    
    # Load libraries
    for lib_name, symbols in module.get('libs', {}).items():
        try:
            if lib_name.endswith('.dll'):
                lib = ctypes.WinDLL(lib_name)
            else:
                lib = ctypes.CDLL(lib_name)
            loaded_libs[lib_name] = lib
        except OSError as e:
            print(f"Warning: Could not load library {lib_name}: {e}")
            continue
    
    # Generate FFI functions
    for func_name, func_decl in module.get('ffi', {}).items():
        # Find which library contains this function
        lib = None
        symbol_name = func_name
        
        for lib_name, symbols in module.get('libs', {}).items():
            if func_name in symbols:
                lib = loaded_libs.get(lib_name)
                symbol_name = symbols[func_name]
                break
        
        if lib is None:
            print(f"Warning: No library found for FFI function {func_name}")
            continue
        
        # Get function from library
        try:
            c_func = getattr(lib, symbol_name)
        except AttributeError:
            print(f"Warning: Symbol {symbol_name} not found in library")
            continue
        
        # Set argument types
        arg_types = []
        for arg in func_decl.get('decl', []):
            arg_type = _map_type_to_ctypes(arg['type'])
            if arg_type is not None:
                arg_types.append(arg_type)
        
        c_func.argtypes = arg_types
        
        # Set return type
        return_type = _map_type_to_ctypes(func_decl.get('returns', 'void'))
        c_func.restype = return_type if return_type is not None else None
        
        # Create Python wrapper function
        def make_wrapper(c_func, arg_names, arg_types_list):
            def wrapper(*args):
                # Convert arguments to appropriate types
                converted_args = []
                for i, arg_value in enumerate(args):
                    if i < len(arg_types_list) and arg_types_list[i] is not None:
                        expected_type = arg_types_list[i]
                        # If expecting a pointer type
                        if expected_type == ctypes.c_void_p:
                            # If already a pointer type, use as is
                            if isinstance(arg_value, (ctypes._Pointer, ctypes._SimpleCData)):
                                converted_args.append(arg_value)
                            # If it's an integer (address), convert to pointer
                            elif isinstance(arg_value, int):
                                converted_args.append(ctypes.c_void_p(arg_value))
                            else:
                                converted_args.append(arg_value)
                        else:
                            converted_args.append(arg_value)
                    else:
                        converted_args.append(arg_value)
                return c_func(*converted_args)
            wrapper.__name__ = func_name
            return wrapper
        
        arg_names = [arg['name'] for arg in func_decl.get('args', [])]
        ffi_functions[func_name] = make_wrapper(c_func, arg_names, arg_types)
    
    return ffi_functions

def _parse_value(value, locals_dict, constants):
    """Parse a value string to Python value, checking local variables and constants"""
    value = value.strip()
    # Check for property access (e.g., hello.ptr, hello.bytes)
    if '.' in value:
        parts = value.split('.', 1)
        var_name = parts[0]
        property_name = parts[1]
        
        # Check if it's a local variable referencing a constant
        if var_name in locals_dict:
            const_ref = locals_dict[var_name]
            if isinstance(const_ref, dict) and 'value' in const_ref:
                const_value = const_ref['value']
                # Handle string constants
                if isinstance(const_value, str):
                    if property_name == 'ptr':
                        # Return pointer to string (as ctypes pointer)
                        import ctypes
                        return ctypes.c_char_p(const_value.encode('utf-8'))
                    elif property_name == 'bytes':
                        # Return byte length
                        return len(const_value.encode('utf-8'))
        return value
    
    # Check if it's a local variable
    if value in locals_dict:
        ref = locals_dict[value]
        # If it's a constant reference, return the actual value
        if isinstance(ref, dict) and 'value' in ref:
            return ref['value']
        return ref
    
    # Try to parse as integer
    try:
        return int(value)
    except ValueError:
        pass
    # Try to parse as float
    try:
        return float(value)
    except ValueError:
        pass
    # Check if string literal
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    # Return as string identifier (might be used later)
    return value

 # Funktion zur Verarbeitung von String-Literalen mit Ersetzung von '\n' durch Linebreaks
def _process_string_literal(s):
    # Ersetzt '\n' (escaptes) durch echte Zeilenumbrüche
    return s.replace('\\n', '\n')

def _parse_const_value(value_str):
    """Parse a constant value string to Python value"""
    value = None
    # Try to parse as integer
    try:
        value = int(value_str)
    except ValueError:
        pass
    # Try to parse as float
    if value is None:
        try:
            value = float(value_str)
        except ValueError:
            pass
    # Check if string literal
    if value is None:
        if value_str.startswith('"') and value_str.endswith('"'):
            value = value_str[1:-1]
        else:
            value = value_str
        value = _process_string_literal(value)
    return value

def _execute_call(call_args, module, stack, locals_dict, constants):
    """Execute a call statement"""
    if not call_args:
        return
    
    func_name = call_args[0].strip()
    # Parse arguments (supporting local variables and constants)
    args = [_parse_value(arg, locals_dict, constants) for arg in call_args[1:]]
    # Check if it's an FFI function
    if 'ffi_functions' in module and func_name in module['ffi_functions']:
        result = module['ffi_functions'][func_name](*args)
        if result is not None:
            stack.append(result)
    # Check if it's a module function
    elif 'fun' in module and func_name in module['fun']:
        stack.extend(args)
        _execute_function(func_name, module, stack, {}, constants)
    else:
        print(f"Warning: Function '{func_name}' not found")

def _execute_move(var_name, stack, locals_dict):
    """Execute a move statement"""
    var_name = var_name.strip()
    if not stack:
        print(f"Error: Stack is empty, cannot move to variable '{var_name}'")
        return
    value = stack.pop()
    locals_dict[var_name] = value

def _execute_const(const_args, locals_dict, constants):
    """Execute a const statement"""
    if len(const_args) < 2:
        print(f"Error: const statement requires variable name and value")
        return
    
    var_name = const_args[0].strip()
    value_str = const_args[1].strip()
    
    # Parse the value
    value = _parse_const_value(value_str)
    
    # Store in constants set (using value as key for uniqueness if hashable)
    # For hashable types (str, int, float, etc.), use value as key
    # This ensures uniqueness: same value = same key
    if isinstance(value, (str, int, float, bool, type(None))):
        constants[value] = value
    else:
        # For non-hashable types, use id as fallback
        constants[id(value)] = value
    
    # Reference in local dictionary
    locals_dict[var_name] = {'value': value}

def _execute_decl(param_defs, stack, locals_dict):
    """Execute a decl statement (similar to args but for local variable declarations)"""
    if not param_defs:
        return
    
    # Pop values from stack in reverse order (last argument pushed is first popped)
    # But we want to assign them in the order they were defined
    num_params = len(param_defs)
    if len(stack) < num_params:
        print(f"Error: Stack has only {len(stack)} values, but {num_params} parameters expected")
        return
    
    # Pop values from stack (in reverse order of definition)
    values = []
    for _ in range(num_params):
        values.append(stack.pop())
    
    # Assign to local variables in definition order (reverse the popped values)
    for i, param_def in enumerate(param_defs):
        param_name = param_def['name'].strip()
        # Ignore type as requested
        locals_dict[param_name] = values[num_params - 1 - i]

def _execute_cmp(cmp_args, locals_dict, constants):
    """Execute a cmp statement"""
    if len(cmp_args) < 2:
        print(f"Error: cmp statement requires two operands")
        return
    
    # Parse both operands (supporting local variables and constants)
    val1 = _parse_value(cmp_args[0], locals_dict, constants)
    val2 = _parse_value(cmp_args[1], locals_dict, constants)
    
    result = 0
    
    # Check if both are numbers (int or float)
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        if val1 == val2:
            result = 0
        elif val1 > val2:
            result = 1
        else:  # val1 < val2
            result = -1
    else:
        # Different types: compare as equal if both are None/empty, otherwise -1
        if val1 == val2:
            result = 0
        else:
            result = -1
    
    # Store result in .cmp local variable
    locals_dict['.cmp'] = result

def _execute_if(if_args, locals_dict, constants):
    """Execute an if statement"""
    if len(if_args) < 2:
        print(f"Error: if statement requires condition value and label name")
        return
    
    # Parse the condition value
    condition_value = _parse_value(if_args[0].strip(), locals_dict, constants)
    
    # Get .cmp value
    cmp_value = locals_dict.get('.cmp', 0)
    
    # Compare: if condition is not equal to .cmp, we need to jump
    # Return a special value to indicate jump is needed
    if condition_value != cmp_value:
        # Return the label name so _execute_function can handle the jump
        return {'jump_to_label': if_args[1].strip()}
    
    # If condition is true (equal), continue normally (return None)
    return None

def _execute_statement(stmt, module, stack, locals_dict, constants):
    """Execute a single statement"""
    if 'call' in stmt:
        _execute_call(stmt['call'], module, stack, locals_dict, constants)
    elif 'move' in stmt:
        _execute_move(stmt['move'], stack, locals_dict)
    elif 'const' in stmt:
        _execute_const(stmt['const'], locals_dict, constants)
    elif 'decl' in stmt:
        _execute_decl(stmt['decl'], stack, locals_dict)
    elif 'cmp' in stmt:
        _execute_cmp(stmt['cmp'], locals_dict, constants)
    elif 'label' in stmt:
        # label=label_name - label registration is handled in _execute_function
        # where we have access to statement indices
        pass
    elif 'if' in stmt:
        return _execute_if(stmt['if'], locals_dict, constants)

def _execute_function(func_name, module, stack, parent_locals, constants):
    """Execute a function by name"""
    if 'fun' not in module or func_name not in module['fun']:
        print(f"Error: Function '{func_name}' not found")
        return
    
    # Create local variables dictionary for this function
    locals_dict = {}
    
    statements = module['fun'][func_name]
    
    # First, register all labels with their statement index as value
    label_indices = {}
    for i, stmt in enumerate(statements):
        if 'label' in stmt:
            label_name = stmt['label'].strip()
            # Store the index of this statement (label points to itself)
            label_indices[label_name] = i
    
    # first execute args and decl to populate local variables
    for stmt in statements:
        if 'decl' in stmt:
            _execute_statement(stmt, module, stack, locals_dict, constants)
    
    # Then execute other statements with index-based execution for jumps
    i = 0
    while i < len(statements):
        stmt = statements[i]
        
        # Skip args, decl and label statements (already executed)
        if 'decl' in stmt or 'label' in stmt:
            i += 1
            continue
        
        # Execute the statement
        result = _execute_statement(stmt, module, stack, locals_dict, constants)
        
        # Check if a jump was requested
        if isinstance(result, dict) and 'jump_to_label' in result:
            label_name = result['jump_to_label']
            if label_name in label_indices:
                # Jump to the label's statement index
                i = label_indices[label_name]
                # Continue from the label (which will be skipped in next iteration)
                continue
            else:
                print(f"Error: Label '{label_name}' not found")
                break
        
        i += 1

def run(module): 
    print(module)
    # Generate FFI functions for this module
    ffi_functions = _generate_ffi_functions(module)
    module['ffi_functions'] = ffi_functions
    
    # Create constants set (unique storage for constants)
    constants = {}
    
    # Find main function and execute it
    if 'fun' in module and 'main' in module['fun']:
        stack = [0,0]
        _execute_function('main', module, stack, {}, constants)
    else:
        print(f"Warning: No 'main' function found in module {module.get('module', 'unknown')}")

if __name__ == "__main__":
    print("vm")