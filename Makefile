.PHONY: help deb clean install uninstall

help:
	@echo "Apt-Ex Package Manager - Build Targets"
	@echo "======================================"
	@echo "  deb        - Build Debian package"
	@echo "  clean      - Clean build artifacts"
	@echo "  install    - Install locally (requires sudo)"
	@echo "  uninstall  - Uninstall (requires sudo)"

deb:
	@./build-deb.sh

clean:
	rm -rf debian/apt-ex-package-manager
	rm -rf debian/.debhelper
	rm -rf debian/files
	rm -rf debian/*.substvars
	rm -rf debian/*.log
	rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

install:
	@if [ -f ../apt-ex-package-manager_*.deb ]; then \
		sudo apt install ../apt-ex-package-manager_*.deb; \
	else \
		echo "No .deb file found. Run 'make deb' first."; \
		exit 1; \
	fi

uninstall:
	sudo apt remove apt-ex-package-manager
