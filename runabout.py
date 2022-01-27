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

import pkg_resources
from PySide6.QtCore import Property, QMimeData, QObject, QSysInfo, Signal, Slot
from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QmlElement, QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

import style_rc  # pylint: disable=unused-import
from version_info import PRODUCT_COMMIT, PRODUCT_VERSION

dialogDisclaimers = len(sys.argv) > 1 and sys.argv[1].lower().startswith('disc')

app = QApplication(sys.argv)

appName = 'About'
app.setOrganizationName('eduardovalle.com')
app.setOrganizationDomain('tests.eduardovalle.com')
app.setApplicationName(appName)
app.setApplicationVersion('0.1')


# Application resources
applicationPath = Path(__file__).resolve(strict=True)
# imagesDir = applicationPath.parent / 'resources' / 'images'
applicationPath = Path(__file__).resolve(strict=True)
imagesDir = applicationPath.parent / 'resources' / 'images'
fontsDir = applicationPath.parent / 'resources' / 'fonts'
dataDir = applicationPath.parent / 'resources' / 'data'
textDir = applicationPath.parent / 'resources' / 'text'

# Load fonts
for typeface in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Medium.ttf", "Roboto-MediumItalic.ttf",
                 "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf",):
    fontPath = str(fontsDir / typeface)
    QFontDatabase.addApplicationFont(fontPath)

# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.aboutinfo'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

clipboard = app.clipboard()

