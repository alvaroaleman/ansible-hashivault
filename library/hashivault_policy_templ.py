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

                if are_rules_equal(current_rules, desired_rules):
                    module.exit_json(changed=False)
                else:
                    write_policy(policy_name, desired_rules, conn, module)
                    module.exit_json(changed=True)
            else:
                conn.make_request('/v1/sys/policy/%s' % policy_name, method='DELETE')
                module.exit_json(changed=True)
        else:
            if module.params['state'] == 'absent':
                module.exit_json(changed=False)
            else:
                write_policy(policy_name, desired_rules, conn, module)
                module.exit_json(changed=True)

    except Exception as e:
        module.fail_json(msg=e.message)


def write_policy(policy, rules, connection, module):
    # We must replace " with a \" before POSTing
    data = '{"rules": "%s"}' % rules.replace('"', '\\"')
    response = connection.make_request('/v1/sys/policy/%s' % policy, method='POST', data=data)
    if response[1] not in [200, 204]:
        module.fail_json(msg='Error creating policy "%s" with rules "%s": "%s"'
                % (policy, data, response[0]))


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

    return rule1 == rule2


if __name__ == '__main__':
    main()
