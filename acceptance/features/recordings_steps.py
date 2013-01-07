# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from lettuce import step
from rest_campaign import RestCampaign
from time import strftime, localtime
from xivo_recording.dao.record_campaign_dao import RecordCampaignDbBinder
from xivo_recording.recording_config import RecordingConfig
import random
from xivo_recording import rest

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################

rest_campaign = RestCampaign()
caller = '2222'
callee = '3333'
time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
callid = None
campaign_name = None
queue_name = "test_queue" + str(random.randint(10, 99))

@step(u'Given there is a campaign named "([^"]*)"')
def given_there_is_a_campaign_named_campaing_name(step, local_campaign_name):
    global campaign_name
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    assert rest_campaign.create(campaign_name), "Cannot create a campaign"


@step(u'When I save call details for a call referenced by its "([^"]*)" in campaign "([^"]*)"')
def when_i_save_call_details_for_a_call_referenced_by_its_group1_in_campaign_group2(step, local_callid, local_campaign_name):
    global callid, campaign_name
    callid = local_callid + str(random.randint(1000, 9999))
    assert callid, "Callid null!"
    record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    campaign_id = record_db.id_from_name(campaign_name)
    assert rest_campaign.addRecordingDetails(campaign_id, callid, caller, callee, time, queue_name), "Cannot add call details"


@step(u'Then I can consult these details')
def then_i_can_consult_these_details(step):
    global campaign_name, callid
    record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    campaign_id = record_db.id_from_name(campaign_name)
    assert rest_campaign.verifyRecordingsDetails(campaign_id, callid), "Recording not found"

@step(u'Given there is a campaign of id "([^"]*)"')
def given_there_is_a_campaign_of_id(step, campaign_id):
    rest_campaign = RestCampaign()
    assert rest_campaign.create_if_not_exists(campaign_id), 'The campaign could not be created'

@step(u'Given I create a recording for campaign "([^"]*)" with caller "([^"]*)" and agent "([^"]*)"')
def given_i_create_a_recording_for_campaign_group1_with_caller_group2_and_agent_group3(step, campaign_id, caller, agent):
    rest_campaign = RestCampaign()
    #rest_campaign.addRecordingDetails(campaign_id, callid, caller, callee, time, queue_name)
    assert False, 'This step must be implemented'
@step(u'When I search recordings in the campaign "([^"]*)" with the key "([^"]*)"')
def when_i_search_recordings_in_the_campaign_group1_with_the_key_group2(step, group1, group2):
    assert False, 'This step must be implemented'
@step(u'Then I get the first two recordings')
def then_i_get_the_first_two_recordings(step):
    assert False, 'This step must be implemented'

