.PHONY: hashivault_authbackend-test
hashivault_authbackend-test: library/hashivault_authbackend.py
	ansible-playbook test/playbook.yml -t testsetup,hashivault_authbackend -vvvv

.PHONY: library/hashivault_authbackend.py
library/hashivault_authbackend.py:
	@cat library/hashivault_common.py > library/hashivault_authbackend.py
	@cat library/hashivault_authbackend_templ.py >> library/hashivault_authbackend.py

.PHONY: modules
modules: library/hashivault_authbackend.py
