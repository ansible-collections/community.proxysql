# ProxySQL collection for Ansible
[![Plugins CI](https://github.com/ansible-collections/community.proxysql/workflows/Plugins%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.proxysql/actions?query=workflow%3A"Plugins+CI") [![Roles CI](https://github.com/ansible-collections/community.proxysql/workflows/Roles%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.proxysql/actions?query=workflow%3A"Roles+CI") [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.proxysql)](https://codecov.io/gh/ansible-collections/community.proxysql)

## Code of Conduct

We follow [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior violating [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html), please let [maintainers](MAINTAINERS) know by mentioning them or creating a dedicated issue.

## Contributing to this collection

The content of this collection are made by good [people](CONTRIBUTORS) like you.

All types of contributions are very welcome.

**[TODO]** Add links to the [CONTRIBUTING.md and Quick-start guide](https://github.com/Andersson007/community-docs/blob/0f2dcd63be40a0b97042f3c78f6073d4c2d28e43/CONTRIBUTING.md) when they finally find home.

## Included content

- **Modules**:
  - [proxysql_backend_servers](https://docs.ansible.com/ansible/latest/modules/proxysql_backend_servers_module.html)
  - [proxysql_global_variables](https://docs.ansible.com/ansible/latest/modules/proxysql_global_variables_module.html)
  - [proxysql_manage_config](https://docs.ansible.com/ansible/latest/modules/proxysql_manage_config_module.html)
  - [proxysql_mysql_users](https://docs.ansible.com/ansible/latest/modules/proxysql_mysql_users_module.html)
  - [proxysql_query_rules](https://docs.ansible.com/ansible/latest/modules/proxysql_query_rules_module.html)
  - [proxysql_replication_hostgroups](https://docs.ansible.com/ansible/latest/modules/proxysql_replication_hostgroups_module.html)
  - [proxysql_scheduler](https://docs.ansible.com/ansible/latest/modules/proxysql_scheduler_module.html)
- **Roles**:
  - proxysql

## Tested with Ansible

- 2.9
- 2.10
- 2.11
- devel

## External requirements

The ProxySQL modules rely on a MySQL connector.  The list of supported drivers is below:

- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [MySQLdb](https://github.com/PyMySQL/mysqlclient-python)
- Support for other Python MySQL connectors may be added in a future release.

## Using this collection

### Installing the Collection from Ansible Galaxy

Before using the ProxySQL collection, you need to install it with the Ansible Galaxy CLI:

```bash
ansible-galaxy collection install community.proxysql
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.proxysql
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
