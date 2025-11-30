import translator
import virtual_machine
import asg_utils
import yaml
from pathlib import Path


def validate_yaml(yaml_data: dict) -> None:
    """
    Validates YAML data for required fields and their types.
    
    Required fields:
    - apiVersion: String
    - name: String
    - description: String
    - type: String
    - version: String
    - appVersion: String
    - files: List of strings
    
    Args:
        yaml_data: Dictionary containing the YAML data
    
    Raises:
        ValueError: If a required field is missing or has the wrong type
    """
    if not isinstance(yaml_data, dict):
        raise ValueError("YAML data must be a dictionary")
    
    # Required string fields
    string_fields = ['apiVersion', 'name', 'description', 'type', 'version', 'appVersion']
    
    for field in string_fields:
        if field not in yaml_data:
            raise ValueError(f"Required field '{field}' is missing")
        if not isinstance(yaml_data[field], str):
            raise ValueError(f"Field '{field}' must be of type string, but is {type(yaml_data[field]).__name__}")
    
    # Check 'files' field
    if 'files' not in yaml_data:
        raise ValueError("Required field 'files' is missing")
    
    if not isinstance(yaml_data['files'], list):
        raise ValueError(f"Field 'files' must be a list, but is {type(yaml_data['files']).__name__}")
    
    # Check that all elements in 'files' are strings
    for i, file_item in enumerate(yaml_data['files']):
        if not isinstance(file_item, str):
            raise ValueError(f"Element {i} in 'files' must be a string, but is {type(file_item).__name__}")


def load_yaml(file_path: str | Path) -> dict:
    """
    Loads a YAML file and returns its content as a dictionary.
    
    Args:
        file_path: Path to the YAML file (string or Path object)
    
    Returns:
        Dictionary containing the YAML file content
    
    Raises:
        FileNotFoundError: If the file is not found
        yaml.YAMLError: If the YAML file cannot be parsed
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
   try:
      yaml_data = load_yaml('xil.yaml')
      validate_yaml(yaml_data)      
   except FileNotFoundError as e:
      print(f"Error loading YAML file: {e}")
      exit(1)
   except yaml.YAMLError as e:
      print(f"Error parsing YAML file: {e}")
      exit(1)
   except ValueError as e:
      print(f"Validation error: {e}")
      exit(1)
   for file in yaml_data['files']:
      filename = Path(file).name
      with open(filename, 'r', encoding='utf-8') as f:
         content = f.read()
         python_object = translator.translate(filename, content)
         graph = translator.python_object_to_graph(python_object)
         asg_utils.graph_to_mermaid(graph)
         virtual_machine.run(graph)