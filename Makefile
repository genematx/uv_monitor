# Declare constants
IMAGE_NAME = "uv_monitor"
PWD = $(shell pwd)
TEST_PATH = tests

#- Download and prepare the data
# Define the list of URLs
urls := \
  https://uvb.nrel.colostate.edu/uvbdata/erythemal/locations/NewZealand-erythemal.zip

# Download the archives
archives:
	mkdir -p ./data
	for url in $(urls); do \
    	echo "Downloading $$url"; \
		wget -P ./data $$url; \
	done

# Unzip the archives
unzipped: archives
	for archive in ./data/*.zip; do \
    	echo "Extracting $$archive"; \
    	unzip -o -qq $$archive -d ./data; \
    	rm $$archive; \
	done

#- Development and Debugging
## Build the development Docker image
build: 
	docker build \
	-t $(IMAGE_NAME):dev -f docker/Dockerfile --target=dev .

## Open a bash shell inside the local dev container
bash: build
	docker run -it --rm \
	-e CI \
	-v $(PWD):/workspace \
	$(IMAGE_NAME):dev bash 

#- Testing and formatting
## Run unit tests locally in Docker
test: build
	docker run --rm \
	-e CI \
	-v $(PWD):/workspace \
	$(IMAGE_NAME):dev \
	test $(if $(test-args),$(test-args),$(TEST_PATH))

## Run style checks
lint: build
	docker run --rm \
	-e CI \
	-v $(PWD):/workspace \
	$(IMAGE_NAME):dev \
	lint

## Run code formatters
fmt: build
	docker run --rm \
	-e CI \
	-v $(PWD):/workspace \
	$(IMAGE_NAME):dev \
	fmt $(isort-args) $(black-args)

## Build the production Docker image
build-prod: 
	docker build \
	-t $(IMAGE_NAME):latest -f docker/Dockerfile --target=prod .

## Prune Docker containers, networks, and images
clean:
	docker system prune -f
