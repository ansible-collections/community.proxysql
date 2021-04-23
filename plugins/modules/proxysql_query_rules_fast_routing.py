#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxysql_query_rules_fast_routing
author: "Akim Faskhutdinov (@akimrx)"
short_description: Modifies query rules for fast routing policies using the proxysql admin interface.
description:
   - The M(community.proxysql.proxysql_query_rules_fast_routing) module modifies query rules for fast
     routing policies and attributes using the proxysql admin interface.
options:
  username:
    description:
      - Filtering criteria matching username, a query will match only if the connection is made with
        the correct username.
    type: str
    required: True
  schemaname:
    description:
      - Filtering criteria matching schemaname, a query will match only if the connection uses
        schemaname as its default schema.
    type: str
    required: True
  flagIN:
    description:
      - Evaulated in the same way as I(flagIN) is in I(mysql_query_rules) and correlates to the
        I(flagOUT/apply) specified in the I(mysql_query_rules) table.
        (see M(community.proxysql.proxysql_query_rules)).
    type: int
    default: 0
  destination_hostgroup:
    description:
      - Route matched queries to this hostgroup. This happens unless there is a
        started transaction and the logged in user has
        I(transaction_persistent) set to C(True) (see M(community.proxysql.proxysql_mysql_users)).
    type: int
    required: True
  comment:
    description:
      - Free form text field, usable for a descriptive comment of the query rule.
    type: str
    default: ''
  state:
    description:
      - When C(present) - adds the rule, when C(absent) - removes the rule.
    type: str
    choices: [ "present", "absent" ]
    default: present
  force_delete:
    description:
      - By default we avoid deleting more than one schedule in a single batch,
        however if you need this behaviour and you're not concerned about the
        schedules deleted, you can set I(force_delete) to C(True).
    type: bool
    default: False
extends_documentation_fragment:
- community.proxysql.proxysql.managing_config
- community.proxysql.proxysql.connectivity

'''

EXAMPLES = '''
---
# This example adds a rule for fast routing

- name: Add a rule
  community.proxysql.proxysql_query_rules:
    login_user: admin
    login_password: admin
    username: 'user_ro'
    schemaname: 'default'
    destination_hostgroup: 1
    comment: 'fast route user_ro to default schema'
    state: present
    save_to_disk: yes
    load_to_runtime: yes

'''

RETURN = '''
stdout:
    description: The mysql user modified or removed from proxysql
    returned: On create/update will return the newly modified rule, in all
              other cases will return a list of rules that match the supplied
              criteria.
    type: dict
    "sample": {
        "changed": true,
        "msg": "Added rule to mysql_query_rules_fast_routing",
        "rules": [
            {
                "username": "user_ro",
                "schemaname": "default",
                "destination_hostgroup": 1,
                "flagIN": "0",
                "comment": ""
            }
        ],
        "state": "present"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.proxysql.plugins.module_utils.mysql import mysql_connect, mysql_driver, mysql_driver_fail_msg
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_native

# ===========================================
# proxysql module specific support methods.
#


def perform_checks(module):
    if module.params["login_port"] < 0 \
       or module.params["login_port"] > 65535:
        module.fail_json(
            msg="login_port must be a valid unix port number (0-65535)"
        )

    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)


def save_config_to_disk(cursor):
    cursor.execute("SAVE MYSQL QUERY RULES TO DISK")
    return True


def load_config_to_runtime(cursor):
    cursor.execute("LOAD MYSQL QUERY RULES TO RUNTIME")
    return True


