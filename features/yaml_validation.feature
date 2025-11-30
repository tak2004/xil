Feature: YAML Validation
  As a developer
  I want to validate YAML configuration files
  So that I can ensure they contain all required fields with correct types

  Scenario: Valid YAML file is successfully loaded
    Given a valid YAML file exists
    When I load the YAML file
    Then the YAML data should be loaded successfully
    And the YAML data should contain all required fields

  Scenario: Missing required field raises ValueError
    Given a YAML file with missing required field "apiVersion"
    When I load and validate the YAML file
    Then a ValueError should be raised
    And the error message should contain "Required field 'apiVersion' is missing"

  Scenario: Wrong field type raises ValueError
    Given a YAML file where "version" is not a string
    When I load and validate the YAML file
    Then a ValueError should be raised
    And the error message should indicate the wrong type

  Scenario: Invalid files field raises ValueError
    Given a YAML file where "files" is not a list
    When I load and validate the YAML file
    Then a ValueError should be raised
    And the error message should indicate "files" must be a list

  Scenario: Non-string element in files list raises ValueError
    Given a YAML file where "files" contains a non-string element
    When I load and validate the YAML file
    Then a ValueError should be raised
    And the error message should indicate the element must be a string

  Scenario: Non-existent YAML file raises FileNotFoundError
    Given a YAML file that does not exist
    When I try to load the YAML file
    Then a FileNotFoundError should be raised

