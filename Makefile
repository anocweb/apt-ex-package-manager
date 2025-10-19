# Makefile for Apt-Ex Package Manager

PREFIX ?= /usr
DESTDIR ?=
PYTHON ?= python3

.PHONY: install uninstall clean test

install:
	# Install Python package
	$(PYTHON) setup.py install --prefix=$(PREFIX) --root=$(DESTDIR)
	
	# Create plugin directory
	install -d $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/plugins
	
	# Copy plugins
	install -m 644 src/controllers/plugins/*.py $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/plugins/
	
	# Copy UI files
	install -d $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/ui
	install -m 644 src/ui/*.ui $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/ui/
	
	# Copy icons
	install -d $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/icons
	install -m 644 src/icons/*.svg $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager/icons/
	
	# Install desktop file
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install -m 644 apt-ex-package-manager.desktop $(DESTDIR)$(PREFIX)/share/applications/

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/share/apt-ex-package-manager
	rm -f $(DESTDIR)$(PREFIX)/share/applications/apt-ex-package-manager.desktop
	$(PYTHON) setup.py uninstall

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	$(PYTHON) -m pytest tests/

dev:
	$(PYTHON) src/main.py
