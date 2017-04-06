#!/usr/bin/env make

# Should contain:
# {D4R,K8S}_{NAME,NS,HOST}
include Makefile.defs

# Base other vars on imported ones.
K8S_DEPLOY_BASE = https://$(K8S_HOST)/apis/extensions/v1beta1
K8S_DEPLOY_URL = $(K8S_DEPLOY_BASE)/namespaces/$(K8S_NS)/deployments/$(K8S_NAME)
D4R_IMAGE = $(D4R_HOST)/$(D4R_NS)/$(D4R_NAME)

# Current time.
DATE = $(shell date '+%Y-%m-%d %H:%M:%S')

# Forces new deploy because of "changes" when/if TAG is unchanged.
# Without a metadata label change, the lack of change to the containers
# would cause no deployment. Only if a deployment is scheduled does it
# actually attempt to force-pull (imagePullPolicy=Always).
FORCEPUSH = $(shell date '+S%s')


.PHONY: dbuild dpush kdeploy has_dtag has_ktoken

help:
	@echo 'Usage:'
	@echo '  make DTAG=0.1.2web1 dbuild		# docker build'
	@echo '  make DTAG=0.1.2web1 dpush		# docker push'
	@echo '  make DTAG=0.1.2web1 kdeploy KTOKEN=longapikey==  # k8s deploy'
	@echo
	@echo 'Define the following in Makefile.defs for Docker:'
	@echo '  D4R_NAME = myproject'
	@echo '  D4R_NS = myorg'
	@echo '  D4R_HOST = hub.docker.io'
	@echo 'And the same for Kubernetes in K8S_{NAME,NS,HOST}.'
	@echo
	@echo 'The DTAG and KTOKEN are the Docker image version (tag) and the '
	@echo 'Kubernetes token respectively. The GTAG is the git tag.'

dbuild: has_dtag prerequisites
	docker build -t $(D4R_IMAGE):$(DTAG) .

dpush: has_dtag
	docker login $(D4R_HOST)
	docker push $(D4R_IMAGE):$(DTAG)

kdeploy: has_ktoken
	curl -s -XPATCH -H "Content-Type: application/strategic-merge-patch+json" \
		-H "Authorization: Bearer $(KTOKEN)" \
		-d '{"spec":{"template":{"spec":{'\
'                     "containers":[{"image":"$(D4R_IMAGE):$(DTAG)","name":"$(K8S_NAME)"}]},'\
'                     "metadata":{"labels":{"forcePush":"$(FORCEPUSH)"}}}},'\
'                    "metadata":{"annotations":'\
'                     {"kubernetes.io/change-cause":"Makefile deploy ver. $(DTAG) [$(DATE)]"}}}' \
		-k $(K8S_DEPLOY_URL)
	#' # vim-syn-fix

has_dtag:
	@test -n "$(DTAG)" || (echo 'Please specify DTAG=nnn on the cmd line' >&2; false)

has_ktoken:
	@test -n "$(KTOKEN)" || (echo 'Please specify KTOKEN= on the cmd line' >&2; false)


.PHONY: docker_run docker_bash docker_inspect

docker_run: dbuild
	docker run -d '$(D4R_IMAGE):$(DTAG)'

docker_bash: dbuild
	docker run -it '$(D4R_IMAGE):$(DTAG)' /bin/bash

docker_inspect: dbuild  # and run
	ID=$$(docker ps -f 'ancestor=$(D4R_IMAGE):$(DTAG)' --format '{{.ID}}') && \
	  echo "ID = $$ID" && docker inspect $$ID


.PHONY: prerequisites has_gtag

G4B_RAW_BASE = https://raw.githubusercontent.com/$(G4B_NS)/$(G4B_NAME)

prerequisites: index.html wsgi.py

index.html:
	@test -n "$(GTAG)" || (echo 'Please specify GTAG=nnn on the cmd line' >&2; false)
	curl '$(G4B_RAW_BASE)/$(GTAG)/web/index.html' >index.html || $(RM) index.html

wsgi.py:
	@test -n "$(GTAG)" || (echo 'Please specify GTAG=nnn on the cmd line' >&2; false)
	curl '$(G4B_RAW_BASE)/$(GTAG)/web/wsgi.py' >wsgi.py || $(RM) wsgi.py
