from schema import EdgeList, StringList, TextViewList, Edge, NodeType, EdgeType, TextView

def translate(file, content):
    lines = content.split('\n')
    currentBlock = None
    module = None
    use = []
    libs = {}
    current_lib = None
    ffi = {}
    fun = {}
    current_fun = None

    for line in lines:
        if line.startswith('[module') and line.endswith(']'):
            # Parse module name safely: [module name] or [module]
            module_part = line[7:-1].strip()  # Remove '[module' and ']'
            if module_part:
                # Split by space and take the last part (handles [module name] and [module name extra])
                parts = module_part.split()
                module = parts[0] if parts else None
            else:
                module = None
            currentBlock = 'module'
        elif line.startswith('[use') and line.endswith(']'):
            use.append(line[5:-1])
            currentBlock = 'use'
        elif line.startswith('[lib') and line.endswith(']'):
            name=line[5:-1].split('"')[1]
            libs[name] = {}
            current_lib = libs[name]
            currentBlock = 'lib'
        elif line.startswith('[ffi]'):
            currentBlock = 'ffi'
        elif line.startswith('[fun') and line.endswith(']'):
            fun[line[5:-1]] = []
            current_fun = fun[line[5:-1]]
            currentBlock = 'fun'
        elif line == '':
            continue
        elif currentBlock == 'ffi':
            key,value = line.split('=')            
            decl={'args':[],'returns':[]}
            if value.startswith('(') and value.index(')') != -1:
                args = value[1:value.index(')')].split(',')
                ret = value[value.index(')')+1:]
                decl['args'] = [{'name':arg.split(':')[0].strip(), 'type':arg.split(':')[1].strip()} for arg in args if ':' in arg]
                decl['returns'] = ret.strip()
            else:
                print("Parse error: Unexpected ffi declaration: ", line)
            ffi[key]=decl
        elif currentBlock == 'lib':
          key,value = line.split('=')
          current_lib[key]=value.split('"')[1]
        elif currentBlock == 'fun':
          if line.startswith('label='):
            current_fun.append({'label':line.split('=')[1]})
          elif line.startswith('call='):
            current_fun.append({'call':line[5:].split(',')})
          elif line.startswith('move='):
            current_fun.append({'move':line[5:].strip()})
          elif line.startswith('const='):
            current_fun.append({'const':line[6:].split(',')})
          elif line.startswith('if='):
            current_fun.append({'if':line[3:].split(',')})
          elif line.startswith('cmp='):
            current_fun.append({'cmp':line[4:].split(',')})
          elif line.startswith('decl='):
            # Parse decl=(arg1:type1,arg2:type2)retType
            decl_str = line[5:].strip()
            if decl_str.startswith('(') and ')' in decl_str:
                args_part = decl_str[1:decl_str.index(')')]
                ret_part = decl_str[decl_str.index(')')+1:]
                args = [arg.strip() for arg in args_part.split(',')] if args_part.strip() else []
                current_fun.append({
                    'decl': [
                        {'name': arg.split(':')[0].strip(), 
                         'type': arg.split(':')[1].strip()} for arg in args if ':' in arg
                    ],
                    'retType': ret_part.strip()
                })
            else:
                print("Parse error: Unexpected decl declaration: ", line)
          else:
            print("Parse error: Unexpected instruction: ", line)
        else:
            print("Parse error: Unexpected line: ",  line)
    return {'unit': file, 'module':module, 'use':use, 'libs':libs, 'ffi':ffi, 'fun':fun}

def isNumber(arg):
    return arg.isdigit()

def isStringLiteral(arg):
    return arg.startswith('"') and arg.endswith('"')

