# ======================================================================================================================
# Copyright 2022 Eduardo Valle.
#
# This file is part of Cook-a-Dream.
#
# Cook-a-Dream is free software: you can redistribute it and/or modify it under the terms of the version 3 of the GNU
# General Public License as published by the Free Software Foundation.
#
# Cook-a-Dream is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Cook-a-Dream. If not, see
# https://www.gnu.org/licenses.
# ======================================================================================================================
# pylint: disable=invalid-name

import re
import sys

lightformatTextFileName = sys.argv[1]
htmlFileName = sys.argv[2]

# Reads and preprocesses input file
with open(lightformatTextFileName, 'rt', encoding='utf-8') as lightformatTextFile:
    lightformatText = lightformatTextFile.readlines()

lightformatText = [l.rstrip() for l in lightformatText]
lightformatText = [l for l in lightformatText if l]

# Prepares regular expressions for recognizins section headers, license text and text bolding
matchHeader  = re.compile(r'^(#+)\s*(.*)$')
matchLicense = re.compile(r'^\>\s*(.*)$')
matchBold    = re.compile(r'\*\*(.*?)\*\*')
matchItalics = re.compile(r'__(.*?)__')
matchLink    = re.compile(r'(https?://\S*)')

# Prepares options for formatting
# https://doc.qt.io/qt-6.2/richtext-html-subset.html
formatChoices = {
    'default': {
        'margin-top'    : '6px',
        'margin-left'   : '0px',
        'margin-bottom' : '0px',
        # 'font-family'   : 'serif',
        'font-size'     : 'medium',
        'font-style'    : 'normal',
        'font-weight'   : 'normal',
    },
    'h1': {
        'margin-top'  : '12px',
        'font-size'   : 'large',
        'font-weight' : 'bold',
    },
    'h2': {
        'margin-top'  : '12px',
        'font-weight' : 'bold',
    },
    'body': {
        'margin-left' : '24px',
    },
    'license': {
        'margin-left' : '48px',
        'font-style'  : 'italic',
    },
}

defaultFormat = formatChoices['default']
for fc in formatChoices:
    if fc == 'default':
        continue
    formatDict = dict(defaultFormat)
    formatDict.update(formatChoices[fc])
    formatChoices[fc] = formatDict
# formattedTag = '<%s style="margin-top:{margin-top};margin-bottom:{margin-bottom};margin-left:{margin-left};' \
#                'font-style:{font-style};font-weight:{font-weight};font-size:{font-size};font-family:{font-family}">' \
#                '%s</%s>'
formattedTag = '<%s style="margin-top:{margin-top};margin-bottom:{margin-bottom};margin-left:{margin-left};' \
               'font-style:{font-style};font-weight:{font-weight};font-size:{font-size}">' \
               '%s</%s>'

# Ancillary functions for creating the html content
indent = '  '
htmlText = ''
licenseText = ''
bodyText = ''

def emit(html, indentLevel):
    global htmlText
    htmlText += indentLevel * indent + html + '\n'

def emitSectionHeader(text, level):
    headerLevel = f'h{level}'
    header = formattedTag % (headerLevel, text, headerLevel)
    header = header.format(**formatChoices[headerLevel])
    emit(header, level)

def emitText(text, formatName):
    text = formattedTag % ('p', text, 'p')
    text = text.format(**formatChoices[formatName])
    emit(text, 3)

def formatText(text):
    text = matchBold.sub(r'<b>\1</b>', text)
    text = matchItalics.sub(r'<i>\1</i>', text)
    text = matchLink.sub(r'<a style="text-decoration:none" href="\1">\1</a>', text)
    return text

def emitAccumulated(text, formatName):
    if text:
        emitText(text, formatName)
    return ''

# Converts text to html
emit('<html>', 0)
for lft in lightformatText:
    if lft[:3] == '[[[' and lft[-3:] == ']]]':
        emit(lft, 3)
        continue

    m = matchHeader.fullmatch(lft)
    if m:
        licenseText = emitAccumulated(licenseText, 'license')
        bodyText = emitAccumulated(bodyText, 'body')
        sectionLevel = len(m.group(1))
        headerText = m.group(2)
        emitSectionHeader(headerText, sectionLevel)
        continue

    m = matchLicense.fullmatch(lft)
    if m:
        bodyText = emitAccumulated(bodyText, 'body')
        if licenseText:
            licenseText += '<br/>'
        licenseText += formatText(m.group(1))
        continue

    licenseText = emitAccumulated(licenseText, 'license')
    if bodyText:
        bodyText += '<br/>'
    bodyTextContinues = lft[-1:] == '\\'
    newBodyText = lft[:-1] if bodyTextContinues else lft
    bodyText += formatText(newBodyText)
    if not bodyTextContinues:
        bodyText = emitAccumulated(bodyText, 'body')

licenseText = emitAccumulated(licenseText, 'license')
bodyText = emitAccumulated(bodyText, 'body')
emit('</html>', 0)

# Writes formatted text
with open(htmlFileName, 'wt', encoding='utf-8') as htmlFile:
    htmlFile.write(htmlText)
