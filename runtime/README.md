# Concept

Runtime contains a JIT and linker.
Python VM runs the runtime code to utilize the JIT and build a standalone interpreter with the linker.
A standalone executable can be build by JIT the whole code, stripe runtime and unused functions.

# JIT

## Facts

The executable is compiled and linked for the specified combination.

| fact | known ✅ / ❌ | notes
|------|-------|-----|
| CPU architecture | ✅ | arm64/x64
| OS | ✅ | linux/windows
| CPU features | ❌ | e.g. AVX512, SSE4.1
| NUMA configuration | ❌ | CPU-Memory association
| CPU specs | ❌ | Logical Processor configuration, caches, ...
| Memory specs | ❌ | baseline speed, amount, pages, ...

## Assembler matching

XIL utilize functions for nearly all operations and xil templates allow to map functions to specific assembler instructions. This way a module is able to provide types, structs and functions with optimized assembler routines.
GoASM provides an battle proof solution which will be adopted by XIL.
This way it takes very little assembler code in the XIL runtime because the modules are providing the pattern and necessary code.
The JIT can load the specialized modules of the found facts if available to utilize the hardware.

## Module specialization

Auswirkung auf code haben folgende dinge.

* Architecture
* OS
* CPU-Features

Der Modulname ist frei wählbar und wird in der xil.yaml restriktiert.

## Types

```xil
[type integer32bit]
bytes=4
align=8

[struct file]
i32=bytes
str=path
embed=file_stats
```

### Builtin Types

* builtin.intLiteral
* builtin.strLiteral
* builtin.boolLiteral