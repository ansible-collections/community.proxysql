# ProxySQL collection for Ansible
[![Plugins CI](https://github.com/ansible-collections/community.proxysql/workflows/Plugins%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.proxysql/actions?query=workflow%3A"Plugins+CI") [![Roles CI](https://github.com/ansible-collections/community.proxysql/workflows/Roles%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.proxysql/actions?query=workflow%3A"Roles+CI") [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.proxysql)](https://codecov.io/gh/ansible-collections/community.proxysql)

This collection is a part of Ansible package.

## Code of Conduct

We follow [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior violating the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html), please refer to the [policy violations](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html#policy-violations) section of the Code of Conduct for information on how to raise a complaint.

## Contributing to this collection

The content of this collection is made by good [people](CONTRIBUTORS) like you, a community of individuals collaborating on making the world better through developing automation software.

All types of contributions are very welcome.

You don't know how to start? Refer to our [contribution guide](CONTRIBUTING.md)!

The current maintainers are listed in the [MAINTAINERS](MAINTAINERS) file. Don't hesitate to reach them out mentioning in the proposals. To learn how to maintain / become a maintainer of this collection, refer to the [Maintainer guidelines](https://github.com/ansible/community-docs/blob/main/maintaining.rst).

## Communication

We announce releases and important changes through the [Ansible Bullhorn newsletter](https://github.com/ansible/community/issues/546). Be sure you are subscribed.

Join us in the ``ansible-community`` [IRC channel](https://docs.ansible.com/ansible/devel/community/communication.html#irc-channels).

We take part in the global quarterly [Ansible Contributor Summit](https://github.com/ansible/community/wiki/Contributor-Summit) virtually or in-person. Track the [Bullhorn newsletter](https://github.com/ansible/community/issues/546) and join us.

For more information about communication, refer to the [Ansible Communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

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

Before using the ProxySQL collection, you need to install it with the Ansible Galaxy command-line tool:

```bash
ansible-galaxy collection install community.proxysql
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.proxysql
```

You can also download the tarball from [Ansible Galaxy](https://galaxy.ansible.com/community/proxysql) and install the collection manually wherever you need.

Note that if you install the collection from Ansible Galaxy with the command-line tool or tarball, it will not be upgraded automatically with upgrade of the Ansible package. To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install community.proxysql --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax:

```bash
ansible-galaxy collection install community.proxysql:==X.Y.Z
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
