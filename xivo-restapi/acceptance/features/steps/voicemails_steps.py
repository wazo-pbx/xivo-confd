# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from acceptance.features.steps.helpers.rest_voicemail import RestVoicemail
from lettuce import step
from xivo_dao import voicemail_dao

rest_voicemail = RestVoicemail()
result = None


@step(u'Given there is no voicemail')
def given_there_is_no_voicemail(step):
    voicemail_dao.delete_all()


@step(u'Given there is a voicemail with fullname "([^"]*)" and with number "([^"]*)"')
def given_there_is_a_voicemail_with_fullname_group1_and_with_number_group2(step, fullname, number):
    rest_voicemail.create_voicemail(fullname=fullname, number=number)


@step(u'When I list the voicemails')
def when_i_list_the_voicemails(step):
    global result
    result = rest_voicemail.list()


@step(u'Then I get a response from voicemails webservice with status "([^"]*)"')
def then_i_get_a_response_from_voicemails_webservice_with_status_group1(step, status):
    global result
    assert result.status == int(status)


@step(u'Then I get one voicemail with fullname "([^"]*)" and with number "([^"]*)"')
def then_i_get_one_voicemail_with_fullname_group1_and_with_number_group2(step, fullname, number):
    global result
    assert len(result.data["items"]) == 1
    data = result.data["items"][0]
    assert data["fullname"] == fullname
    assert data["mailbox"] == number


@step(u'When I update the voicemail of number "([^"]*)" with number "([^"]*)" and fullname "([^"]*)"')
def when_i_update_the_voicemail_of_number_group1_with_number_group2_and_fullname_group3(step, oldnumber, newnumber, newfullname):
    global result
    result = rest_voicemail.update_voicemail(oldnumber, newnumber=newnumber, newfullname=newfullname)


@step(u'Then there is a voicemail with number "([^"]*)" and fullname "([^"]*)"')
def then_there_is_a_voicemail_with_number_group1_and_fullname_group2(step, number, fullname):
    local_result = rest_voicemail.list()
    voicemails = local_result.data["items"]
    matching_voicemails = [voicemail for voicemail in voicemails\
                                if voicemail["mailbox"] == number and voicemail["fullname"] == fullname]
    assert len(matching_voicemails) > 0


@step(u'When I update the voicemail of id "([^"]*)"')
def when_i_update_the_voicemail_of_id_group1(step, voicemailid):
    global result
    result = rest_voicemail.update_voicemail_by_id(int(voicemailid), {})


@step(u'When I update the voicemail of number "([^"]*)" with a field "([^"]*)" of value "([^"]*)"')
def when_i_update_the_voicemail_of_number_group1_with_a_field_group2_of_value_group3(step, number, fieldname, fieldvalue):
    global result
    result = rest_voicemail.update_voicemail_field(number, fieldname, fieldvalue)


@step(u'Then I get an error message from voicemails webservice "([^"]*)"')
def then_i_get_an_error_message_from_voicemails_webservice_group1(step, message):
    global result
    assert result.data[0] == message