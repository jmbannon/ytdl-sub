
build:
	python setup.py bdist_wheel --dist-dir docker
docker: build
	sudo docker build -t ytdl-sub:0.1 docker/

.PHONY: build