@QmlElement
class AboutInfo(QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._licenseText = None
        self._licensePlainText = None
        self._disclaimersText = None
        self._disclaimersPlainText = None
        self._locale = ''
        self._packagesData = self.getPackagesData()
        self._packagesDataText = self.formatPackagesData(self._packagesData, html=True)
        self._packagesDataPlainText = self.formatPackagesData(self._packagesData, html=False)
        self._localeSet('enUS')

    def _loadLicenseTexts(self):
        aboutTextPath = textDir / f'ABOUT_{self.locale}.html'
        with open(aboutTextPath, 'rt', encoding='utf-8') as aboutTextFile:
            aboutText = aboutTextFile.read()
        aboutTextPath = textDir / f'ABOUT_{self.locale}.md'
        with open(aboutTextPath, 'rt', encoding='utf-8') as aboutTextFile:
            aboutPlainText = aboutTextFile.read()
        aboutText = aboutText.replace('[[[PACKAGES_DATA]]]', self._packagesDataText)
        self._licenseText = aboutText
        aboutPlainText = aboutPlainText.replace('[[[PACKAGES_DATA]]]', self._packagesDataPlainText)
        self._licensePlainText = aboutPlainText

    def _loadDisclaimersTexts(self):
        disclaimersTextPath = textDir / f'DISCLAIMERS_{self.locale}.html'
        with open(disclaimersTextPath, 'rt', encoding='utf-8') as disclaimersTextFile:
            disclaimersText = disclaimersTextFile.read()
        disclaimersTextPath = textDir / f'DISCLAIMERS_{self.locale}.md'
        with open(disclaimersTextPath, 'rt', encoding='utf-8') as disclaimersTextFile:
            disclaimersPlainText = disclaimersTextFile.read()
        self._disclaimersText = disclaimersText
        self._disclaimersPlainText = disclaimersPlainText

    @Slot()
    def _refresh(self):
        self._loadLicenseTexts()
        self.licenseTextChanged.emit()
        self.licensePlainTextChanged.emit()
        self._loadDisclaimersTexts()
        self.licensePlainTextChanged.emit()
        self.disclaimersTextChanged.emit()

    # --- Property .licenseText (read-only, protected write)
    licenseTextChanged = Signal(name='licenseTextChanged')

    def licenseTextGet(self):
        if self._licenseText is None:
            self._loadLicenseTexts()
        return self._licenseText

    licenseText = Property(str, licenseTextGet, notify=licenseTextChanged)

    # --- Property .licensePlainText (read-only, protected write)
    licensePlainTextChanged = Signal(name='licensePlainTextChanged')

    def licensePlainTextGet(self):
        if self._licensePlainText is None:
            self._loadLicenseTexts()
        return self._licensePlainText

    licensePlainText = Property(str, licensePlainTextGet, notify=licensePlainTextChanged)

    # --- Property .ready (read-only, protected write)
    disclaimersTextChanged = Signal(name='disclaimersTextChanged')

    def disclaimersTextGet(self):
        if self._disclaimersText is None:
            self._loadDisclaimersTexts()
        return self._disclaimersText

    def _disclaimersTextSet(self, disclaimersText):
        if self._disclaimersText != disclaimersText:
            self._disclaimersText = disclaimersText
            self.disclaimersTextChanged.emit()

    disclaimersText = Property(str, disclaimersTextGet, notify=disclaimersTextChanged)

    # --- Property .ready (read-only, protected write)
    disclaimersPlainTextChanged = Signal(name='disclaimersPlainTextChanged')

    def disclaimersPlainTextGet(self):
        if self._disclaimersPlainText is None:
            self._loadDisclaimersTexts()
        return self._disclaimersPlainText

    disclaimersPlainText = Property(str, disclaimersPlainTextGet, notify=disclaimersPlainTextChanged)

    # --- Property .locale (read-only, protected write)
    localeChanged = Signal(name='localeChanged')

    def localeGet(self):
        return self._locale

    def _localeSet(self, locale):
        if self._locale != locale:
            self._locale = locale
            self.localeChanged.emit()
            if self._licenseText is not None:
                self._loadLicenseTexts()
                self._licenseTextChanged.emit()
                self._licensePlainTextChanged.emit()
            if self._disclaimersText is not None:
                self._loadDisclaimersTexts()
                self._disclaimersTextChanged.emit()
                self._disclaimersPlainTextChanged.emit()

    locale = Property(str, localeGet, notify=localeChanged)

    # --- Version Info
    @Property(str, constant=True)
    def version(self):
        return PRODUCT_VERSION

    @Property(str, constant=True)
    def commit(self):
        return PRODUCT_COMMIT

    # --- System Info
    @Property(str, constant=True)
    def sysinfo(self):
        sysinfo = (QSysInfo.buildAbi(), QSysInfo.currentCpuArchitecture(), QSysInfo.kernelType(),
                   QSysInfo.kernelVersion(), QSysInfo.productType(), QSysInfo.productVersion())
        return '; '.join(sysinfo)

    # --- Slots for copying data
    @Slot()
    def copyLicense(self):
        mimeData = QMimeData()
        mimeData.setHtml(self.licenseText)
        mimeData.setText(self.licensePlainText)
        clipboard.setMimeData(mimeData)

    @Slot()
    def copyInfo(self):
        info = f'{appName}\nVersion: {self.version}\nCommit: {self.commit}\nSysInfo: {self.sysinfo}'
        clipboard.setText(info)

    # --- Ancillary routines for getting installed packages licenses
    @staticmethod
    def getPackageData(package):
        # https://packaging.python.org/en/latest/specifications/core-metadata/
        # https://pypi.org/classifiers/
        metadata = package.get_metadata_lines('METADATA')
        # metadata = package.get_metadata_lines('PKG-INFO')
        packageLicense = ''
        packageClassifierLicense = ''
        packageHomepage = ''
        for m in metadata:
            key = m.lower()
            if key.startswith('license:'):
                packageLicense =  m[8:].strip()
            elif key.startswith('home-page:'):
                packageHomepage =  m[10:].strip()
            elif key.startswith('classifier: license ::'):
                packageClassifierLicense =  m[22:].strip()
            if packageClassifierLicense and packageHomepage:
                break
        if packageLicense.lower() == 'unknown':
            packageLicense = ''
        if packageHomepage.lower() == 'unknown':
            packageHomepage = ''
        if packageClassifierLicense:
            packageLicense = packageClassifierLicense
        if packageLicense.lower().startswith('osi approved ::'):
            packageLicenseWithoutPrefix = packageLicense[15:].strip()
            if len(packageLicenseWithoutPrefix) >= 3:
                packageLicense = packageLicenseWithoutPrefix
        return packageLicense, packageHomepage

    @classmethod
    def getPackagesData(cls):
        packages = pkg_resources.working_set
        packages = sorted(packages, key=lambda p: str(p).lower())
        packagesData = []
        for p in packages:
            packageLicense, packageHomepage = cls.getPackageData(p)
            packageName = str(p)
            packagesData.append((packageName, packageLicense, packageHomepage,))
        return packagesData

    @staticmethod
    def formatPackagesData(packagesData, html=False):
        if html:
            formattedData = [f'    <li><b>{packageName}:</b> License: {packageLicense}, '
                             f'<a style="text-decoration:none" href="{packageHomepage}">{packageHomepage}</a></li>'
                             for packageName, packageLicense, packageHomepage in packagesData]
            formattedData = '      <ul>\n        ' + '\n        '.join(formattedData) + '\n      </ul>\n'
        else:
            formattedData = [f'- {packageName}: License: {packageLicense}, Homepage: {packageHomepage}'
                             for packageName, packageLicense, packageHomepage in packagesData]
            formattedData = '\n'.join(formattedData) + '\n'
        return formattedData


PLATFORM_SYSTEM = QSysInfo.kernelType()
PLATFORM_MACOS = PLATFORM_SYSTEM == 'darwin'
PLATFORM_MENUS = PLATFORM_MACOS

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
        qml_path = Path(__file__).parent / 'Disclaimers.qml'
    else:
        qml_path = Path(__file__).parent / 'About.qml'
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    result = app.exec()

    if result != 0:
        print('ERROR: program exitted with code:', result)
        sys.exit(result)
