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
                rules = trim_rule(rules)
                module.exit_json(msg=rules)
            else:
                conn.make_request('/v1/sys/policy/%s' % policy_name, method='DELETE')
                module.exit_json(changed=True)
    except Exception as e:
        module.fail_json(msg=e.message)


def trim_rule(rule):
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
