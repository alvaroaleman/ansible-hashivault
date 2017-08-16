vault:
	docker run -d \
		--name=vault \
		-e VAULT_DEV_ROOT_TOKEN_ID=helloworld \
		-e 'VAULT_LOCAL_CONFIG={"disable_mlock": true}' \
		-p 127.0.0.1:8300:8200 \
		vault
