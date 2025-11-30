from schema import EdgeType

def graph_to_mermaid(graph):
    for e in graph['edges'].elements:
        if e.type == EdgeType.STRING:
            print(f"{e.src_type.name}-{e.src_id} --> {graph['strings'].elements[e.sink_id]}")
        elif e.type == EdgeType.TEXTVIEW:
            print(f"{e.src_type.name}-{e.src_id} --> TextView[{graph['textViews'].elements[e.sink_id].row},{graph['textViews'].elements[e.sink_id].column}]")
        else:
            print(f"{e.src_type.name}-{e.src_id} --> {e.sink_type.name}-{e.sink_id}")