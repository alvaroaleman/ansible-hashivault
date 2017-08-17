def main():
    module = AnsibleModule(
        argument_spec       = dict(
            name            = dict(required=True),
            state           = dict(default='present', choices=['present', 'absent']),
            content         = dict(type='string'),
            token           = dict(type='string'),
        ),
    required_if = [ ("state", "present", ["content"])],
    supports_check_mode = True
    )

    try:
        conn = HashivaultConnection(token=module.params['token'], dry_mode=module.check_mode)
    except Exception as e:
        module.fail_json(msg=e.message)
    module.exit_json()


if __name__ == '__main__':
    main()
