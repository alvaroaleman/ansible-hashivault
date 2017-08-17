##################################################################################################
## GENERATED
## All the content here is generated from hashivault_common.py

import requests
import os

from ansible.module_utils.basic import AnsibleModule


ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']

class NoVaultURLException(Exception):
    pass

class HashivaultConnection(object):
    def __init__(self, token, vault_url=None, dry_mode=False):
        if not vault_url:
            vault_url = ANSIBLE_HASHI_VAULT_ADDR
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
