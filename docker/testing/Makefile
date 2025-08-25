# Local building and testing of the Docker image variants.

# Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-eu -o pipefail -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules
export PS1?=$$
# Prefix echoed recipe commands with the recipe line number for debugging:
export PS4?=:$$LINENO+

VARIANTS=headless gui ubuntu
ROOT_PREREQS:=$(shell find ../root -type f)

# Finished with `$(shell)`, echo recipe commands going forward
.SHELLFLAGS+= -x


### Top-level targets:

.PHONY: all
all: build

.PHONY: build
build: $(VARIANTS:%=./build/ytdl-sub-%.log)

.PHONY: run
run: build $(VARIANTS:%=./volumes/ytdl-sub-%/)
	docker compose up


### Real targets:

# Re-build the local images when changes require it.
./build/ytdl-sub-%.log: ../Dockerfile.% $(ROOT_PREREQS)
	mkdir -pv "$(dir $(@))"
	docker compose build "$(@:build/ytdl-sub-%.log=ytdl-sub-%)" |&
	    tee -a "$(@)"

# Ensure volumes are owned by the developer's normal user:
./volumes/ytdl-sub-%/:
	mkdir -pv "$(@)"
