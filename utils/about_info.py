import pkg_resources

from PySide6.QtCore import (Property, QMimeData, QObject, QSysInfo, Signal, Slot)
from PySide6.QtQml import QmlElement

from .version_info import PRODUCT_COMMIT, PRODUCT_VERSION

appName = None
textDir = None
clipboard = None

def configureAboutInfo(applicationObject, textDirPathObject):
    global appName, textDir, clipboard
    appName = applicationObject.applicationName()
    textDir = textDirPathObject
    clipboard = applicationObject.clipboard()

# --- Python-QML bridge element for about window

# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.aboutinfo'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

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
