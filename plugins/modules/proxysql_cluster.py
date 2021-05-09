#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxysql_cluster
author: "Akim Lindberg (@akimrx)"
short_description: Adds or removes proxysql cluster hosts using the B(ProxySQL) admin interface.
description:
   - The M(community.proxysql.proxysql_cluster) module adds or removes
     ProxySQL cluster hosts using the B(ProxySQL) admin interface.
options:
  hostname:
    description:
      - The IP address or FQDN at which the proxysql cluster host can be contacted.
    type: str
    required: True
  port:
    description:
      - The port at which the proxysql cluster host can be contacted.
    type: int
    default: 6032
  weight:
    description:
      - The bigger the weight of a server relative to other weights, the higher
        the probability of the server being chosen from the B(ProxySQL) cluster. If
        omitted the B(ProxySQL) server default for I(weight) is 0.
    type: int
    default: 0
  comment:
    description:
      - Text field that can be used for any purposed defined by the user.
        Could be a description of what the host stores, a reminder of when the
        host was added or disabled, or a JSON processed by some checker script.
    type: str
    default: ''
  state:
    description:
      - When C(present) - adds the host, when C(absent) - removes the host.
    type: str
    choices: [ "present", "absent" ]
    default: present
notes:
- Supports C(check_mode).
extends_documentation_fragment:
- community.proxysql.proxysql.managing_config
- community.proxysql.proxysql.connectivity

'''

EXAMPLES = '''
---
# This example adds a server, it saves the proxysql server config to disk, but
# avoids loading the proxysql server config to runtime (this might be because
# several servers are being added and the user wants to push the config to
# runtime in a single batch using the community.general.proxysql_manage_config
# module).  It uses supplied credentials to connect to the proxysql admin
# interface.

- name: Add a server
  community.proxysql.proxysql_cluster:
    login_user: 'admin'
    login_password: 'admin'
    hostname: '{{ item.hostname }}'
    port: {{ item.port | int }}
    weight: {{ item.weight }}
    state: {{ item.state }}
    comment: {{ item.comment }}
    save_to_disk: True
    load_to_runtime: False
  with_items:
    - hostname: 'proxysql-01'
      port: 6032
      weight: 1
      comment: 'Main ProxySQL server'
      state: present
    - hostname: 'proxysql-02'
      port: 6032
      weight: 0
      comment: 'Backup ProxySQL server'
      state: present

# This example removes a server, saves the proxysql server config to disk, and
# dynamically loads the proxysql server config to runtime.  It uses credentials
# in a supplied config file to connect to the proxysql admin interface.

- name: Remove a server
  community.proxysql.proxysql_cluster:
    config_file: '~/proxysql.cnf'
    hostname: 'proxysql-01'
    save_to_disk: True
    state: absent
'''

RETURN = '''
stdout:
    description: The proxysql host modified or removed from ProxySQL cluster
    returned: On create/update will return the newly modified host, on delete
              it will return the deleted record.
    type: dict
    "sample": {
        "changed": true,
        "hostname": "10.10.10.2",
        "msg": "Added server to proxysql cluster",
        "server": {
            "hostname": "10.10.10.2",
            "port": "6032",
            "weight": "1"
            "comment": "",
        },
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

    if module.params["port"] < 0 \
       or module.params["port"] > 65535:
        module.fail_json(
            msg="port must be a valid unix port number (0-65535)"
        )

    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)


def save_config_to_disk(cursor):
    cursor.execute("SAVE PROXYSQL SERVERS TO DISK")
    return True


def load_config_to_runtime(cursor):
    cursor.execute("LOAD PROXYSQL SERVERS TO RUNTIME")
    return True


