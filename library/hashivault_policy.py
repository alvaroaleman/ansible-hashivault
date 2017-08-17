##################################################################################################
## GENERATED
## All the content here is generated from hashivault_common.py

import requests
import os

from ansible.module_utils.basic import AnsibleModule


ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'
ANSIBLE_HASHI_VAULT_TOKEN = os.environ.get('VAULT_TOKEN')

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']


class NoVaultURLException(Exception):
    def __init__(self):
        msg = "No vault url available! Declare it via the VAULT_ADDR environment variable."
        super(NoVaultURLException, self).__init__(msg)


class NoVaultTokenExecption(Exception):
    def __init__(self):
        msg = "No vault token available! Declare it via the VAULT_TOKEN environment variable"\
                " or as module parameter"
        super(NoVaultTokenExecption, self).__init__(msg)


class HashivaultConnection(object):
    def __init__(self, token=None, vault_url=None, dry_mode=False):
        if not vault_url:
            vault_url = ANSIBLE_HASHI_VAULT_ADDR
        if not token and not ANSIBLE_HASHI_VAULT_TOKEN:
            raise NoVaultTokenExecption()
        if not token and ANSIBLE_HASHI_VAULT_TOKEN:
            token = ANSIBLE_HASHI_VAULT_TOKEN
        self.vault_url = vault_url
        self.token = token
        self.dry_mode = dry_mode
        self.headers = {'X-VAULT-TOKEN': token}

    def make_request(self, uri, method='GET', data=None):
        if method == 'GET':
            response = requests.get('%s%s' % (self.vault_url, uri), headers=self.headers)
            return (response.json(), response.status_code)
        if method == 'POST':
            if self.dry_mode:
                return ({}, 200)
            else:
                response = requests.post('%s%s' % (self.vault_url, uri),
                        headers=self.headers, data=data)
                if response.status_code == 204:
                    content = ''
                else:
                    content = response.json()
                return (content, response.status_code)
        if method == 'DELETE':
            if self.dry_mode:
                return ({}, 200)
            else:
                response = requests.delete('%s%s' % (self.vault_url, uri),
                        headers=self.headers, data=data)
                if response.status_code == 204:
                    content = ''
                else:
                    content = response.json()
                return (content, response.status_code)
## END GENERATED CONTENT
##################################################################################################
def main():
    module = AnsibleModule(
        argument_spec       = dict(
            name            = dict(required=True),
            state           = dict(default='present', choices=['present', 'absent']),
            rules           = dict(type='list'),
            token           = dict(type='string'),
        ),
    required_if = [("state", "present", ["rules"])],
    supports_check_mode = True
    )

    policy_name =  module.params['name']

    try:
        conn = HashivaultConnection(token=module.params['token'], dry_mode=module.check_mode)
        rules = conn.make_request('/v1/sys/policy')[0].get('data', {}).get('policies', {})

        policy_present = policy_name in rules

        if policy_present:
            if module.params['state'] == 'present':
                rules = conn.make_request('/v1/sys/policy/%s' % policy_name)[0].get('rules', '')
                rules = clean_rule(rules)
                module.exit_json(msg=rules)
            else:
                conn.make_request('/v1/sys/policy/%s' % policy_name, method='DELETE')
                module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=e.message)


def clean_rule(rule):
    """
    Removes spaces after opening curly brackets and
    before closing curly brackets
    """
    elements = rule.split('{')
    elements[1] = elements[1].lstrip()
    rule = '{'.join(elements)
    elements = rule.split('}')
    elements[0] = elements[0].rstrip()
    rule = '}'.join(elements)
    return rule

if __name__ == '__main__':
    main()
