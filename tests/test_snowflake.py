# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#

from __future__ import absolute_import, division, unicode_literals

from unittest import TestCase

from mo_parsing.debug import Debugger

from mo_sql_parsing import parse


class TestSnowflake(TestCase):
    def test_issue_101_create_temp_table(self):
        sql = """CREATE TEMP TABLE foo(a varchar(10))"""
        result = parse(sql)
        expected = {"create table": {
            "columns": {"name": "a", "type": {"varchar": 10}},
            "name": "foo",
            "temporary": True,
        }}
        self.assertEqual(result, expected)

    def test_issue_101_create_transient_table(self):
        sql = """CREATE TRANSIENT TABLE foo(a varchar(10))"""
        result = parse(sql)
        expected = {"create table": {
            "columns": {"name": "a", "type": {"varchar": 10}},
            "name": "foo",
            "temporary": True,
        }}
        self.assertEqual(result, expected)

    def test_issue_102_table_functions1(self):
        sql = """
        SELECT seq4()
        FROM TABLE(generator(rowcount => 10))
        """
        result = parse(sql)
        expected = {
            "from": {"table": {"generator": {"=>": ["rowcount", 10]}}},
            "select": {"value": {"seq4": {}}},
        }
        self.assertEqual(result, expected)

    def test_issue_102_table_functions2(self):
        sql = """
        SELECT uniform(1, 10, random())
        FROM TABLE(generator(rowcount => 5));
        """
        result = parse(sql)
        expected = {
            "from": {"table": {"generator": {"=>": ["rowcount", 5]}}},
            "select": {"value": {"uniform": [1, 10, {"random": {}}]}},
        }
        self.assertEqual(result, expected)

    def test_issue_102_table_functions3(self):
        sql = """
        SELECT t.index, t.value
        FROM TABLE(split_to_table('a.b.z.d', '.')) as t
        ORDER BY t.value;
        """
        result = parse(sql)
        expected = {
            "from": {
                "name": "t",
                "value": {"table": {"split_to_table": [
                    {"literal": "a.b.z.d"},
                    {"literal": "."},
                ]}},
            },
            "orderby": {"value": "t.value"},
            "select": [{"value": "t.index"}, {"value": "t.value"}],
        }
        self.assertEqual(result, expected)
