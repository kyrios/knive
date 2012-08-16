AC_PREREQ([2.69])
AC_INIT([knive], [0.1.0], [knive@kyri0s.de])
m4_include([autotools_ax_python_module.m4])
AC_CONFIG_SRCDIR([src/live_segmenter.c])
AC_CONFIG_FILES([python-src/Makefile])
AC_CONFIG_FILES([python-src/setup.py], [chmod +x python-src/setup.py])
AM_INIT_AUTOMAKE


# Checks for programs.
AC_PROG_CC
AC_PROG_MAKE_SET
AC_PATH_PROG([ffmpeg_bin_path],[ffmpeg])


AC_CHECK_LIB([avformat], [avio_open],[],[AC_MSG_ERROR(could not find required version of libavformat >= 52.92.0)])
AC_CHECK_LIB([avcodec], [av_dup_packet],[],[AC_MSG_ERROR(could not find required version of libavcodec)])
AC_CHECK_LIB([avutil], [av_freep],[],[AC_MSG_ERROR(could not find required version of libavutil)])


# Checks for header files.
AC_CHECK_HEADERS([string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([memset])

AC_CONFIG_FILES([Makefile src/Makefile])
#                 doc/Makefile
#                 src/Makefile])

# if test "$ac_cv_lib_avformat_avio_open" == no
# then
# 	AC_MSG_ERROR([Error, libavformat is required])
# fi
AM_PATH_PYTHON([2.7])
AX_PYTHON_MODULE([crypt],[.])
AX_PYTHON_MODULE([pyasn1],[.])
AX_PYTHON_MODULE([logging],[.])
AX_PYTHON_MODULE([twisted.conch.manhole_tap],[.])
AX_PYTHON_MODULE([zope.interface],[.])
AX_PYTHON_MODULE([json],[.])


AC_OUTPUT
