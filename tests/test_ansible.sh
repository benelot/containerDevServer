#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── Ansible ──────────────────────────────────────"

if ! has_cmd ansible-playbook; then
    skip "Ansible syntax check" "ansible-playbook not installed"
    summary "Ansible"; exit 0
fi

if ansible-playbook --syntax-check \
        -i "${REPO_ROOT}/ansible/inventory/hosts.yml" \
        "${REPO_ROOT}/ansible/playbook.yml" &>/dev/null; then
    pass "playbook syntax check"
else
    fail "playbook syntax check"
    ansible-playbook --syntax-check \
        -i "${REPO_ROOT}/ansible/inventory/hosts.yml" \
        "${REPO_ROOT}/ansible/playbook.yml" 2>&1 | sed 's/^/    /'
fi

if has_cmd ansible-lint; then
    if ansible-lint "${REPO_ROOT}/ansible/playbook.yml" &>/dev/null; then
        pass "ansible-lint"
    else
        fail "ansible-lint"
    fi
else
    skip "ansible-lint" "not installed"
fi

summary "Ansible"
