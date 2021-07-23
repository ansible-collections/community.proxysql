===========================================
Community ProxySQL Collection Release Notes
===========================================

.. contents:: Topics


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
