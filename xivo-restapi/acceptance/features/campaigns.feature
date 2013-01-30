Feature: Recording campaign management

	In order to execute call quality assessment
	
	Scenario: Campaign creation and consultation
	  Given there is no campaign
	  When I create a campaign "test_campaign"
	  Then I can consult this campaign
	  
	Scenario: Campaign creation and consultation with accents
	  Given there is no campaign
	  When I create a campaign "accents_éèà&"
	  Then I can consult this campaign
	  
	Scenario: Get activated campaigns
	  Given there is no campaign
	  Given there is an activated campaign named "quality" focusing queue "test1"
	  Given there is an non activated campaign named "disabled" focusing queue "test2"	   
	  When I ask for activated campaigns for queue "test1"
	  Then I get a list of activated campaigns with campaign "quality"

	Scenario: Campaign edition
	  Given there is no campaign
	  Given there is a queue "test1" and a queue "test2"
	  Given I create a campaign "lettuce" pointing to queue "test1" with start date "2012-01-01 00:00:00" and end date "2013-05-05 14:59:14"
	  When I change its name to "lettuce_updated", its queue to "test2", its start date to "2012-02-01 00:11:00" and its end date to "2013-04-05 12:59:14"
	  Then the campaign is actually modified

	Scenario: Consulting running and activated campaigns for a given queue
	  Given there is no campaign
	  Given there is a queue "1" and a queue "2"
	  Given I create an activated campaign "lettuce1" pointing to queue "test1" currently running
	  Given I create an activated campaign "lettuce2" pointing to queue "test2" currently running
	  Given I create an activated campaign "lettuce3" pointing to queue "test1" currently not running
	  When I ask for running and activated campaigns for queue "test1"
	  Then I get campaign "lettuce1", I do not get "lettuce2", "lettuce3"
	  
	Scenario: Campaign creation and consultation without dates
	  Given there is no campaign
	  When I create a campaign "test_dates" without dates
	  Then this campaign is created with its start date and end date equal to now
	  
	Scenario: Campaign creation and consultation with unproprer dates
	  Given there is no campaign
	  When I create the campaign "test_unproper_dates" with start date "2013-02-01" and end date "2013-01-01"
	  Then I get an error code '400' with message 'start_greater_than_end'
	  
	Scenario: Consistent number of campaigns
	  Given there is no campaign
	  When I ask for all the campaigns
	  Then the displayed total is equal to the actual number of campaigns
	  
	Scenario: Campaign pagination
	  Given there is no campaign
	  Given there are at least "10" campaigns
	  When I ask for a list of campaigns with page "1" and page size "5"
	  Then I get exactly "5" campaigns
	  
	Scenario: No overlapping when paginating campaigns
	  Given there is no campaign
	  Given there are at least "10" campaigns
	  Given I ask for a list of campaigns with page "1" and page size "5"
	  Given I ask for a list of campaigns with page "2" and page size "5"
	  Then the two results do not overlap
	  
	Scenario: Campaign dates overlapping
	  Given there is no campaign
	  Given I create a campaign "test1" pointing to queue "test" with start date "2013-01-01" and end date "2013-02-01"
	  When I try to create a campaign "test2" pointing to queue "test" with start date "2013-01-15" and end date "2013-02-15"
	  Then I get an error code '400' with message 'concurrent_campaigns'
	  
	Scenario: Queue deletion
	  Given there is no campaign
	  Given I create a campaign "test1" pointing to queue "test" with start date "2013-01-01" and end date "2013-02-01"
	  When I delete the queue "test"
	  Then the queue "test" is actually deleted
	  Then I can get the campaign "test1" with an empty queue_id
	  
	Scenario: Campaign remove fails because there are still some recordings
	  Given there is no campaign
	  Given I create a campaign "test_remove" pointing to queue "test" with start date "2013-01-01" and end date "2013-02-01"
	  Given there is at least one recording for the campaign "test_remove"
	  When I ask to delete the campaign "test_remove"
	  Then I get an error code '412' with message 'campaign_not_empty'
	  
	Scenario: Campaign remove success
	  Given there is no campaign
	  Given I create a campaign "test_remove" pointing to queue "test" with start date "2013-01-01" and end date "2013-02-01"
	  Given there is not any recording for the campaign "test_remove"
	  When I ask to delete the campaign "test_remove"
	  Then I get a response with code '200' and the campaign is deleted

	Scenario: Campaign configuration and execution
	  Given there is no campaign
	  Given there is no campaign "quality",
	  Given I create a campaign named "quality",
	  Given I add queue "5001" for this campaign, 
	  When I start this campaign
	  Then calls placed in this queue are recorded 
	  