class ProxyQueryRuleFastRouting(object):

    def __init__(self, module):
        self.state = module.params["state"]
        self.force_delete = module.params["force_delete"]
        self.save_to_disk = module.params["save_to_disk"]
        self.load_to_runtime = module.params["load_to_runtime"]

        config_data_keys = ["username",
                            "schemaname",
                            "flagIN",
                            "destination_hostgroup",
                            "comment"]

        self.config_data = dict((k, module.params[k])
                                for k in config_data_keys)

    def check_rule_pk_exists(self, cursor):
        query_string = \
            """SELECT count(*) AS `rule_count`
               FROM mysql_query_rules_fast_routing
               WHERE username = %s
               AND schemaname = %s
               AND flagIN = %s"""

        query_data = \
            [self.config_data["username"],
             self.config_data["schemaname"],
             self.config_data["flagIN"]]

        cursor.execute(query_string, query_data)
        check_count = cursor.fetchone()
        return (int(check_count['rule_count']) > 0)

    def check_rule_cfg_exists(self, cursor):
        query_string = \
            """SELECT count(*) AS `rule_count`
               FROM mysql_query_rules_fast_routing"""

        cols = 0
        query_data = []

        for col, val in iteritems(self.config_data):
            if val is not None:
                cols += 1
                query_data.append(val)
                if cols == 1:
                    query_string += "\n WHERE " + col + " = %s"
                else:
                    query_string += "\n  AND " + col + " = %s"

        if cols > 0:
            cursor.execute(query_string, query_data)
        else:
            cursor.execute(query_string)
        check_count = cursor.fetchone()
        return int(check_count['rule_count'])

    def get_rule_config(self, cursor):
        query_string = \
            """SELECT *
               FROM mysql_query_rules_fast_routing
               WHERE username = %s
                 AND schemaname = %s
                 AND flagIN = %s"""

        query_data = \
            [self.config_data["username"],
             self.config_data["schemaname"],
             self.config_data["flagIN"]]

        for col, val in iteritems(self.config_data):
            if val is not None:
                query_data.append(val)
                query_string += "\n  AND " + col + " = %s"

        cursor.execute(query_string, query_data)
        rule = cursor.fetchall()
        return rule

    def create_rule_config(self, cursor):
        query_string = \
            """INSERT INTO mysql_query_rules_fast_routing ("""

        cols = 0
        query_data = []

        for col, val in iteritems(self.config_data):
            if val is not None:
                cols += 1
                query_data.append(val)
                query_string += "\n" + col + ","

        query_string = query_string[:-1]

        query_string += \
            (")\n" +
             "VALUES (" +
             "%s ," * cols)

        query_string = query_string[:-2]
        query_string += ")"

        cursor.execute(query_string, query_data)
        return True

    def update_rule_config(self, cursor):
        query_string = """UPDATE mysql_query_rules_fast_routing"""

        cols = 0
        query_data = \
            [self.config_data["username"],
             self.config_data["schemaname"],
             self.config_data["flagIN"]]

        for col, val in iteritems(self.config_data):
            if val is not None and col not in ("username", "schemaname", "flagIN"):
                cols += 1
                query_data.append(val)
                if cols == 1:
                    query_string += "\nSET " + col + "= %s,"
                else:
                    query_string += "\n    " + col + " = %s,"

        query_string = query_string[:-1]
        query_string += \
            """WHERE username = %s
                 AND schemaname = %s
                 AND flagIN = %s"""

        cursor.execute(query_string, query_data)
        return True

    def delete_rule_config(self, cursor):
        query_string = \
            """DELETE FROM mysql_query_rules_fast_routing"""

        cols = 0
        query_data = []

        for col, val in iteritems(self.config_data):
            if val is not None:
                cols += 1
                query_data.append(val)
                if cols == 1:
                    query_string += "\n WHERE " + col + " = %s"
                else:
                    query_string += "\n  AND " + col + " = %s"

        if cols > 0:
            cursor.execute(query_string, query_data)
        else:
            cursor.execute(query_string)
        check_count = cursor.rowcount
        return True, int(check_count)

    def manage_config(self, cursor, state):
        if state:
            if self.save_to_disk:
                save_config_to_disk(cursor)
            if self.load_to_runtime:
                load_config_to_runtime(cursor)

    def create_rule(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = self.create_rule_config(cursor)
            result['msg'] = "Added rule to mysql_query_rules_fast_routing"
            self.manage_config(cursor,
                               result['changed'])
            result['rules'] = self.get_rule_config(cursor)
        else:
            result['changed'] = True
            result['msg'] = ("Rule would have been added to" +
                             " mysql_query_rules_fast_routing," +
                             " however check_mode is enabled.")

    def update_rule(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = \
                self.update_rule_config(cursor)
            result['msg'] = "Updated rule in mysql_query_rules_fast_routing"
            self.manage_config(cursor,
                               result['changed'])
            result['rules'] = \
                self.get_rule_config(cursor)
        else:
            result['changed'] = True
            result['msg'] = ("Rule would have been updated in" +
                             " mysql_query_rules_fast_routing," +
                             " however check_mode is enabled.")

    def delete_rule(self, check_mode, result, cursor):
        if not check_mode:
            result['rules'] = \
                self.get_rule_config(cursor)
            result['changed'], result['rows_affected'] = \
                self.delete_rule_config(cursor)
            result['msg'] = "Deleted rule from mysql_query_rules_fast_routing"
            self.manage_config(cursor,
                               result['changed'])
        else:
            result['changed'] = True
            result['msg'] = ("Rule would have been deleted from" +
                             " mysql_query_rules_fast_routing," +
                             " however check_mode is enabled.")

# ===========================================
# Module execution.
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            login_user=dict(default=None, type='str'),
            login_password=dict(default=None, no_log=True, type='str'),
            login_host=dict(default="127.0.0.1"),
            login_unix_socket=dict(default=None),
            login_port=dict(default=6032, type='int'),
            config_file=dict(default="", type='path'),
            username=dict(required=True, type='str'),
            schemaname=dict(required=True, type='str'),
            destination_hostgroup=dict(required=True, type='int'),
            flagIN=dict(default=0, type='int'),
            comment=dict(default='', type='str'),
            state=dict(default='present', choices=['present',
                                                   'absent']),
            force_delete=dict(default=False, type='bool'),
            save_to_disk=dict(default=True, type='bool'),
            load_to_runtime=dict(default=True, type='bool')
        ),
        supports_check_mode=True
    )

    perform_checks(module)

    login_user = module.params["login_user"]
    login_password = module.params["login_password"]
    config_file = module.params["config_file"]

    cursor = None
    try:
        cursor, db_conn = mysql_connect(module,
                                        login_user,
                                        login_password,
                                        config_file,
                                        cursor_class='DictCursor')
    except mysql_driver.Error as e:
        module.fail_json(
            msg="unable to connect to ProxySQL Admin Module.. %s" % to_native(e)
        )

    proxysql_query_rule_fast_routing = ProxyQueryRuleFastRouting(module)
    result = {}

    result['state'] = proxysql_query_rule_fast_routing.state

    if proxysql_query_rule_fast_routing.state == "present":
        try:
            if not proxysql_query_rule_fast_routing.check_rule_cfg_exists(cursor):
                if ("username", "schemaname", "flagIN") \
                    in proxysql_query_rule_fast_routing.config_data and \
                    proxysql_query_rule_fast_routing.check_rule_pk_exists(cursor):
                    proxysql_query_rule_fast_routing.update_rule(module.check_mode,
                                                                 result,
                                                                 cursor)
                else:
                    proxysql_query_rule_fast_routing.create_rule(module.check_mode,
                                                                 result,
                                                                 cursor)
            else:
                result['changed'] = False
                result['msg'] = ("The rule already exists in" +
                                 " mysql_query_rules_fast_routing" +
                                 " and doesn't need to be updated.")
                result['rules'] = \
                    proxysql_query_rule_fast_routing.get_rule_config(cursor)

        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to modify rule.. %s" % to_native(e)
            )

    elif proxysql_query_rule_fast_routing.state == "absent":
        try:
            existing_rules = proxysql_query_rule_fast_routing.check_rule_cfg_exists(cursor)
            if existing_rules > 0:
                if existing_rules == 1 or \
                   proxysql_query_rule_fast_routing.force_delete:
                    proxysql_query_rule_fast_routing.delete_rule(module.check_mode,
                                                                 result,
                                                                 cursor)
                else:
                    module.fail_json(
                        msg=("Operation would delete multiple rules" +
                             " use force_delete to override this")
                    )
            else:
                result['changed'] = False
                result['msg'] = ("The rule is already absent from the" +
                                 " mysql_query_rules_fast_routing memory" +
                                 " configuration")
        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to remove rule.. %s" % to_native(e)
            )

    module.exit_json(**result)


if __name__ == '__main__':
    main()