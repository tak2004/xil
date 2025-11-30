"""
Behave environment configuration for BDD tests.
Provides setup and teardown hooks for test execution.
"""

from behave import fixture, use_fixture
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def before_all(context):
    """Run before all features are executed"""
    # Set up any global test configuration
    context.project_root = project_root
    context.test_data_dir = os.path.join(project_root, 'tests')


def after_all(context):
    """Run after all features are executed"""
    # Clean up any global resources
    pass


def before_feature(context, feature):
    """Run before each feature file"""
    # Set up feature-specific configuration
    pass


def after_feature(context, feature):
    """Run after each feature file"""
    # Clean up feature-specific resources
    pass


def before_scenario(context, scenario):
    """Run before each scenario"""
    # Initialize scenario-specific context variables
    context.scenario_name = scenario.name
    # Clear any previous state
    if hasattr(context, 'yaml_file'):
        delattr(context, 'yaml_file')
    if hasattr(context, 'yaml_data'):
        delattr(context, 'yaml_data')
    if hasattr(context, 'translated_object'):
        delattr(context, 'translated_object')
    if hasattr(context, 'graph'):
        delattr(context, 'graph')
    if hasattr(context, 'mermaid_output'):
        delattr(context, 'mermaid_output')


def after_scenario(context, scenario):
    """Run after each scenario"""
    # Clean up scenario-specific resources
    import os
    # Clean up temporary files
    if hasattr(context, 'yaml_file') and os.path.exists(context.yaml_file):
        try:
            os.unlink(context.yaml_file)
        except:
            pass
    
    # Clear context variables
    for attr in ['yaml_file', 'yaml_data', 'translated_object', 'graph', 'mermaid_output', 
                 'load_error', 'validation_error', 'translation_error', 'graph_error']:
        if hasattr(context, attr):
            try:
                delattr(context, attr)
            except:
                pass


def before_step(context, step):
    """Run before each step"""
    pass


def after_step(context, step):
    """Run after each step"""
    # Log step execution if needed
    pass