def processStatement(stmt, asg, nt_counter):
    nt_counter[NodeType.STATEMENT] += 1
    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.STATEMENT], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.STATEMENT, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))
    # Lookup-Tabelle von String auf NodeType OP-Werte
    op_to_nodetype = {
        'cmp': NodeType.OPCMP,
        'call': NodeType.OPCALL,
        'if': NodeType.OPIF,
        'label': NodeType.OPLABEL,
    }
    for key, value in stmt.items():
        if key in op_to_nodetype:
            nt_counter[op_to_nodetype[key]] += 1
            asg['edges'].elements.append(Edge(src_id=nt_counter[op_to_nodetype[key]], sink_id=nt_counter[NodeType.STATEMENT], src_type=op_to_nodetype[key], sink_type=NodeType.STATEMENT, type=EdgeType.PARENTCHILD))
            for arg in value:
                nt_counter[NodeType.FUNCTIONARGUMENT] += 1
                asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.FUNCTIONARGUMENT], sink_id=nt_counter[op_to_nodetype[key]], src_type=NodeType.FUNCTIONARGUMENT, sink_type=op_to_nodetype[key], type=EdgeType.PARENTCHILD))
                if isNumber(arg):
                    nt_counter[NodeType.NUMBER] += 1
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.NUMBER], sink_id=nt_counter[NodeType.FUNCTIONARGUMENT], src_type=NodeType.NUMBER, sink_type=NodeType.FUNCTIONARGUMENT, type=EdgeType.STRING))
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.NUMBER], sink_id=len(asg['strings'].elements), src_type=NodeType.NUMBER, sink_type=NodeType.ID, type=EdgeType.STRING))
                    asg['strings'].elements.append(arg)
                elif isStringLiteral(arg):
                    nt_counter[NodeType.STRING] += 1
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.STRING], sink_id=nt_counter[NodeType.FUNCTIONARGUMENT], src_type=NodeType.STRING, sink_type=NodeType.FUNCTIONARGUMENT, type=EdgeType.PARENTCHILD))
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.STRING], sink_id=len(asg['strings'].elements), src_type=NodeType.STRING, sink_type=NodeType.ID, type=EdgeType.STRING))
                    asg['strings'].elements.append(arg)
                else:
                    nt_counter[NodeType.ID] += 1
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.ID], sink_id=nt_counter[NodeType.FUNCTIONARGUMENT], src_type=NodeType.ID, sink_type=NodeType.FUNCTIONARGUMENT, type=EdgeType.PARENTCHILD))
                    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.ID], sink_id=len(asg['strings'].elements), src_type=NodeType.ID, sink_type=NodeType.ID, type=EdgeType.STRING))
                    asg['strings'].elements.append(arg)

