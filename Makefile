
export DATE=$(shell date +'%Y.%m.%d')
export REV=$(shell git rev-parse --short HEAD)
export VERSION="$(DATE)+$(REV)"

lint:
	@-isort .
	@-black .
	@-pylint src/
	@-pydocstyle src/*
check_lint:
	isort . --check-only --diff  \
		&& black . --check  \
		&& pylint src/  \
		&& pydocstyle src/*
wheel: clean
	$(shell echo "__version__ = \"$(VERSION)\"" > src/ytdl_sub/__init__.py)
	pip3 install build
	python3 -m build
docker_stage: wheel
	cp dist/*.whl docker/root/
	cp -R examples docker/root/defaults/
docker: docker_stage
	sudo docker build --no-cache -t ytdl-sub:local docker/
docs:
	sphinx-build -a -b html docs docs/_html
clean:
	rm -rf \
		.pytest_cache/ \
		build/ \
		dist/ \
		src/ytdl_sub.egg-info/ \
		docs/_html/ \
		.coverage \
		docker/root/*.whl \
		docker/root/defaults/examples \
		coverage.xml

.PHONY: lint check_lint wheel docker_stage docker docs clean
