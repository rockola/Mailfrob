# Mailfrob

Mailfrob is a drag'n'drop helper for Apple Mail. When you drag an
email from Apple Mail and drop it on Mailfrob, you'll be asked for a
directory in which the mail will be copied. When you have selected the
directory, the attachments will be copied there, and the email message
itself will be saved as a PDF file.

## Motivation

If you drag'n'drop from Apple Mail to Finder, your email message is
saved as an .eml file. However, there are way more steps if you wish
to save all the attachments as well as the email itself as a
PDF. Hence, Mailfrob.

## Compatibility

Mailfrob is known to work with Mail.app 9.1 (3096.5) on OSX
10.11.1. OSX and/or Mail.app versions prior to El Capitan (10.11) are
unlikely to work.

Mailfrob may break when Mail.app is updated, as it goes behind the
scenes to retrieve the email & attachments; Mailfrob makes some
assumptions about the directory structure in ~/Library/Mail.

## Building Mailfrob from source

The heart of Mailfrob is mailfrob.py, a Python program that does
all the dirty work. Since OSX comes with Python 2.x, you should not
need to install Python or any additional libraries.

### Platypus

The Python program is turned into a proper OSX app with Platypus,
available at
http://www.sveinbjorn.org/platypus

When you have installed Platypus, go to Preferences and click Install
under "Command line tool is not installed". This will install the
command line version of platypus in /usr/local/bin. You can build
platypus without installing the CLI version just by using Platypus.app
itself, however, the provided Makefile needs the CLI version.

### wkhtmltopdf

wkhtmltopdf is used for saving the email message as PDF.

Step 1:
Download the wkhtmltopdf OSX 64-bit package from
http://wkhtmltopdf.org/downloads.html which, at the time of writing this, is at
http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_osx-cocoa-x86-64.pkg
and copy it to ./lib.

Step 2:
The Makefile contains a rule to unpack the wkhtmltox distribution and
copy the wkhtmltopdf binary to ./lib.

    % make lib/wkhtmltopdf
    Expanding lib/wkhtmltox-0.12.2.1_osx-cocoa-x86-64.pkg...Done.

Step 3 (optional):
Remove the .pkg file from ./lib as it is no longer needed.

wkhtmltopdf is licensed under GNU LGPL v3.

### CocoaDialog

CocoaDialog is used for the file dialog that is used to select and, if
necessary, create the output directory.

Step 1:
Download CocoaDialog from
https://github.com/downloads/mstratman/cocoadialog/CocoaDialog-2.1.1.dmg

Step 2:
Mount the CocoaDialog DMG.

Step 3:
Copy CocoaDialog.app to ./lib.

CocoaDialog is licensed under GNU GPL v2.


