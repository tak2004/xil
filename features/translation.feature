Feature: XIL Translation
  As a compiler
  I want to translate XIL code to Python objects
  So that I can process the abstract syntax representation

  Scenario: Simple XIL file is translated successfully
    Given a simple XIL file with module, use, lib, ffi and fun blocks
    When I translate the XIL content
    Then the translation should succeed
    And the result should contain a "unit" field
    And the result should contain a "module" field
    And the result should contain a "use" list
    And the result should contain a "libs" dictionary
    And the result should contain a "ffi" dictionary
    And the result should contain a "fun" dictionary

  Scenario: Module block is parsed correctly
    Given an XIL file with a module block "[module app]"
    When I translate the XIL content
    Then the module name should be "app"

  Scenario: Use block is parsed correctly
    Given an XIL file with use blocks
    When I translate the XIL content
    Then the use list should contain the module names

  Scenario: Library block is parsed correctly
    Given an XIL file with a library block
    When I translate the XIL content
    Then the libs dictionary should contain the library name
    And the library should contain imported symbols

  Scenario: FFI block is parsed correctly
    Given an XIL file with an FFI declaration
    When I translate the XIL content
    Then the ffi dictionary should contain the function name
    And the function should have arguments
    And the function should have a return type

  Scenario: Function with call statement is parsed correctly
    Given an XIL file with a function containing a call statement
    When I translate the XIL content
    Then the function should contain a call statement
    And the call statement should have the function name and arguments

  Scenario: Function with if statement is parsed correctly
    Given an XIL file with a function containing an if statement
    When I translate the XIL content
    Then the function should contain an if statement
    And the if statement should have condition and label

  Scenario: Function with cmp statement is parsed correctly
    Given an XIL file with a function containing a cmp statement
    When I translate the XIL content
    Then the function should contain a cmp statement
    And the cmp statement should have operands

  Scenario: Function with label statement is parsed correctly
    Given an XIL file with a function containing a label statement
    When I translate the XIL content
    Then the function should contain a label statement
    And the label statement should have the label name

  Scenario: Function with args statement is parsed correctly
    Given an XIL file with a function containing an args statement
    When I translate the XIL content
    Then the function should contain an args statement
    And the args statement should contain argument definitions with name and type

