PLATYPUS=/usr/local/bin/platypus
PLATYPUS_PROFILE=Mailfrob.platypus

WKHTMLTOPDF_PKG := $(shell find lib -name "wkhtmlto*.pkg" -print0)
WKHTMLTOPDF_TMPDIR=lib/tmp
PATH_TO_WKHTMLTOX_INSTALLER=/usr/local/share/wkhtmltox-installer

#COCOADIALOG_LINK=https://github.com/downloads/mstratman/cocoadialog/CocoaDialog-2.1.1.dmg

DOWNLOADER=curl -O

all: lib/wkhtmltopdf mailfrob

mailfrob: Mailfrob.app

Mailfrob.app: mailfrob.py lib/wkhtmltopdf
	${PLATYPUS} -P ${PLATYPUS_PROFILE} $@

lib/wkhtmltopdf:
	@/bin/echo -n "Expanding ${WKHTMLTOPDF_PKG}... "
	@pkgutil --expand "${WKHTMLTOPDF_PKG}" "${WKHTMLTOPDF_TMPDIR}"
	@(cd ${WKHTMLTOPDF_TMPDIR}; tar xf Payload)
	@(cd ${WKHTMLTOPDF_TMPDIR}${PATH_TO_WKHTMLTOX_INSTALLER}; tar xf app.tar.xz)
	@cp ${WKHTMLTOPDF_TMPDIR}${PATH_TO_WKHTMLTOX_INSTALLER}/bin/wkhtmltopdf lib
	@rm -rf lib/tmp
	@/bin/echo Done.