class ProxySQLServer(object):

    def __init__(self, module):
        self.state = module.params["state"]
        self.save_to_disk = module.params["save_to_disk"]
        self.load_to_runtime = module.params["load_to_runtime"]

        self.hostname = module.params["hostname"]
        self.port = module.params["port"]

        config_data_keys = [
            "weight",
            "comment"
        ]

        self.config_data = dict(
            (k, module.params[k])
            for k in config_data_keys
        )

    def check_server_config_exists(self, cursor):
        query_string = (
            "SELECT count(*) AS `host_count` "
            "FROM proxysql_servers "
            "WHERE hostname = %s "
            "AND port = %s"
        )

        query_data = [
            self.hostname,
            self.port
        ]

        cursor.execute(query_string, query_data)
        check_count = cursor.fetchone()
        return (int(check_count['host_count']) > 0)

    def check_server_config(self, cursor):
        query_string = (
            "SELECT count(*) AS `host_count` "
            "FROM proxysql_servers "
            "WHERE hostname = %s "
            "AND port = %s"
        )

        query_data = [
            self.hostname,
            self.port
        ]

        for col, val in iteritems(self.config_data):
            if val is not None:
                query_data.append(val)
                query_string += " AND " + col + " = %s"

        cursor.execute(query_string, query_data)
        check_count = cursor.fetchone()

        if isinstance(check_count, tuple):
            return int(check_count[0]) > 0

        return (int(check_count['host_count']) > 0)

    def get_server_config(self, cursor):
        query_string = (
            "SELECT * "
            "FROM proxysql_servers "
            "WHERE hostname = %s "
            "AND port = %s"
        )

        query_data = [
            self.hostname,
            self.port
        ]

        cursor.execute(query_string, query_data)
        server = cursor.fetchone()
        return server

    def create_server_config(self, cursor):
        query_string = "INSERT INTO proxysql_servers (hostname, port"

        cols = 2
        query_data = [
            self.hostname,
            self.port
        ]

        for col, val in iteritems(self.config_data):
            if val is not None:
                cols += 1
                query_data.append(val)
                query_string += ", " + col

        query_string += (
            ") VALUES (" +
            "%s ," * cols
        )

        query_string = query_string[:-2]
        query_string += ")"

        cursor.execute(query_string, query_data)
        return True

    def update_server_config(self, cursor):
        query_string = "UPDATE proxysql_servers"

        cols = 0
        query_data = []

        for col, val in iteritems(self.config_data):
            if val is not None:
                cols += 1
                query_data.append(val)
                if cols == 1:
                    query_string += " SET " + col + "= %s,"
                else:
                    query_string += " " + col + " = %s,"

        query_string = query_string[:-1]
        query_string += ("WHERE hostname = %s AND port = %s")

        query_data.append(self.hostname)
        query_data.append(self.port)

        cursor.execute(query_string, query_data)
        return True

    def delete_server_config(self, cursor):
        query_string = (
            "DELETE FROM proxysql_servers "
            "WHERE hostname = %s "
            "AND port = %s"
        )

        query_data = [
            self.hostname,
            self.port
        ]

        cursor.execute(query_string, query_data)
        return True

    def manage_config(self, cursor, state):
        if state:
            if self.save_to_disk:
                save_config_to_disk(cursor)
            if self.load_to_runtime:
                load_config_to_runtime(cursor)

    def create_server(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = self.create_server_config(cursor)
            result['msg'] = "Added server to proxysql cluster"
            result['server'] = self.get_server_config(cursor)
            self.manage_config(cursor, result['changed'])
        else:
            result['changed'] = True
            result['msg'] = (
                "Server would have been added to "
                "proxysql cluster, however check_mode "
                "is enabled."
            )

    def update_server(self, check_mode, result, cursor):
        if not check_mode:
            result['changed'] = self.update_server_config(cursor)
            result['msg'] = "Updated server in proxysql cluster"
            result['server'] = self.get_server_config(cursor)
            self.manage_config(cursor, result['changed'])
        else:
            result['changed'] = True
            result['msg'] = (
                "Server would have been updated in "
                "proxysql cluster, however check_mode "
                "is enabled."
            )

    def delete_server(self, check_mode, result, cursor):
        if not check_mode:
            result['server'] = self.get_server_config(cursor)
            result['changed'] = self.delete_server_config(cursor)
            result['msg'] = "Deleted server from proxysql cluster"
            self.manage_config(cursor, result['changed'])
        else:
            result['changed'] = True
            result['msg'] = (
                "Server would have been deleted from "
                "proxysql cluster, however check_mode "
                "is enabled."
            )

# ===========================================
# Module execution.
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            login_user=dict(default=None, type='str'),
            login_password=dict(default=None, no_log=True, type='str'),
            login_host=dict(default='127.0.0.1'),
            login_unix_socket=dict(default=None),
            login_port=dict(default=6032, type='int'),
            config_file=dict(default='', type='path'),
            hostname=dict(required=True, type='str'),
            port=dict(default=6032, type='int'),
            weight=dict(default=0, type='int'),
            comment=dict(default='', type='str'),
            state=dict(default='present', choices=['present',
                                                   'absent']),
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
        cursor, db_conn = mysql_connect(
            module,
            login_user,
            login_password,
            config_file,
            cursor_class='DictCursor'
        )
    except mysql_driver.Error as e:
        module.fail_json(
            msg="unable to connect to ProxySQL Admin Module.. %s" % to_native(e)
        )

    proxysql_server = ProxySQLServer(module)
    result = {}

    result['state'] = proxysql_server.state
    if proxysql_server.hostname:
        result['hostname'] = proxysql_server.hostname

    if proxysql_server.state == "present":
        try:
            if not proxysql_server.check_server_config(cursor):
                if not proxysql_server.check_server_config_exists(cursor):
                    proxysql_server.create_server(
                        module.check_mode,
                        result,
                        cursor
                    )
                else:
                    proxysql_server.update_server(
                        module.check_mode,
                        result,
                        cursor
                    )
            else:
                result['changed'] = False
                result['msg'] = (
                    "The server already exists in proxysql cluster "
                    "and doesn't need to be updated."
                )
                result['server'] = proxysql_server.get_server_config(cursor)
        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to modify server.. %s" % to_native(e)
            )

    elif proxysql_server.state == "absent":
        try:
            if proxysql_server.check_server_config_exists(cursor):
                proxysql_server.delete_server(
                    module.check_mode,
                    result,
                    cursor
                )
            else:
                result['changed'] = False
                result['msg'] = (
                    "The server is already absent from the "
                    "proxysql cluster memory configuration"
                )
        except mysql_driver.Error as e:
            module.fail_json(
                msg="unable to remove server.. %s" % to_native(e)
            )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
