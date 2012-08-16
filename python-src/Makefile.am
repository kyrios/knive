EXTRA_DIST = configobj knive webknive users.txt kniveServ.py

all-local:
	$(PYTHON) setup.py build

install-exec-local:
	$(PYTHON) setup.py install --optimize --prefix=$(DESTDIR)$(prefix)  --record installedFiles.txt

uninstall-local:
	cat installedFiles.txt | xargs rm -rf

clean-local:
	$(PYTHON) setup.py clean --all
	@rm -f $(top_builddir)/*.pyc

dist-hook:
	rm -rf `find $(distdir) -type f -name "*.pyc"`