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
import sys
from pathlib import Path

from PySide6.QtCore import QSysInfo
from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from . import about_info
from . import style_rc  # pylint: disable=unused-import
from .version_info import PRODUCT_VERSION

dialogDisclaimers = len(sys.argv) > 1 and sys.argv[1].lower().startswith('disc')

app = QApplication(sys.argv)

appName = 'About'
app.setOrganizationName('eduardovalle.com')
app.setOrganizationDomain('tests.eduardovalle.com')
app.setApplicationName(appName)
app.setApplicationVersion(PRODUCT_VERSION)

# Application resources
applicationPath = Path(__file__).resolve(strict=True)
applicationDir = applicationPath.parent.parent
imagesDir = applicationDir / 'resources' / 'images'
fontsDir = applicationDir / 'resources' / 'fonts'
dataDir = applicationDir / 'resources' / 'data'
textDir = applicationDir / 'resources' / 'text'
examplesDir = applicationDir / 'resources' / 'examples'
qmlDir = applicationDir / 'gui'

about_info.configureAboutInfo(applicationObject=app, textDirPathObject=textDir)

# Load fonts
for typeface in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Medium.ttf", "Roboto-MediumItalic.ttf",
                 "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf",):
    fontPath = str(fontsDir / typeface)
    QFontDatabase.addApplicationFont(fontPath)

PLATFORM_SYSTEM = QSysInfo.kernelType()
PLATFORM_MACOS = PLATFORM_SYSTEM == 'darwin'

if __name__ == '__main__':
    controlsTheme = 'Material' if PLATFORM_MACOS else 'Universal'
    QQuickStyle.setStyle(controlsTheme)
    engine = QQmlApplicationEngine()
    print('theme = "%s", engine = %s' % (controlsTheme, engine))

    # Adds global symbols to QML
    rootContext = engine.rootContext()
    imagesUri = imagesDir.as_uri()
    rootContext.setContextProperty('IMAGES_URI', imagesUri)
    dataUri = dataDir.as_uri()
    rootContext.setContextProperty('DATA_URI', dataUri)
    rootContext.setContextProperty('CONTROLS_THEME', controlsTheme)
    rootContext.setContextProperty('DIALOG_DEBUG', True)
    print('-- global symbols created')

    if dialogDisclaimers:
        qml_path = qmlDir / 'Disclaimers.qml'
    else:
        qml_path = qmlDir / 'About.qml'
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    result = app.exec()

    if result != 0:
        print('ERROR: program exitted with code:', result)
        sys.exit(result)
