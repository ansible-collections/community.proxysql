#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxysql_pgsql_users
author: "Janos Ruszo (@jruszo)"
short_description: Adds or removes postgresql users from proxysql admin interface
description:
   - The M(community.proxysql.proxysql_pgsql_users) module adds or removes postgresql users using the
     proxysql admin interface.
version_added: '1.8.0'
options:
  username:
    description:
      - Name of the user connecting to the postgresql or ProxySQL instance.
    type: str
    required: true
  password:
    description:
      - Password of the user connecting to the postgresql or ProxySQL instance.
    type: str
  active:
    description:
      - A user with I(active) set to C(False) will be tracked in the database,
        but will be never loaded in the in-memory data structures. If omitted
        the proxysql database default for I(active) is C(True).
    type: bool
  use_ssl:
    description:
      - If I(use_ssl) is set to C(True), connections by this user will be made
        using SSL connections. If omitted the proxysql database default for
        I(use_ssl) is C(False).
    type: bool
  default_hostgroup:
    description:
      - If there is no matching rule for the queries sent by this user, the
        traffic it generates is sent to the specified hostgroup.
        If omitted the proxysql database default for I(default_hostgroup) is 0.
    type: int
  transaction_persistent:
    description:
      -  If this is set for the user with which the PostgreSQL client is connecting
         to ProxySQL (thus a "frontend" user), transactions started within a
         hostgroup will remain within that hostgroup regardless of any other
         rules.
         If omitted the proxysql database default for I(transaction_persistent)
         is C(True).
    type: bool
  fast_forward:
    description:
      - If I(fast_forward) is set to C(True), I(fast_forward) will bypass the
        query processing layer (rewriting, caching) and pass through the query
        directly as is to the backend server. If omitted the proxysql database
        default for I(fast_forward) is C(False).
    type: bool
  backend:
    description:
      -  If I(backend) is set to C(True), this (username, password) pair is
         used for authenticating to the ProxySQL instance.
    default: true
    type: bool
  frontend:
    description:
      - If I(frontend) is set to C(True), this (username, password) pair is
        used for authenticating to the PostgreSQL servers against any hostgroup.
    default: true
    type: bool
  max_connections:
    description:
      - The maximum number of connections ProxySQL will open to the backend for
        this user. If omitted the proxysql database default for
        I(max_connections) is 10000.
    type: int
  state:
    description:
      - When C(present) - adds the user, when C(absent) - removes the user.
    type: str
    choices: [ "present", "absent" ]
    default: present
extends_documentation_fragment:
- community.proxysql.proxysql.managing_config
- community.proxysql.proxysql.connectivity
attributes:
  check_mode:
    description: Do not make any changes to memory, disk, or runtime.
    support: full
'''

EXAMPLES = '''
---
# This example adds a user, it saves the postgresql user config to disk, but
# avoids loading the postgresql user config to runtime (this might be because
# several users are being added and the user wants to push the config to
# runtime in a single batch using the community.general.proxysql_manage_config
# module).  It uses supplied credentials to connect to the proxysql admin
# interface.

- name: Add a user
  community.proxysql.proxysql_pgsql_users:
    login_user: 'admin'
    login_password: 'admin'
    username: 'productiondba'
    state: present
    load_to_runtime: false

# This example removes a user, saves the postgresql user config to disk, and
# dynamically loads the postgresql user config to runtime.  It uses credentials
# in a supplied config file to connect to the proxysql admin interface.

- name: Remove a user
  community.proxysql.proxysql_pgsql_users:
    config_file: '~/proxysql.cnf'
    username: 'postgresboy'
    state: absent
