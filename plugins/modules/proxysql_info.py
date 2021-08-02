#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxysql_info
author: "Markus Bergholz (@markuman)"
short_description: Gathers information about proxysql server
description:
   - Gathers information about proxysql server.
version_added: '1.2.0'
extends_documentation_fragment:
- community.proxysql.proxysql.connectivity
notes:
- Supports C(check_mode).
'''

EXAMPLES = '''
---
# This example adds a rule for fast routing
- name: Add a rule
  community.proxysql.proxysql_info:
    login_user: admin
    login_password: admin
'''

RETURN = '''
stdout:
    description: The mysql user modified or removed from proxysql.
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
from ansible_collections.community.proxysql.plugins.module_utils.mysql import mysql_connect, mysql_driver
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_native

# ===========================================
# proxysql module specific support methods.
#


def perform_checks(module):
    if module.params["login_port"] < 0 or module.params["login_port"] > 65535:
        module.fail_json(msg="login_port must be a valid unix port number (0-65535)")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            login_user=dict(default=None, type='str'),
            login_password=dict(default=None, no_log=True, type='str'),
            login_host=dict(default="127.0.0.1"),
            login_unix_socket=dict(default=None),
            login_port=dict(default=6032, type='int'),
            config_file=dict(default="", type='path')
        ),
        supports_check_mode=True
    )

    perform_checks(module)

    login_user = module.params["login_user"]
    login_password = module.params["login_password"]
    config_file = module.params["config_file"]

    cursor = None
    try:
        cursor, db_conn = mysql_connect(
            module,
            login_user,
            login_password,
            config_file,
            cursor_class='DictCursor'
        )
    except mysql_driver.Error as e:
        module.fail_json(msg="unable to connect to ProxySQL Admin Module: %s" % to_native(e))

    result = dict()
    cursor.execute("select version();")
    version = cursor.fetchone()
    # 2.2.0-72-ge14accd
    _version = version.get('version()').split('-')
    __version = _version[0].split('.')
    result['version'] = dict()
    result['version']['full'] = version.get('version()')
    result['version']['major'] = __version[0]
    result['version']['minor'] = __version[1]
    result['version']['release'] = __version[2]
    result['version']['suffix'] = _version[1]

    tables = list()
    cursor.execute("show tables")
    for table in cursor.fetchall():
        tables.append(table.get('tables'))
    result['tables'] = tables

    for table in result.get('tables'):
        cursor.execute(f"select * from {table}")

        if 'global_variables' in table:
            result[table] = dict()
            for item in cursor.fetchall():
                result[table][item.get('variable_name')] = item.get('variable_value')

        else:
            result[table] = cursor.fetchall()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
