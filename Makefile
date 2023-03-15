# Get version related variables
export DATE=$(shell date +'%Y.%m.%d')
export DATE_COMMIT_COUNT=$(shell git rev-list --count HEAD --since="$(DATE) 00:00:00")
export COMMIT_HASH=$(shell git rev-parse --short HEAD)

# Set Local version to YYYY.MM.DD-<hash>
export LOCAL_VERSION="$(DATE)+$(COMMIT_HASH)"

# Set PyPi version to YYYY.MM.DD or YYYY.MM.DD.postN if N > 0
ifeq ("$(DATE_COMMIT_COUNT)", "0")
	export PYPI_VERSION="$(DATE)"
else
	export PYPI_VERSION="$(DATE).post$(DATE_COMMIT_COUNT)"
endif

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
	$(shell echo "__pypi_version__ = \"$(PYPI_VERSION)\"\n__local_version__ = \"$(LOCAL_VERSION)\"" > src/ytdl_sub/__init__.py)
	cat src/ytdl_sub/__init__.py
	pip3 install build
	python3 -m build
docker_stage: wheel
	cp dist/*.whl docker/root/
	cp -R examples docker/root/defaults/
docker: docker_stage
	sudo docker build --progress=plain --no-cache -t ytdl-sub:local docker/
docker_ubuntu: docker_stage
	sudo docker build --progress=plain --no-cache -t ytdl-sub:local_ubuntu -f docker/Dockerfile.ubuntu docker/
executable: clean
	pyinstaller ytdl-sub.spec
	mv dist/ytdl-sub dist/ytdl-sub${EXEC_SUFFIX}
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
