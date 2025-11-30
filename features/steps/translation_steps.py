from behave import given, when, then
import sys
import os
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import translator


@given('a simple XIL file with module, use, lib, ffi and fun blocks')
def step_simple_xil_file(context):
    """Create a simple XIL file"""
    context.xil_content = """[module app]
[use builtin]

[lib "KERNEL32.DLL"]
exit="ExitProcess"

[ffi]
exit=(code:i32)void

[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with a module block "{module_block}"')
def step_xil_with_module(context, module_block):
    """Create an XIL file with a specific module block"""
    context.xil_content = f"""{module_block}
[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with use blocks')
def step_xil_with_use(context):
    """Create an XIL file with use blocks"""
    context.xil_content = """[module app]
[use builtin]
[use stdlib]

[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with a library block')
def step_xil_with_lib(context):
    """Create an XIL file with a library block"""
    context.xil_content = """[module app]
[lib "KERNEL32.DLL"]
exit="ExitProcess"

[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with an FFI declaration')
def step_xil_with_ffi(context):
    """Create an XIL file with an FFI declaration"""
    context.xil_content = """[module app]
[ffi]
exit=(code:i32)void

[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with a function containing a call statement')
def step_xil_with_call(context):
    """Create an XIL file with a function containing a call statement"""
    context.xil_content = """[module app]
[ffi]
exit=(code:i32)void

[fun.main]
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with a function containing an if statement')
def step_xil_with_if(context):
    """Create an XIL file with a function containing an if statement"""
    context.xil_content = """[module app]
[fun.main]
cmp=argn,1
if=1,no_args
label=no_args"""
    context.filename = "test.xil"


@given('an XIL file with a function containing a cmp statement')
def step_xil_with_cmp(context):
    """Create an XIL file with a function containing a cmp statement"""
    context.xil_content = """[module app]
[fun.main]
cmp=argn,1"""
    context.filename = "test.xil"


@given('an XIL file with a function containing a label statement')
def step_xil_with_label(context):
    """Create an XIL file with a function containing a label statement"""
    context.xil_content = """[module app]
[fun.main]
label=start
call=exit,0"""
    context.filename = "test.xil"


@given('an XIL file with a function containing an args statement')
def step_xil_with_args(context):
    """Create an XIL file with a function containing an args statement"""
    context.xil_content = """[module app]
[fun.main]
args=argn:i32,argv:ptr
call=exit,0"""
    context.filename = "test.xil"


@when('I translate the XIL content')
def step_translate_xil(context):
    """Translate the XIL content"""
    try:
        context.translated_object = translator.translate(context.filename, context.xil_content)
        context.translation_error = None
    except Exception as e:
        context.translation_error = e


@then('the translation should succeed')
def step_translation_succeeds(context):
    """Verify translation succeeded"""
    assert context.translation_error is None, \
        f"Translation failed with error: {context.translation_error}"
    assert context.translated_object is not None, "Translated object should not be None"


@then('the result should contain a "{field}" field')
def step_result_has_field(context, field):
    """Verify the result contains a specific field"""
    assert field in context.translated_object, \
        f"Result should contain '{field}' field, but got: {list(context.translated_object.keys())}"


@then('the result should contain a "{field}" list')
def step_result_has_list_field(context, field):
    """Verify the result contains a list field"""
    assert field in context.translated_object, \
        f"Result should contain '{field}' field"
    assert isinstance(context.translated_object[field], list), \
        f"Field '{field}' should be a list, but is {type(context.translated_object[field])}"


@then('the result should contain a "{field}" dictionary')
def step_result_has_dict_field(context, field):
    """Verify the result contains a dictionary field"""
    assert field in context.translated_object, \
        f"Result should contain '{field}' field"
    assert isinstance(context.translated_object[field], dict), \
        f"Field '{field}' should be a dictionary, but is {type(context.translated_object[field])}"


@then('the module name should be "{name}"')
def step_module_name_is(context, name):
    """Verify the module name"""
    assert context.translated_object['module'] == name, \
        f"Expected module name '{name}', but got '{context.translated_object['module']}'"


@then('the use list should contain the module names')
def step_use_contains_modules(context):
    """Verify the use list contains module names"""
    assert 'use' in context.translated_object, "Result should contain 'use' field"
    assert isinstance(context.translated_object['use'], list), "'use' should be a list"
    assert len(context.translated_object['use']) > 0, "Use list should not be empty"


@then('the libs dictionary should contain the library name')
def step_libs_contains_library(context):
    """Verify the libs dictionary contains library names"""
    assert 'libs' in context.translated_object, "Result should contain 'libs' field"
    assert isinstance(context.translated_object['libs'], dict), "'libs' should be a dictionary"
    assert len(context.translated_object['libs']) > 0, "Libs dictionary should not be empty"


@then('the library should contain imported symbols')
def step_library_has_symbols(context):
    """Verify the library contains imported symbols"""
    libs = context.translated_object['libs']
    for lib_name, symbols in libs.items():
        assert isinstance(symbols, dict), f"Library '{lib_name}' should contain a dictionary of symbols"
        assert len(symbols) > 0, f"Library '{lib_name}' should contain at least one symbol"


@then('the ffi dictionary should contain the function name')
def step_ffi_contains_function(context):
    """Verify the ffi dictionary contains function names"""
    assert 'ffi' in context.translated_object, "Result should contain 'ffi' field"
    assert isinstance(context.translated_object['ffi'], dict), "'ffi' should be a dictionary"
    assert len(context.translated_object['ffi']) > 0, "FFI dictionary should not be empty"


@then('the function should have arguments')
def step_function_has_arguments(context):
    """Verify the function has arguments"""
    ffi = context.translated_object['ffi']
    for func_name, func_decl in ffi.items():
        assert 'args' in func_decl, f"Function '{func_name}' should have 'args' field"
        assert isinstance(func_decl['args'], list), f"Function '{func_name}' args should be a list"


@then('the function should have a return type')
def step_function_has_return_type(context):
    """Verify the function has a return type"""
    ffi = context.translated_object['ffi']
    for func_name, func_decl in ffi.items():
        assert 'returns' in func_decl, f"Function '{func_name}' should have 'returns' field"


@then('the function should contain a call statement')
def step_function_has_call(context):
    """Verify the function contains a call statement"""
    fun = context.translated_object['fun']
    found_call = False
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'call' in stmt:
                found_call = True
                break
    assert found_call, "Function should contain a call statement"


@then('the call statement should have the function name and arguments')
def step_call_has_name_and_args(context):
    """Verify the call statement has function name and arguments"""
    fun = context.translated_object['fun']
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'call' in stmt:
                call_value = stmt['call']
                assert isinstance(call_value, list), "Call should be a list"
                assert len(call_value) > 0, "Call should have at least the function name"
                return


@then('the function should contain an if statement')
def step_function_has_if(context):
    """Verify the function contains an if statement"""
    fun = context.translated_object['fun']
    found_if = False
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'if' in stmt:
                found_if = True
                break
    assert found_if, "Function should contain an if statement"


@then('the if statement should have condition and label')
def step_if_has_condition_and_label(context):
    """Verify the if statement has condition and label"""
    fun = context.translated_object['fun']
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'if' in stmt:
                if_value = stmt['if']
                assert isinstance(if_value, list), "If should be a list"
                assert len(if_value) >= 2, "If should have condition and label"
                return


@then('the function should contain a cmp statement')
def step_function_has_cmp(context):
    """Verify the function contains a cmp statement"""
    fun = context.translated_object['fun']
    found_cmp = False
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'cmp' in stmt:
                found_cmp = True
                break
    assert found_cmp, "Function should contain a cmp statement"


@then('the cmp statement should have operands')
def step_cmp_has_operands(context):
    """Verify the cmp statement has operands"""
    fun = context.translated_object['fun']
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'cmp' in stmt:
                cmp_value = stmt['cmp']
                assert isinstance(cmp_value, list), "Cmp should be a list"
                assert len(cmp_value) >= 2, "Cmp should have at least two operands"
                return


@then('the function should contain a label statement')
def step_function_has_label(context):
    """Verify the function contains a label statement"""
    fun = context.translated_object['fun']
    found_label = False
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'label' in stmt:
                found_label = True
                break
    assert found_label, "Function should contain a label statement"


@then('the label statement should have the label name')
def step_label_has_name(context):
    """Verify the label statement has a label name"""
    fun = context.translated_object['fun']
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'label' in stmt:
                label_value = stmt['label']
                assert isinstance(label_value, str), "Label should be a string"
                assert len(label_value) > 0, "Label should not be empty"
                return


@then('the function should contain an args statement')
def step_function_has_args(context):
    """Verify the function contains an args statement"""
    fun = context.translated_object['fun']
    found_args = False
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'args' in stmt:
                found_args = True
                break
    assert found_args, "Function should contain an args statement"


@then('the args statement should contain argument definitions with name and type')
def step_args_has_definitions(context):
    """Verify the args statement contains argument definitions"""
    fun = context.translated_object['fun']
    for func_name, statements in fun.items():
        for stmt in statements:
            if 'args' in stmt:
                args_value = stmt['args']
                assert isinstance(args_value, list), "Args should be a list"
                assert len(args_value) > 0, "Args should contain at least one argument"
                for arg in args_value:
                    assert 'name' in arg, "Each argument should have a 'name' field"
                    assert 'type' in arg, "Each argument should have a 'type' field"
                return

