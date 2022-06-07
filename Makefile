
wheel: clean
	python setup.py bdist_wheel
docker: wheel
	cp dist/*.whl docker/root/
	sudo docker build --no-cache -t ytdl-sub:0.1 docker/
docs:
	sphinx-build -a -b html docs docs/_html
clean:
	rm -rf \
		.pytest_cache/ \
		build/ \
		dist/ \
		src/ytdl_sub.egg-info/ \
		.coverage \
		coverage.xml

.PHONY: wheel docker docs clean
