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

    conn = HashivaultConnection(token, dry_mode=module.check_mode)
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
