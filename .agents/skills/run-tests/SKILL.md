---
name: run-tests
description: Runs and writes tests (sanity, integration) for the community.proxysql Ansible collection using ansible-test. Use when asked to run, check, or write tests for a module or utility. Do not use for PR reviews or questions unrelated to testing.
---

# Skill: run-tests

## Purpose

Run and write tests for the `community.proxysql` Ansible collection. Covers sanity and integration tests using `ansible-test`.

## When to Invoke

TRIGGER when:
- A user asks to run tests, check tests, or verify changes with tests
- A user asks how to test a module or utility
- A user asks to write tests for new or modified code

DO NOT TRIGGER when:
- Reviewing a PR for overall quality (use `.agents/skills/pr-review/SKILL.md` instead)
- The question is about module logic unrelated to testing

## Test Infrastructure

All tests run inside Docker/Podman via `ansible-test --docker`. No local package installation is needed. The collection must be installed at `ansible_collections/community/proxysql/` (relative to a directory on `ANSIBLE_COLLECTIONS_PATHS`) for imports to resolve correctly.

---

## Test Commands

### Sanity

Checks style, documentation, and imports for a changed file:

```bash
ansible-test sanity plugins/modules/proxysql_backend_servers.py --docker -vvv
```

### Integration

Runs integration tests against a live ProxySQL instance (started by Docker):

```bash
ansible-test integration test_proxysql_backend_servers --docker default -vvv
ansible-test integration test_proxysql_mysql_users --docker default -vvv
```

Integration tests live under `tests/integration/targets/<module_name>/`. Each target declares either `setup_proxysql` or `setup_proxysql_v3` as a dependency in `tests/integration/targets/<name>/meta/main.yml` — this target installs Python dependencies and configures the ProxySQL test environment.

---

## When Tests Are Required

| Change type | Sanity | Integration |
|---|---|---|
| New module | yes | yes |
| New parameter | yes | yes |
| Bug fix | yes | yes |
| Refactoring | yes | no |
| Documentation only | yes | no |

---

## Integration Test Pattern

Every integration test target must follow this sequence:

1. Call the module under test → `register: result`
2. Assert on `result` using `ansible.builtin.assert`
3. Verify the resulting ProxySQL state by querying the admin interface via `shell: mysql -uadmin -padmin -h127.0.0.1 -P6032 -BNe"<SQL>"` → `register: result` → `ansible.builtin.assert`

```yaml
- name: Add backend server
  community.proxysql.proxysql_backend_servers:
    login_user: admin
    login_password: admin
    hostname: backend1
    state: present
  register: result

- name: Assert changed
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify server exists in ProxySQL
  shell: mysql -uadmin -padmin -h127.0.0.1 -P6032 -BNe"SELECT hostname FROM mysql_servers WHERE hostname = 'backend1'"
  register: result

- name: Assert server is present
  ansible.builtin.assert:
    that:
      - "'backend1' in result.stdout"
```

Tests must also cover:
- **Idempotency**: run the same task a second time and assert `result is not changed`.
- **`state: absent`**: where applicable, remove the resource and assert it is gone.
