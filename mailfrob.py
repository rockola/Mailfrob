#!/usr/bin/python

################################################################
# mailfrob.py
# (c) 2015 Ola Rinta-Koski <mailfrob@rinta-koski.net>
# MIT License
################################################################

import os
import sys
import shutil
import fnmatch
import email
import email.header
import errno
import mimetypes
import re

from cgi import escape
from string import maketrans
#from tempfile import mkstemp
from subprocess import call, Popen, PIPE

cocoa = "CocoaDialog.app/Contents/MacOS/CocoaDialog"

def dirselect( ):
    "Cocoa dialog - select (only) directory"
    output = ''
    try:
        # --with-directory {directory}: start in {directory}
        # --with-file {file}: start with {directory}/{file};
        #                     needs --with-directory
        cocoa_args = [cocoa, "filesave",
                      "--title", "Choose a directory",
                      "--text", "Choose a file/directory"]
        p = Popen(cocoa_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
    except OSError as e:
        print "CocoaDialog error({0}): {1}".format(e.errno, e.strerror)
        print os.getcwd()
        print cocoa
    return os.path.dirname(output), output


#try:
#    os.mkdir(outputdir)
#except OSError as e:
#    # Ignore directory exists error
#    if e.errno != errno.EEXIST:
#        raise

emailfile = ''
junkarg = re.compile(r'-')

# emailfile = path to file underlying the Apple Mail email message
#
# we look for .emlx files
pattern = r'(?P<id>\d+)(?P<partial>\.partial)?\.emlx$'
nameregex = re.compile(pattern)
m = False
for arg in sys.argv:
    if junkarg.match(arg):
        continue
    m = nameregex.search(arg)
    if m:
        emailfile = arg
        break
    else:
        # print arg, "does not match", pattern
        pass

if not emailfile:
    print "Drag'n'drop failed - please press <ALT> while dragging"
    sys.exit()

inputdir = os.path.dirname(emailfile)
print "email file", emailfile
sys.stdout.flush()

outputdir, fullfilepath = dirselect()
print "Outputdir", outputdir
print "fullfilepath", fullfilepath
sys.stdout.flush()

# UNUSED!
# The idea was to copy attachments from ../Attachments/{...}
# however, it would appear that attachments show up there only
# sometimes - probably if they've already been viewed in Apple Mail
def copy_existing_attachments():
    attachmentdir = None
    if m:
        print "ID", m.group('id')
        print "partial", m.group('partial')
        repl = "Attachments/" + m.group('id')
        attachmentdir = os.path.dirname(emailfile).replace("Messages", repl)
        print "Attachments are in", attachmentdir
        attachments = []
        attachmentindex = 1
        for root, dirnames, filenames in os.walk(attachmentdir):
            for filename in filenames:
                fullpath = os.path.join(root, filename)
                attachments.append(fullpath)
                print "Attachment #", attachmentindex, ":", fullpath
                attachmentindex += 1
                shutil.copy2(fullpath, outputdir)
    else:
        print pattern, "doesn't match", emailfile
    return attachmentdir

def attachmentdir( n ):
    print "ID", m.group('id')
    print "partial", m.group('partial')
    repl = "Attachments/" + m.group('id')
    return os.path.join(os.path.dirname(emailfile).replace("Messages", repl), str(n))


f = open(emailfile, "r")
# fnumber = magic number Apple Mail sticks in front of the MIME email
# needs to be discarded before file can be fed to email parser
fnumber = f.readline()
# msg = actual MIME email (does not include Apple XML stuff at the end)
msg = email.message_from_file(f)
f.close()

counter = 1
attachmentcounter = 1
attachmentsinemlx = []
plaintext = []
html = []

def attachmentfilenum( n = attachmentcounter ):
    return n + 1
def attachmentondisk( i ):
    return m.group('id') + '.' + str(attachmentfilenum(i)) + ".emlxpart"
def savedattachment( acounter, filename ):
    return os.path.join(attachmentdir(acounter), filename)


for part in msg.walk():
    if part.get_content_maintype() == 'multipart':
        continue
    filename = part.get_filename()
    contenttype = part.get_content_type()
    counter += 1
    if filename:
        has_filename = True
    else:
        has_filename = False
        print "Not an attachment; content type for", counter, "is", contenttype
        ext = mimetypes.guess_extension(contenttype)
        if not ext:
            # hope we never get here but if we do,
            # "Use a generic bag-of-bits extension"
            ext = '.bin'
        filename = 'part-%03d%s' % (counter, ext)
    if has_filename:
        print "This is attachment #", attachmentcounter
        thisattachment = attachmentcounter
        attachmentcounter += 1
        # attachment has filename, but might still be inline
        inline = part.get_param('inline', None, 'content-disposition')
        if inline:
            # the payload is inline, get it from there
            pass
        else:
            print "Current payload is", part.get_payload()
            if not part.get_payload():
                # attachment is on disk
                attachmentfname = savedattachment(thisattachment, filename)
                if os.path.isfile(attachmentfname):
                    # already saved to ../Attachment dir
                    print "This is processed attachment", thisattachment, "in file", attachmentfname
                    try:
                        shutil.copy2(attachmentfname, outputdir)
                    except (IOError, os.error) as e:
                        print "Could not copy", attachmentfname, "to", outputdir, ":", str(e)
                    continue
                else:
                    attachmentfname = attachmentondisk(thisattachment)
                    print "This is raw attachment", thisattachment, "in file", attachmentfname
                    # no payload, set it from file
                    fp = open(os.path.join(inputdir, attachmentfname), 'r')
                    r = fp.read()
                    fp.close()
                    part.set_payload(r)
        contents = part.get_payload(decode=True)
        print "Saving as", filename
        sys.stdout.flush()
        fp = open(os.path.join(outputdir, filename), 'wb')
        fp.write(contents)
        fp.close()
        # attachmentcounter += 1
        attachmentsinemlx.append(filename)
    else:
        contents = part.get_payload(decode=True)
        charset = part.get_content_charset()
        if contenttype == 'text/plain':
            print "Charset is", charset
            #plaintext.append(contents)
            plaintext.append(contents.decode(charset).encode("UTF-8"))
            continue
        if contenttype == 'text/html':
            print "Charset is", charset
            html.append(contents.decode(charset).encode("UTF-8"))
            continue
        print sys.getsizeof(contents), " bytes"
        print "Saving as", filename
        sys.stdout.flush()
        fp = open(os.path.join(outputdir, filename), 'wb')
        fp.write(contents)
        fp.close()

################################################################
# plaintext version

print 'From', msg['from']
print 'Subject', msg['subject']
print 'Date', msg['date']
print 'To', msg['to']
print
sys.stdout.flush()

ia = 1
for a in attachmentsinemlx:
    print 'Attachment', ia, ':', a
    ia += 1

print    

for p in plaintext:
    print p

sys.stdout.flush()

# end of plaintext version
################################################################

################################################################
# HTML version

htmlfile = "msg.html"
htmlfilepath = os.path.join(outputdir, htmlfile)

def pdffilenamewithordinal( s, n ):
    if n == 1:
        return os.path.join(outputdir, s + '.pdf')
    else:
        return os.path.join(outputdir, s + ' ' + str(n) + '.pdf')

def pdffilename( name ):
    decodedsubject = ''
    trans = maketrans(u"/:", u"__")
    for decodedpartstring, subjectcharset in name:
        # TODO: convert according to charset
        decodedsubject += decodedpartstring
    s = decodedsubject.translate(trans)
    if s.startswith('.'):
        s = '_' + s
    i = 1
    while True:
        path = pdffilenamewithordinal( s, i )
        if os.path.isfile(path):
            i += 1
        else:
            break
    return path
        
pdffile = pdffilename(email.header.decode_header(msg['subject']))
    
print "PDF output in", pdffile

html_header = """
<!DOCTYPE html>
<html>
<meta charset="UTF-8"
<head>
<title>Your title here</title>
</head>
<body>
"""

html_footer = """
</body>
</html>
"""

def header2html( title, content, emp='b' ):
    r = '<' + emp + '>' + title + ':</' + emp + '> '
    for partstring, partcharset in email.header.decode_header(content):
        # TODO: do something with partcharset
        # now assumed to just magically 'work'
        r += escape(partstring)
    r += '<br>'
    return r

html_email_header = ''
html_email_header += header2html('From', msg['from'])
html_email_header += header2html('Subject', msg['subject'])
html_email_header += header2html('Date', msg['date'])
html_email_header += header2html('To', msg['to'])

ia = 1
for a in attachmentsinemlx:
    html_email_header += header2html('Attachment ' + str(ia), a, emp='i')
    ia += 1


fp = open(htmlfilepath, 'wb')

fp.write(html_header)
fp.write(html_email_header)
fp.write('<p>&nbsp;</p>')

if not html:
    for p in plaintext:
        fp.write('<div style="white-space: pre-wrap;">')
        fp.write(p)
        fp.write('</div>')
else:
    for h in html:
        fp.write(h)

fp.write(html_footer)
fp.close()

sys.stdout.flush()

def dialog( prompt ):
    "Cocoa dialog"
    try:
        call([cocoa, "yesno-msgbox", "--title", "Foo", "--text", prompt, "--informative-text", "bar"])
    except OSError as e:
        print "CocoaDialog error({0}): {1}".format(e.errno, e.strerror)
        print os.getcwd()
        print cocoa
        print prompt
    return 0



print "Saving email as PDF in", pdffile, "; tmp HTML in", htmlfilepath
htmltopdf = './wkhtmltopdf'
try:
    sys.stdout.flush()
    call([htmltopdf, htmlfilepath, pdffile])
    sys.stdout.flush()
    os.remove(htmlfilepath)
except OSError as e:
    print "OS error({0}): {1}".format(e.errno, e.strerror)
    print os.getcwd()
    print htmltopdf
    print htmlfilepath
    print pdffile

#
################################################################

#dialog("Saved email as PDF in " + pdffile)
sys.stdout.flush()
