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
import re
def main():
    module = AnsibleModule(
        argument_spec       = dict(
            name            = dict(required=True),
            state           = dict(default='present', choices=['present', 'absent']),
            rules           = dict(type='str'),
            token           = dict(type='str'),
        ),
    required_if = [("state", "present", ["rules"])],
    supports_check_mode = True
    )

    policy_name =  module.params['name']

    try:
        conn = HashivaultConnection(token=module.params['token'], dry_mode=module.check_mode)
        current_rules = conn.make_request('/v1/sys/policy')[0].get('data', {}).get('policies', {})

        policy_present = policy_name in current_rules

        desired_rules = module.params['rules']

        if policy_present:
            if module.params['state'] == 'present':
                current_rules = conn.make_request('/v1/sys/policy/%s' % policy_name)[0]['rules']

                if not are_rules_equal(current_rules, desired_rules):

                    response = write_policy(policy_name, desired_rules, conn)
                    if response[1] not in [200, 204]:
                        module.fail_json(msg='Error creating policy "%s" with rules "%s": "%s"'
                                % (policy_name, data, response[0]))
                    else:
                        module.exit_json(changed=True)
                else:
                    module.exit_json()
            else:
                conn.make_request('/v1/sys/policy/%s' % policy_name, method='DELETE')
                module.exit_json(changed=True)
        else:
            if module.params['state'] == 'absent':
                module.exit_json()
            else:
                response = write_policy(policy_name, desired_rules, conn)
                if response[1] not in [200, 204]:
                    module.fail_json(msg='Error creating policy "%s" with rules "%s": "%s"'
                            % (policy_name, data, response[0]))
                else:
                    module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=e.message)

def write_policy(policy, rules, connection):
    # We must replace " with a \" before POSTing
    data = '{"rules": "%s"}' % rules.replace('"', '\\"')
    return connection.make_request('/v1/sys/policy/%s' % policy, method='POST', data=data)


def trim_rule(rule):
    """
    Remove spaces before and after curly braces
    Remove spaces before \"
    """
    rule = re.sub(' *{ *', '{', rule)
    rule = re.sub(' *} *', '}', rule)
    rule = re.sub(' *\"', '\"', rule)

    return rule

def are_rules_equal(rule1, rule2):
    rule1 = trim_rule(rule1)
    rule2 = trim_rule(rule2)
    with open('/tmp/test', 'w') as f:
        f.write(rule1)
        f.write('\n')
        f.write(rule2)

    return rule1 == rule2

if __name__ == '__main__':
    main()
