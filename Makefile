#
## use the BASH shell 
SHELL=/bin/bash

DANGLING_CONTAINERS=$(shell docker images -f "dangling=true" -q)

##
## point at work and source directories ...
WRK_DIR=./app
SRC_DIR=../src
TST_DIR=./test
REQ=requirements.txt 

##
## artifacts ... 

all:	$(WRK_DIR) update

$(WRK_DIR):
	python3 -m venv $(WRK_DIR)
	cp $(REQ) $(WRK_DIR)
	cd $(WRK_DIR); . bin/activate ; pip install --upgrade pip
	cd $(WRK_DIR); . bin/activate ; pip install -r $(REQ)

update: $(WRK_DIR)
	cd $(WRK_DIR) ; cp -r $(SRC_DIR)/* . 

launch:	update
	docker run -d -p 0.0.0.0:8001:8001 --priviledged $(DOCKER_IMAGE)

realclean:
	rm -rf $(WRK_DIR)
	docker rmi -f $(DANGLING_CONTAINERS) dummy

depends:
	sudo apt-get install build-essential libi2c-dev i2c-tools python-dev libffi-dev
	curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh