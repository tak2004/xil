Feature: Graph Creation
  As a compiler
  I want to create an abstract syntax graph from translated Python objects
  So that I can represent the code structure as a graph

  Scenario: Graph is created from Python object
    Given a translated Python object
    When I create a graph from the Python object
    Then the graph should contain edges
    And the graph should contain strings
    And the graph should contain textViews

  Scenario: Unit node is created correctly
    Given a Python object with a unit field
    When I create a graph from the Python object
    Then the graph should contain a UNIT node
    And the UNIT node should be connected to a string with the unit name

  Scenario: Module node is created correctly
    Given a Python object with a module field
    When I create a graph from the Python object
    Then the graph should contain a MODULE node
    And the MODULE node should be connected to the UNIT node
    And the MODULE node should be connected to a string with the module name

  Scenario: Use nodes are created correctly
    Given a Python object with use statements
    When I create a graph from the Python object
    Then the graph should contain USE nodes
    And each USE node should be connected to the MODULE node
    And each USE node should be connected to strings with module names

  Scenario: Library nodes are created correctly
    Given a Python object with library definitions
    When I create a graph from the Python object
    Then the graph should contain LIBRARY nodes
    And each LIBRARY node should be connected to the MODULE node
    And each LIBRARY node should have IMPORTLIBRARY child nodes
    And each IMPORTLIBRARY node should be connected to strings

  Scenario: FFI nodes are created correctly
    Given a Python object with FFI declarations
    When I create a graph from the Python object
    Then the graph should contain FFI nodes
    And each FFI node should be connected to the MODULE node
    And each FFI node should have FUNCTIONARGUMENT child nodes
    And each FUNCTIONARGUMENT should have TYPE child nodes

  Scenario: Function nodes are created correctly
    Given a Python object with function definitions
    When I create a graph from the Python object
    Then the graph should contain FUNCTION nodes
    And each FUNCTION node should be connected to the MODULE node
    And each FUNCTION node should be connected to a string with the function name

  Scenario: Statement nodes are created correctly
    Given a Python object with functions containing statements
    When I create a graph from the Python object
    Then the graph should contain STATEMENT nodes
    And each STATEMENT node should be connected to its FUNCTION node

  Scenario: Call operation nodes are created correctly
    Given a Python object with call statements
    When I create a graph from the Python object
    Then the graph should contain OPCALL nodes
    And each OPCALL node should be connected to its STATEMENT node

  Scenario: Label operation nodes are created correctly
    Given a Python object with label statements
    When I create a graph from the Python object
    Then the graph should contain OPLABEL nodes
    And each OPLABEL node should be connected to its STATEMENT node
    And each OPLABEL node should be connected to a string with the label name

  Scenario: Edge types are correctly assigned
    Given a Python object with various elements
    When I create a graph from the Python object
    Then edges should have PARENTCHILD type for hierarchical relationships
    And edges should have STRING type for string references
    And edges should have TEXTVIEW type for text view references when applicable

