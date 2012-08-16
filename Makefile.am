SUBDIRS = src python-src
knivedir = $(datarootdir)/knive
knive_DATA = knive.conf.dist
EXTRA_DIST = knive.conf.dist knive.conf.dist.in

knive.conf.dist: knive.conf.dist.in
	sed \
		-e 's|[@]prefix@|$(prefix)|g' \
		-e 's|[@]exec_prefix@|$(exec_prefix)|g' \
		-e 's|[@]bindir@|$(bindir)|g' \
		-e 's|[@]datarootdir@|$(datarootdir)|g' \
		-e 's|[@]localstatedir@|$(localstatedir)|g' \
		-e 's|[@]ffmpeg_bin_path@|$(ffmpeg_bin_path)|g' \
		< "$<" > "$@"
