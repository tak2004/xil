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
            module = line[7:-1].split(' ')[1]
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
        elif line.startswith('[fun.') and line.endswith(']'):
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
                decl['args'] = [{'name':arg.split(':')[0], 'type':arg.split(':')[1]} for arg in args]
                decl['returns'] = ret
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
          elif line.startswith('if='):
            current_fun.append({'if':line[3:].split(',')})
          elif line.startswith('cmp='):
            current_fun.append({'cmp':line[4:].split(',')})
          elif line.startswith('args='):
            current_fun.append({
                'args':[
                    {'name':arg.split(':')[0], 
                     'type':arg.split(':')[1]} for arg in line[5:].split(',')]})
          else:
            print("Parse error: Unexpected instruction: ", line)
        else:
            print("Parse error: Unexpected line: ",  line)
    return {'unit': file, 'module':module, 'use':use, 'libs':libs, 'ffi':ffi, 'fun':fun}


def processStatement(stmt, asg, nt_counter):
    nt_counter[NodeType.STATEMENT] += 1
    asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.STATEMENT], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.STATEMENT, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))
    if 'label' in stmt and stmt['label']:
        nt_counter[NodeType.OPLABEL] += 1
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.OPLABEL], sink_id=nt_counter[NodeType.STATEMENT], src_type=NodeType.OPLABEL, sink_type=NodeType.STATEMENT, type=EdgeType.PARENTCHILD))
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.OPLABEL], sink_id=len(asg['strings'].elements), src_type=NodeType.OPLABEL, sink_type=NodeType.ID, type=EdgeType.STRING))
        asg['strings'].elements.append(stmt['label'])
    elif 'call' in stmt and stmt['call']:
        nt_counter[NodeType.CALL] += 1
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.OPCALL], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.CALL, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))
    elif 'if' in stmt and stmt['if']:
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.IF], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.IF, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))    
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.IF], sink_id=len(asg['strings'].elements), src_type=NodeType.IF, sink_type=NodeType.ID, type=EdgeType.STRING))
        asg['strings'].elements.append(stmt['if'])
        nt_counter[NodeType.IF] += 1
    elif 'cmp' in stmt and stmt['cmp']:
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.CMP], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.CMP, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))  
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.CMP], sink_id=len(asg['strings'].elements), src_type=NodeType.CMP, sink_type=NodeType.ID, type=EdgeType.STRING))
        asg['strings'].elements.append(stmt['cmp'])
        nt_counter[NodeType.CMP] += 1
    elif 'args' in stmt and stmt['args']:
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.ARGS], sink_id=nt_counter[NodeType.FUNCTION], src_type=NodeType.ARGS, sink_type=NodeType.FUNCTION, type=EdgeType.PARENTCHILD))
        asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.ARGS], sink_id=len(asg['strings'].elements), src_type=NodeType.ARGS, sink_type=NodeType.ID, type=EdgeType.STRING))
        asg['strings'].elements.append(stmt['args'])
        nt_counter[NodeType.ARGS] += 1
        for arg in stmt['args']:
            nt_counter[NodeType.FUNCTIONARGUMENT] += 1
            asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.FUNCTIONARGUMENT], sink_id=nt_counter[NodeType.ARGS], src_type=NodeType.FUNCTIONARGUMENT, sink_type=NodeType.ARGS, type=EdgeType.PARENTCHILD))
            asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.FUNCTIONARGUMENT], sink_id=len(asg['strings'].elements), src_type=NodeType.FUNCTIONARGUMENT, sink_type=NodeType.ID, type=EdgeType.STRING))
            asg['strings'].elements.append(arg['name'])
            nt_counter[NodeType.TYPE] += 1
            asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=nt_counter[NodeType.FUNCTIONARGUMENT], src_type=NodeType.TYPE, sink_type=NodeType.FUNCTIONARGUMENT, type=EdgeType.PARENTCHILD))
            asg['edges'].elements.append(Edge(src_id=nt_counter[NodeType.TYPE], sink_id=len(asg['strings'].elements), src_type=NodeType.TYPE, sink_type=NodeType.ID, type=EdgeType.STRING))
            asg['strings'].elements.append(arg['type'])

def python_object_to_graph(object):
    print(object)
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