Feature: Extensions

    Scenario: Extension list with no extensions
        Given I have no extensions
        When I access the list of extensions
        Then I get a list with only the default extensions

    Scenario: Extension list with one extension
        Given I only have the following extensions:
            | exten | context | type | typeval |
            | 1000  | default | user | 1       |
        When I access the list of extensions
        Then I get a list containing the following extensions:
            | exten | context |
            | 1000  | default |

    Scenario: Extension list with one extension
        Given I only have the following extensions:
            | exten | context | type | typeval |
            | 1001  | default | user | 2       |
            | 1000  | default | user | 1       |
        When I access the list of extensions
        Then I get a list containing the following extensions:
            | exten | context |
            | 1000  | default |
            | 1001  | default |

    Scenario: Get an extension that does not exist
        Given I have no extensions
        When I access the extension with id "100"
        Then I get a response with status "404"

    Scenario: Get an extension
        Given I only have the following extensions:
            | id  | exten | context | type | typeval |
            | 100 | 2000  | default | user | 1       |
        When I access the extension with id "100"
        Then I get a response with status "200"
        Then I have an extension with the following properties:
            | id  | exten | context |
            | 100 | 2000  | default |

    Scenario: Creating an empty extension
        Given I have no extensions
        When I create an empty extension
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: exten,context"

    Scenario: Creating an extension with an empty number:
        Given I have no extensions
        When I create an extension with the following properties:
            | exten | context |
            |       | default |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Exten required"

    Scenario: Creating an extension with an empty context:
        Given I have no extensions
        When I create an extension with the following properties:
            | exten | context |
            | 1000  |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Context required"

    Scenario: Creating an extension with only the number
        Given I have no extensions
        When I create an extension with the following properties:
            | exten |
            | 1000  |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context"

    Scenario: Creating an extension with only the context
        Given I have no extensions
        When I create an extension with the following properties:
            | context |
            | default |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: exten"

    Scenario: Creating an extension with invalid parameters
        Given I have no extensions
        When I create an extension with the following properties:
            | toto |
            | tata |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: toto"

    Scenario: Creating an extension
        Given I have no extensions
        When I create an extension with the following properties:
            | exten | context |
            | 1000  | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response header with a location for the new extension
        Then I get a response with a link to an extension resource

    Scenario: Creating an alphanumeric extension
        Given I have no extensions
        When I create an extension with the following properties:
            | exten  | context |
            | ABC123 | context |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response header with a location for the new extension
        Then I get a response with a link to an extension resource

    Scenario: Creating twice the same extension
        Given I have no extensions
        When I create an extension with the following properties:
            | exten | context |
            | 1000  | default |
        Then I get a response with status "201"
        When I create an extension with the following properties:
            | exten | context |
            | 1000  | default |
        Then I get a response with status "400"
        Then I get an error message "Extension 1000@default already exists"

    Scenario: Creating two extensions in different contexts
        Given I have no extensions
        When I create an extension with the following properties:
            | exten | context |
            | 1000  | default |
        Then I get a response with status "201"
        When I create an extension with the following properties:
            | exten | context     |
            | 1000  | from-extern |
        Then I get a response with status "201"

    #Scenario: Creating an extension outside of context range
    #    Given I have no extensions
    #    When I create an extension with the following properties:
    #        | exten | context |
    #        | 99999 | default |
    #    Then I get a response with status "400"
    #    Then I get an error message "Invalid parameters: exten"

    #Scenario: Creating an extension with a context that doesn't exist
    #    Given I have no extensions
    #    When I create an extension with the following properties:
    #        | exten | context             |
    #        | 1000  | mysuperdupercontext |
    #    Then I get a response with status "400"
    #    Then I get an error message "Invalid parameters: context"

    Scenario: Delete an extension that doesn't exist
        Given I have no extensions
        When I delete extension "100"
        Then I get a response with status "404"

    Scenario: Delete an extension
        Given I only have the following extensions:
            | id  | exten | context | type | typeval |
            | 100 | 1000  | default | user | 1       |
        When I delete extension "100"
        Then I get a response with status "204"
        Then the extension "100" no longer exists