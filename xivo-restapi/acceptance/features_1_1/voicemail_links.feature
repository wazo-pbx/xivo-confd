Feature: Link a user and a voicemail

    Scenario: Link a user with a voicemail that doesn't exist
        Given there is no voicemail with number "1060" and context "default"
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Kathryn   | Janeway  | 1060   | default | sip      |
        When I link user "Kathryn Janeway" with voicemail "1060@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: voicemail \d+ does not exist"

    Scenario: Link a voicemail with a user that has no line
        Given there are users with infos:
            | firstname | lastname |
            | Chakotay  | Marquis  |
        Given I have the following voicemails:
            | name             | number | context |
            | Chakotay Marquis | 1061   | default |
        When I link user "Chakotay Marquis" with voicemail "1061@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user \d+ has no line"

    Scenario: Link a voicemail with a user that has a SIP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tuvok     | Vulcan   | 1063   | default | sip      |
        Given I have the following voicemails:
            | name            | number | context |
            | Tuvok Vulcan    | 1063   | default |
        When I link user "Tuvok Vulcan" with voicemail "1063@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource

    Scenario: Link a voicemail with a user that has an SCCP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tom       | Paris    | 1064   | default | sccp     |
        Given I have the following voicemails:
            | name      | number | context |
            | Tom Paris | 1064   | default |
        When I link user "Tuvok Vulcan" with voicemail "1064@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource

    Scenario: Link a voicemail with a user that already has one
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name  | voicemail_number |
            | B'Elanna  | Torres   | 1065   | default | sip      | B'Elanna Torres | 1065             |
        When I link user "B'Elanna Torres" with voicemail "1065@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user \d+ already has a voicemail"

    Scenario: List link voicemail that doesn't exist
        Given there are users with infos:
            |id | firstname | lastname | number | context | protocol |
            | 1 | Tuvok     | Vulcan   | 1063   | default | sip      |
        When I send a request for the voicemail link for user "1" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: voicemail \d+ does not exist"
        