def python_object_to_graph(object):
    #print(object)
    edges = EdgeList([])
    strings = StringList([])
    textViews = TextViewList([])
    nt_counter = {}
    asg = {'edges': edges, 'strings': strings, 'textViews': textViews}
    for nt in NodeType:
        nt_counter[nt] = 0
    for key, value in object.items():
        if key == 'unit':
            nt_counter[NodeType.UNIT] += 1
            edges.elements.append(Edge(src_id=nt_counter[NodeType.UNIT], sink_id=len(strings.elements), src_type=NodeType.UNIT, sink_type=NodeType.ID, type=EdgeType.STRING))
            strings.elements.append(value)            
        elif key == 'module':            
            nt_counter[NodeType.MODULE] += 1
            edges.elements.append(Edge(src_id=nt_counter[NodeType.MODULE], sink_id=nt_counter[NodeType.UNIT], src_type=NodeType.MODULE, sink_type=NodeType.UNIT, type=EdgeType.PARENTCHILD))
            edges.elements.append(Edge(src_id=nt_counter[NodeType.MODULE], sink_id=len(strings.elements), src_type=NodeType.MODULE, sink_type=NodeType.ID, type=EdgeType.STRING))
            strings.elements.append(value)            
        elif key == 'use':
            nt_counter[NodeType.USE] += 1
            edges.elements.append(Edge(src_id=nt_counter[NodeType.USE], sink_id=nt_counter[NodeType.MODULE], src_type=NodeType.USE, sink_type=NodeType.MODULE, type=EdgeType.PARENTCHILD))
            for use in value:
                edges.elements.append(Edge(src_id=nt_counter[NodeType.USE], sink_id=len(strings.elements), src_type=NodeType.USE, sink_type=NodeType.ID, type=EdgeType.STRING))
                strings.elements.append(use)
        elif key == 'libs':
            for lib in value:
                nt_counter[NodeType.LIBRARY] += 1
                edges.elements.append(Edge(src_id=nt_counter[NodeType.LIBRARY], sink_id=nt_counter[NodeType.MODULE], src_type=NodeType.LIBRARY, sink_type=NodeType.MODULE, type=EdgeType.PARENTCHILD))
                edges.elements.append(Edge(src_id=nt_counter[NodeType.LIBRARY], sink_id=len(strings.elements), src_type=NodeType.LIBRARY, sink_type=NodeType.ID, type=EdgeType.STRING))
                strings.elements.append(lib)
                for imp in value[lib]:
                    var = imp
                    libImport = value[lib][imp]
                    nt_counter[NodeType.IMPORTLIBRARY] += 1
                    nt_counter[NodeType.ID] += 1
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.IMPORTLIBRARY], sink_id=nt_counter[NodeType.LIBRARY], src_type=NodeType.IMPORTLIBRARY, sink_type=NodeType.LIBRARY, type=EdgeType.PARENTCHILD))
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.IMPORTLIBRARY], sink_id=len(strings.elements), src_type=NodeType.IMPORTLIBRARY, sink_type=NodeType.ID, type=EdgeType.STRING))
                    strings.elements.append(libImport)
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.ID], sink_id=nt_counter[NodeType.IMPORTLIBRARY], src_type=NodeType.ID, sink_type=NodeType.IMPORTLIBRARY, type=EdgeType.PARENTCHILD))
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.ID], sink_id=len(strings.elements), src_type=NodeType.ID, sink_type=NodeType.ID, type=EdgeType.STRING))
                    strings.elements.append(var)
        elif key == 'ffi':
            for ffi in value:
                nt_counter[NodeType.FFI] += 1
                edges.elements.append(Edge(src_id=nt_counter[NodeType.FFI], sink_id=nt_counter[NodeType.MODULE], src_type=NodeType.FFI, sink_type=NodeType.MODULE, type=EdgeType.PARENTCHILD))
                edges.elements.append(Edge(src_id=nt_counter[NodeType.FFI], sink_id=len(strings.elements), src_type=NodeType.FFI, sink_type=NodeType.ID, type=EdgeType.STRING))
                strings.elements.append(ffi)
                for fun in value[ffi]['args']:
                    nt_counter[NodeType.FUNCTIONARGUMENT] += 1
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.FUNCTIONARGUMENT], sink_id=nt_counter[NodeType.FFI], src_type=NodeType.FUNCTIONARGUMENT, sink_type=NodeType.FFI, type=EdgeType.PARENTCHILD))
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.FUNCTIONARGUMENT], sink_id=len(strings.elements), src_type=NodeType.FUNCTIONARGUMENT, sink_type=NodeType.ID, type=EdgeType.STRING))
                    strings.elements.append(fun['name'])
                    nt_counter[NodeType.TYPE] += 1
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=nt_counter[NodeType.FUNCTIONARGUMENT], src_type=NodeType.TYPE, sink_type=NodeType.FUNCTIONARGUMENT, type=EdgeType.PARENTCHILD))
                    edges.elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=len(strings.elements), src_type=NodeType.TYPE, sink_type=NodeType.ID, type=EdgeType.STRING))
                    strings.elements.append(fun['type'])
                ret = value[ffi]['returns']
                nt_counter[NodeType.TYPE] += 1
                edges.elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=nt_counter[NodeType.FFI], src_type=NodeType.TYPE, sink_type=NodeType.FFI, type=EdgeType.PARENTCHILD))
                edges.elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=len(strings.elements), src_type=NodeType.TYPE, sink_type=NodeType.ID, type=EdgeType.STRING))
                strings.elements.append(ret)
        elif key == 'fun':
            for fun in value:
                nt_counter[NodeType.FUNCTION] += 1
                edges.elements.append(Edge(src_id=nt_counter[NodeType.FUNCTION], sink_id=nt_counter[NodeType.MODULE], src_type=NodeType.FUNCTION, sink_type=NodeType.MODULE, type=EdgeType.PARENTCHILD))
                edges.elements.append(Edge(src_id=nt_counter[NodeType.FUNCTION], sink_id=len(strings.elements), src_type=NodeType.FUNCTION, sink_type=NodeType.ID, type=EdgeType.STRING))
                strings.elements.append(fun)
                for stmt in value[fun]:
                    processStatement(stmt, asg, nt_counter)
    return asg