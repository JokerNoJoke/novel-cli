.PHONY: test build clean

test:
	uv run python -m unittest discover -v tests/

build:
	mkdir -p dist/build
	# Copy package into build dir so it remains a package
	cp -r novel_cli dist/build/
	# Create entry point that calls the package main
	echo 'import sys; from novel_cli.__main__ import main; sys.exit(main())' > dist/build/__main__.py
	uv run python -m zipapp dist/build -o dist/novel-cli.pyz -p "/usr/bin/env python3"
	rm -rf dist/build
	@echo "Build complete: dist/novel-cli.pyz"
	@echo "Run with: ./dist/novel-cli.pyz"

clean:
	rm -rf dist
	rm -rf plugin_api/__pycache__ novel_cli/__pycache__ tests/__pycache__
