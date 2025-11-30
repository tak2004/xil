from behave import given, when, then
import yaml
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from main import load_yaml, validate_yaml


@given('a valid YAML file exists')
def step_valid_yaml_file(context):
    """Create a temporary valid YAML file"""
    yaml_content = """
apiVersion: v1beta1
name: test app
description: Test description
type: app
version: 1.0.0
appVersion: dev
files:
  - test.xil
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        context.yaml_file = f.name


@given('a YAML file with missing required field "{field}"')
def step_yaml_missing_field(context, field):
    """Create a YAML file missing a required field"""
    yaml_content = {
        'apiVersion': 'v1beta1',
        'name': 'test app',
        'description': 'Test description',
        'type': 'app',
        'version': '1.0.0',
        'appVersion': 'dev',
        'files': ['test.xil']
    }
    yaml_content.pop(field, None)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        context.yaml_file = f.name


@given('a YAML file where "{field}" is not a string')
def step_yaml_wrong_type(context, field):
    """Create a YAML file with wrong type for a field"""
    yaml_content = {
        'apiVersion': 'v1beta1',
        'name': 'test app',
        'description': 'Test description',
        'type': 'app',
        'version': '1.0.0',
        'appVersion': 'dev',
        'files': ['test.xil']
    }
    yaml_content[field] = 123  # Not a string
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        context.yaml_file = f.name


@given('a YAML file where "files" is not a list')
def step_yaml_files_not_list(context):
    """Create a YAML file where files is not a list"""
    yaml_content = {
        'apiVersion': 'v1beta1',
        'name': 'test app',
        'description': 'Test description',
        'type': 'app',
        'version': '1.0.0',
        'appVersion': 'dev',
        'files': 'not a list'  # Should be a list
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        context.yaml_file = f.name


@given('a YAML file where "files" contains a non-string element')
def step_yaml_files_non_string(context):
    """Create a YAML file where files contains non-string elements"""
    yaml_content = {
        'apiVersion': 'v1beta1',
        'name': 'test app',
        'description': 'Test description',
        'type': 'app',
        'version': '1.0.0',
        'appVersion': 'dev',
        'files': ['test.xil', 123]  # Contains non-string
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        context.yaml_file = f.name


@given('a YAML file that does not exist')
def step_yaml_file_not_exist(context):
    """Set a non-existent YAML file path"""
    context.yaml_file = 'non_existent_file_12345.yaml'


@when('I load the YAML file')
def step_load_yaml(context):
    """Load the YAML file"""
    try:
        context.yaml_data = load_yaml(context.yaml_file)
        context.load_error = None
    except Exception as e:
        context.load_error = e


@when('I load and validate the YAML file')
def step_load_and_validate_yaml(context):
    """Load and validate the YAML file"""
    try:
        context.yaml_data = load_yaml(context.yaml_file)
        validate_yaml(context.yaml_data)
        context.validation_error = None
    except Exception as e:
        context.validation_error = e


@when('I try to load the YAML file')
def step_try_load_yaml(context):
    """Try to load the YAML file"""
    try:
        context.yaml_data = load_yaml(context.yaml_file)
        context.load_error = None
    except FileNotFoundError as e:
        context.load_error = e


@then('the YAML data should be loaded successfully')
def step_yaml_loaded_successfully(context):
    """Verify YAML was loaded successfully"""
    assert context.load_error is None, f"Expected no error, but got: {context.load_error}"
    assert context.yaml_data is not None, "YAML data should not be None"


@then('the YAML data should contain all required fields')
def step_yaml_has_required_fields(context):
    """Verify YAML contains all required fields"""
    required_fields = ['apiVersion', 'name', 'description', 'type', 'version', 'appVersion', 'files']
    for field in required_fields:
        assert field in context.yaml_data, f"Required field '{field}' is missing"


@then('a ValueError should be raised')
def step_value_error_raised(context):
    """Verify a ValueError was raised"""
    assert context.validation_error is not None, "Expected ValueError but no error was raised"
    assert isinstance(context.validation_error, ValueError), f"Expected ValueError, got {type(context.validation_error)}"


@then('the error message should contain "{message}"')
def step_error_contains_message(context, message):
    """Verify error message contains specific text"""
    error_msg = str(context.validation_error)
    assert message in error_msg, f"Expected '{message}' in error message, but got: {error_msg}"


@then('the error message should indicate the wrong type')
def step_error_indicates_wrong_type(context):
    """Verify error message indicates wrong type"""
    error_msg = str(context.validation_error)
    assert 'must be of type string' in error_msg or 'must be' in error_msg, \
        f"Expected type error message, but got: {error_msg}"


@then('the error message should indicate "files" must be a list')
def step_error_files_must_be_list(context):
    """Verify error message indicates files must be a list"""
    error_msg = str(context.validation_error)
    assert 'files' in error_msg and 'list' in error_msg, \
        f"Expected 'files' and 'list' in error message, but got: {error_msg}"


@then('the error message should indicate the element must be a string')
def step_error_element_must_be_string(context):
    """Verify error message indicates element must be a string"""
    error_msg = str(context.validation_error)
    assert 'must be a string' in error_msg, \
        f"Expected 'must be a string' in error message, but got: {error_msg}"


@then('a FileNotFoundError should be raised')
def step_file_not_found_error(context):
    """Verify a FileNotFoundError was raised"""
    assert context.load_error is not None, "Expected FileNotFoundError but no error was raised"
    assert isinstance(context.load_error, FileNotFoundError), \
        f"Expected FileNotFoundError, got {type(context.load_error)}"


# Cleanup is handled in features/environment.py

