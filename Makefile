.PHONY: hashivault_authbackend-test
hashivault_authbackend-test:
	ansible-playbook test/playbook.yml -t testsetup,hashivault_authbackend
