Feature: Mermaid Diagram Generation
  As a developer
  I want to generate Mermaid diagrams from abstract syntax graphs
  So that I can visualize the code structure

  Scenario: Mermaid diagram is generated from graph
    Given an abstract syntax graph
    When I generate a Mermaid diagram from the graph
    Then a Mermaid diagram string should be returned
    And the diagram should start with "graph TD"

  Scenario: Mermaid diagram contains all edges
    Given an abstract syntax graph with edges
    When I generate a Mermaid diagram from the graph
    Then the diagram should contain all edges from the graph
    And each edge should be in Mermaid syntax

  Scenario: String edges are converted correctly
    Given an abstract syntax graph with STRING type edges
    When I generate a Mermaid diagram from the graph
    Then the diagram should contain edges pointing to string values
    And string values should be properly quoted

  Scenario: Parent-child edges are converted correctly
    Given an abstract syntax graph with PARENTCHILD type edges
    When I generate a Mermaid diagram from the graph
    Then the diagram should contain edges between node types
    And node types should be formatted as "NodeType-id"

  Scenario: TextView edges are converted correctly
    Given an abstract syntax graph with TEXTVIEW type edges
    When I generate a Mermaid diagram from the graph
    Then the diagram should contain TextView nodes
    And TextView nodes should show row and column information

  Scenario: Mermaid syntax is valid
    Given an abstract syntax graph
    When I generate a Mermaid diagram from the graph
    Then the diagram should be valid Mermaid syntax
    And the diagram can be rendered by Mermaid parsers

