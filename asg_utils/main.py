from schema import EdgeType
from collections import defaultdict

def generateModules(python_objects):
    # Group python_objects by module
    grouped = defaultdict(list)
    for python_object in python_objects:
        module = python_object['module']
        grouped[module].append(python_object)
    
    # Merge objects with the same module
    merged_objects = []
    for module, objects in grouped.items():
        merged = {
            'unit': [],
            'module': module,
            'use': [],
            'libs': {},
            'ffi': {},
            'fun': {}
        }
        
        # Collect all units
        for obj in objects:
            unit = obj.get('unit')
            if unit and unit not in merged['unit']:
                merged['unit'].append(unit)
        
        # Merge use lists (union, no duplicates)
        for obj in objects:
            merged['use'].extend(obj.get('use', []))
        merged['use'] = list(dict.fromkeys(merged['use']))  # Remove duplicates while preserving order
        
        # Merge libs dictionaries (merge inner dictionaries for same keys)
        for obj in objects:
            for lib_name, lib_content in obj.get('libs', {}).items():
                if lib_name not in merged['libs']:
                    merged['libs'][lib_name] = {}
                merged['libs'][lib_name].update(lib_content)
        
        # Merge ffi dictionaries
        for obj in objects:
            merged['ffi'].update(obj.get('ffi', {}))
        
        # Merge fun dictionaries
        for obj in objects:
            merged['fun'].update(obj.get('fun', {}))
        
        merged_objects.append(merged)
    return merged_objects

def graph_to_mermaid(graph):
    for e in graph['edges'].elements:
        if e.type == EdgeType.STRING:
            print(f"{e.src_type.name}-{e.src_id} --> {graph['strings'].elements[e.sink_id]}")
        elif e.type == EdgeType.TEXTVIEW:
            print(f"{e.src_type.name}-{e.src_id} --> TextView[{graph['textViews'].elements[e.sink_id].row},{graph['textViews'].elements[e.sink_id].column}]")
        else:
            print(f"{e.src_type.name}-{e.src_id} --> {e.sink_type.name}-{e.sink_id}")