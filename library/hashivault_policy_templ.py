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

    try:
        conn = HashivaultConnection(token=module.params['token'], dry_mode=module.check_mode)
        rules = conn.make_request('/v1/sys/policy')[0].get('data', {}).get('policies', {})

        policy_present = module.params['name'] in rules

        if policy_present:
            if module.params['state'] == 'absent':
                conn.make_request('/v1/sys/policy/%s' % module.params['name'], method='DELETE')
                module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=e.message)

    module.exit_json()


if __name__ == '__main__':
    main()
