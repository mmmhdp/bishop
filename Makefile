IMAGE_NAME = structurizr/lite
RELATIVE_PATH = ./docs


.PHONY: docs_up
docs_up:
	@docker run -it --rm -d -p 8080:8080 -v $(RELATIVE_PATH):/usr/local/structurizr \
		-e STRUCTURIZR_WORKSPACE_PATH=bishop \
		-e STRUCTURIZR_WORKSPACE_FILENAME=system-landscape $(IMAGE_NAME)

.PHONY: docs_down
docs_down:
	@docker ps --filter ancestor=$(IMAGE_NAME) -q | xargs -r docker stop

