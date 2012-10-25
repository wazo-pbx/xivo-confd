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

import unittest
import random
from dao.record_dao import RecordDao, RecordDbBinder
from xivo_dao.alchemy import dbconnection
from recording_config import RecordingConfig
from dao.tests.table_utils import contains


class TestRecordingDao(unittest.TestCase):
    '''
    Test pre-conditions:
    - an agent with number 2002.
    - a table called recording in Asterisk database :
    
    CREATE TABLE recording
    (
      cid character varying(32) NOT NULL,
      call_direction call_dir_type,
      start_time timestamp without time zone,
      end_time timestamp without time zone,
      caller character varying(32),
      client_id character varying(1024),
      calee character varying(32),
      agent character varying(40),
      CONSTRAINT recording_pkey PRIMARY KEY (cid ),
      CONSTRAINT recording_agent_fkey FOREIGN KEY (agent)
          REFERENCES agentfeatures ("number") MATCH SIMPLE
          ON UPDATE NO ACTION ON DELETE NO ACTION
    )
    WITH (
      OIDS=FALSE
    );
    ALTER TABLE recording
      OWNER TO asterisk;
     
    '''

    def test_recording_db(self):

        cid = str(random.randint(10000, 99999999))
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "+" + str(random.randint(1000, 9999))
        client_id = "satisfied client Žluťoučký kůň"
        callee = str(random.randint(100, 999))
        agent = "2002"
        separator = RecordingConfig.CSV_SEPARATOR

        expected_dir = {"cid": cid,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "client_id": client_id,
                        "callee": callee,
                        "agent": agent
                        }

        expected_object = RecordDao()
        for k, v in expected_dir.items():
            setattr(expected_object, k, v)

        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)

        record_db = RecordDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        record_db.insert_into(expected_dir)
        records = record_db.get_records()

        print("read from database:")
        for record in records:
            print(record.to_string())

        print("saved:")
        print(expected_object.to_string())

        self.assert_(contains(records, lambda record: record.to_string() == expected_object.to_string()), "Write/read from database failed")