'''

RETURN = '''
stdout:
    description: The postgresql user modified or removed from proxysql.
    returned: On create/update will return the newly modified user, on delete
              it will return the deleted record.
    type: dict
    sample:
        changed: true
        msg: Added user to pgsql_users
        state: present
        user:
            active: 1
            backend: 1
            default_hostgroup: 1
            fast_forward: 0
            frontend: 1
            max_connections: 10000
            password: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER
            transaction_persistent: 0
            use_ssl: 0
            username: guest_ro
        username: guest_ro
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.proxysql.plugins.module_utils.mysql import (
    mysql_connect,
    mysql_driver,
    proxysql_common_argument_spec,
    save_config_to_disk,
    load_config_to_runtime
)
from ansible.module_utils._text import to_native

# ===========================================
# proxysql module specific support methods.
#


class ProxySQLPgSQLUser(object):

    def __init__(self, module):
        self.state = module.params["state"]
        self.save_to_disk = module.params["save_to_disk"]
        self.load_to_runtime = module.params["load_to_runtime"]

        self.username = module.params["username"]
        self.backend = module.params["backend"]
        self.frontend = module.params["frontend"]

        config_data_keys = ["password",
                            "active",
                            "use_ssl",
                            "default_hostgroup",
                            "transaction_persistent",
                            "fast_forward",
                            "max_connections"
                            ]

        self.config_data = dict((k, module.params[k])
                                for k in config_data_keys)

    def check_user_config_exists(self, cursor):
        query_string = ("SELECT count(*) AS `user_count`"
               " FROM pgsql_users"
               " WHERE username = %s"
               "   AND backend = %s"
               "   AND frontend = %s")

        query_data = \
            [self.username,
             self.backend,
             self.frontend]

        cursor.execute(query_string, query_data)
        check_count = cursor.fetchone()
        return (int(check_count['user_count']) > 0)

    def check_user_privs(self, cursor):
        query_string = ("SELECT count(*) AS `user_count`"
               " FROM pgsql_users"
               " WHERE username = %s"
               "   AND backend = %s"
               "   AND frontend = %s")

        query_data = \
            [self.username,
             self.backend,
             self.frontend]

        for col, val in self.config_data.items():
            if val is not None:
                query_data.append(val)
                query_string += "\n  AND " + col + " = %s"

        cursor.execute(query_string, query_data)
        check_count = cursor.fetchone()
        return (int(check_count['user_count']) > 0)

    def get_user_config(self, cursor):
        query_string = ("SELECT *"
               " FROM pgsql_users"
               " WHERE username = %s"
               "   AND backend = %s"
               "   AND frontend = %s")

        query_data = \
            [self.username,
             self.backend,
             self.frontend]

        cursor.execute(query_string, query_data)
        user = cursor.fetchone()
        return user

    def create_user_config(self, cursor):
        query_string = ("INSERT INTO pgsql_users ("
               "username,"
               " backend,"
               " frontend")

        cols = 3
        query_data = \
            [self.username,
             self.backend,
             self.frontend]

        for col, val in self.config_data.items():
            if val is not None:
                cols += 1
                query_data.append(val)
                query_string += ",\n" + col

        query_string += \
            (")\n" +
             "VALUES (" +
             "%s ," * cols)

        query_string = query_string[:-2]
        query_string += ")"

        cursor.execute(query_string, query_data)
        return True

    def update_user_config(self, cursor):
        query_string = ("UPDATE pgsql_users")

        cols = 0
        query_data = []

        for col, val in self.config_data.items():
            if val is not None:
                cols += 1
                query_data.append(val)
                if cols == 1:
                    query_string += "\nSET " + col + "= %s,"
                else:
                    query_string += "\n    " + col + " = %s,"

        query_string = query_string[:-1]
        query_string += ("\nWHERE username = %s\n  AND backend = %s" +
                         "\n  AND frontend = %s")

        query_data.append(self.username)
        query_data.append(self.backend)
        query_data.append(self.frontend)

        cursor.execute(query_string, query_data)
        return True

    def delete_user_config(self, cursor):
        query_string = ("DELETE FROM pgsql_users"
               " WHERE username = %s"
               "   AND backend = %s"
               "   AND frontend = %s")

        query_data = \
            [self.username,
             self.backend,
             self.frontend]

        cursor.execute(query_string, query_data)
        return True

    def manage_config(self, cursor, state):
        if state:
            if self.save_to_disk:
                save_config_to_disk(cursor, "USERS", "pgsql")
            if self.load_to_runtime:
                load_config_to_runtime(cursor, "USERS", "pgsql")

    def create_user(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = \
                self.create_user_config(cursor)
            result['msg'] = "Added user to pgsql_users"
            result['user'] = \
                self.get_user_config(cursor)
            self.manage_config(cursor,
                               result['changed'])
        else:
            result['changed'] = True
            result['msg'] = ("User would have been added to" +
                             " pgsql_users, however check_mode" +
                             " is enabled.")

    def update_user(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = \
                self.update_user_config(cursor)
            result['msg'] = "Updated user in pgsql_users"
            result['user'] = \
                self.get_user_config(cursor)
            self.manage_config(cursor,
                               result['changed'])
        else:
            result['changed'] = True
            result['msg'] = ("User would have been updated in" +
                             " pgsql_users, however check_mode" +
                             " is enabled.")

    def delete_user(self, check_mode, result, cursor):
        if not check_mode:
            result['user'] = \
                self.get_user_config(cursor)
            result['changed'] = \
                self.delete_user_config(cursor)
            result['msg'] = "Deleted user from pgsql_users"
            self.manage_config(cursor,
                               result['changed'])
        else:
            result['changed'] = True
            result['msg'] = ("User would have been deleted from" +
                             " pgsql_users, however check_mode is" +
                             " enabled.")

# ===========================================
# Module execution.
#


def main():
    argument_spec = proxysql_common_argument_spec()
    argument_spec.update(
        username=dict(required=True, type='str'),
        password=dict(no_log=True, type='str'),
        active=dict(type='bool'),
        use_ssl=dict(type='bool'),
        default_hostgroup=dict(type='int'),
        transaction_persistent=dict(type='bool'),
        fast_forward=dict(type='bool'),
        backend=dict(default=True, type='bool'),
        frontend=dict(default=True, type='bool'),
        max_connections=dict(type='int'),
        state=dict(default='present', choices=['present',
                                               'absent']),
        save_to_disk=dict(default=True, type='bool'),
        load_to_runtime=dict(default=True, type='bool')
    )

    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=argument_spec
    )

    login_user = module.params["login_user"]
    login_password = module.params["login_password"]
    config_file = module.params["config_file"]

    cursor = None
    try:
        cursor, db_conn, version = mysql_connect(module,
                                                 login_user,
                                                 login_password,
                                                 config_file,
                                                 cursor_class='DictCursor')
    except mysql_driver.Error as e:
        module.fail_json(
            msg="unable to connect to ProxySQL Admin Module.. %s" % to_native(e)
        )

    proxysql_user = ProxySQLPgSQLUser(module)
    result = {}

    result['state'] = proxysql_user.state
    if proxysql_user.username:
        result['username'] = proxysql_user.username

    if proxysql_user.state == "present":
        try:
            if not proxysql_user.check_user_privs(cursor):
                if not proxysql_user.check_user_config_exists(cursor):
                    proxysql_user.create_user(module.check_mode,
                                              result,
                                              cursor)
                else:
                    proxysql_user.update_user(module.check_mode,
                                              result,
                                              cursor)
            else:
                result['changed'] = False
                result['msg'] = ("The user already exists in pgsql_users" +
                                 " and doesn't need to be updated.")
                result['user'] = \
                    proxysql_user.get_user_config(cursor)
        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to modify user.. %s" % to_native(e)
            )

    elif proxysql_user.state == "absent":
        try:
            if proxysql_user.check_user_config_exists(cursor):
                proxysql_user.delete_user(module.check_mode,
                                          result,
                                          cursor)
            else:
                result['changed'] = False
                result['msg'] = ("The user is already absent from the" +
                                 " pgsql_users memory configuration")
        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to remove user.. %s" % to_native(e)
            )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
