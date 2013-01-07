# -*- coding: UTF-8 -*-
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from acceptance.features.rest_queues import RestQueues
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
import datetime
import random


class RestCampaign(object):

    def __init__(self):
        pass

    def create(self, campaign_name, queue_id=1, activated = True, start_date = None, end_date = None):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
                        
        campaign = {}

        campaign["campaign_name"] = campaign_name
        campaign["base_filename"] = campaign_name + "-file-"
        campaign["queue_id"] = queue_id
        campaign["activated"] = activated
        if start_date != None:
            campaign["start_date"] = str(start_date)
        if end_date != None:
            campaign["end_date"] = str(end_date)
        body = rest_encoder.encode(campaign)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        #assert reply.status == 201

        return rest_encoder.decode(reply.read())

    def list(self):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)
        return campaigns

    def get_activated_campaigns(self, queue_id):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        "?activated=true&queue_id=" + str(queue_id)

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)

        return campaigns

    def addRecordingDetails(self, campaign_id, callid, caller, callee, time, queue_name):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        "/" + str(campaign_id) + '/'
        
        recording = {}
        recording['cid'] = callid
        recording['caller'] = caller
        recording['callee'] = callee
        recording['time'] = time
        recording['queue_name'] = queue_name
        body = rest_encoder.encode(recording)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()
        print("\nreply: " + reply.read() + '\n')

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        assert reply.status == 201
        return (reply.status == 201)

    def verifyRecordingsDetails(self, campaign_id, callid):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        '/' + str(campaign_id) + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()
        assert body != None, "No result" 
        recordings = rest_encoder.decode(body)

        result = False
        for recording in recordings:
            if (recording["cid"] == callid):
                result = True

        assert result
        return result

    def update(self, campaign_id, params):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        body = rest_encoder.encode(params)
        connection.request("PUT", requestURI, body, headers)
        reply = connection.getresponse()
        return reply.status == 200 or reply.status == 201
    
    def getCampaign(self, campaign_id):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id)

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())
    def getRunningActivatedCampaignsForQueue(self, queue_id):
        connection = RecordingConfig.getWSConnection()
        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
        parameters = "?activated=true&running=true&queue_id=" + queue_id
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI + parameters, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())
    
    def create_if_not_exists(self, campaign_id):
        result = self.getCampaign(campaign_id)
        if(result == None or len(result) == 0):
            rest_queues = RestQueues()
            rest_queues.create_if_not_exists(1)
            result = self.create("lettuce" + str(random.randint(100, 999)), 1, True, str(datetime.datetime.now()), str(datetime.datetime.now()))
            return type(result) == int and result > 0
        return True