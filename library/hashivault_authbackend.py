#!/usr/bin/env python

import requests
import os

from ansible.module_utils.basic import AnsibleModule


ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']

class HashivaultConnection(object):
    def __init__(self, vault_url, token, dry_mode):
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

def main():
    module = AnsibleModule(
        argument_spec       = dict(
            state           = dict(default='present', choices=['present', 'absent']),
            backend_type    = dict(default='approle', choices=['approle']),
            token           = dict(type='string')
        ),
    supports_check_mode = True
    )

    token = ''
    if os.getenv('VAULT_TOKEN') is not None:
        token = os.environ['VAULT_TOKEN']

    if module.params['token']:
        token = module.params['token']

    if not token:
        module.fail_json(msg='You must submit a vault token via parameter or the VAULT_TOKEN'
                             'environment variable!')

    conn = HashivaultConnection(ANSIBLE_HASHI_VAULT_ADDR, token, module.check_mode)
    enabled_backends = conn.make_request('/v1/sys/auth')[0].get('data', {})

    backend_mounted = '%s/' % module.params['backend_type'] in enabled_backends

    if backend_mounted:
        if module.params['state'] == 'present':
            module.exit_json(changed=False)
        else:
            uri = '/v1/sys/auth/%s' % module.params['backend_type']
            response = conn.make_request(uri, method='DELETE')

            if response[1] not in [200, 204]:
                module.fail_json(msg='Error deleting auth backend "%s": "%s"'
                        % (module.params['backend_type'], response[0]))
            else:
                module.exit_json(changed=True)

    else:
        if module.params['state'] == 'absent':
            module.exit_json(changed=False)
        else:
            data = '{"type": "%s"}' % module.params['backend_type']
            uri = '/v1/sys/auth/%s' % module.params['backend_type']
            response = conn.make_request(uri, method='POST', data=data)
            if response[1] not in [200, 204]:
                module.fail_json(msg='Error creating auth backend "%s": "%s"'
                        % (module.params['backend_type'], response[0]))
            else:
                module.exit_json(changed=True)


if __name__ == '__main__':
    main()
