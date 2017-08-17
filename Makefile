.PHONY: hashivault_authbackend-test
hashivault_authbackend-test: modules
	ansible-playbook test/playbook.yml -t testsetup,hashivault_authbackend -vvvv

.PHONY: library/hashivault_authbackend.py
library/hashivault_authbackend.py:
	@cat library/hashivault_common.py > library/hashivault_authbackend.py
	@cat library/hashivault_authbackend_templ.py >> library/hashivault_authbackend.py

.PHONY: hashivault_policy.py
hashivault_policy.py:
	@cat library/hashivault_common.py > library/hashivault_policy.py
	@cat library/hashivault_policy_templ.py >> library/hashivault_policy.py

.PHONY: modules
modules: library/hashivault_authbackend.py hashivault_policy.py

.PHONY: test
test: modules
	ansible-playbook test/playbook.yml -vvvv
