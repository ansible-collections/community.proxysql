===========================================
Community ProxySQL Collection Release Notes
===========================================

.. contents:: Topics


v1.3.0
======

Release Summary
---------------

This is the minor release of the ``community.proxysql`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- proxysql_query_rules - add ``next_query_flagIN`` argument (https://github.com/ansible-collections/community.proxysql/pull/74).
- proxysql_replication_hostgroups - implement ``check_type`` parameter (https://github.com/ansible-collections/community.proxysql/pull/69).

Bugfixes
--------

- proxysql_query_rules - fix backwards compatibility. Proxysql > 2 does not support parameter ``cache_empty_result`` (https://github.com/ansible-collections/community.proxysql/pull/77).
- proxysql_replication_hostgroups - ability to change ``reader_hostgroup`` (https://github.com/ansible-collections/community.proxysql/pull/69).

v1.2.0
======

Release Summary
---------------

This is the minor release of the ``community.proxysql`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- refactor ``perform_checks`` function and move ``login_port`` check to ``module_utils/mysql.py`` (https://github.com/ansible-collections/community.proxysql/pull/63).

New Modules
-----------

- community.proxysql.proxysql_info - Gathers information about proxysql server

v1.1.0
======

Release Summary
---------------

This is the minor release of the ``community.proxysql`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- Refactoring of connector presence checking (https://github.com/ansible-collections/community.proxysql/pull/50).
- Replace MySQL-Python with mysqlclient in the import error message (https://github.com/ansible-collections/community.proxysql/pull/50).
- proxysql_query_rules - added new parameters ``cache_empty_result``, ``multiplex``, ``OK_msg`` (https://github.com/ansible-collections/community.proxysql/issues/24).

New Modules
-----------

- community.proxysql.proxysql_query_rules_fast_routing - Modifies query rules for fast routing policies using the proxysql admin interface

v1.0.0
======

Release Summary
---------------

This is the first proper release of the ``community.proxysql`` collection. This changelog contains all changes to the modules in this collection that were added after the release of Ansible 2.9.0.
