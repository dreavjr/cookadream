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
import atexit
import random
import sys
from pathlib import Path

import tensorflow as tf
from PySide6.QtCore import Property, QObject, QSettings, QSysInfo
from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QmlElement, QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

import style_rc  # pylint: disable=unused-import


compileSettings = len(sys.argv) > 1 and sys.argv[1] == '--compile'

appName = 'Preferences-Compile-' +str(random.randint(0, 10000000)) if compileSettings else 'Preferences-Demo'
settingsPath = Path.home() / 'Library' / 'Preferences' / f'com.eduardovalle.tests.{appName}.plist'
if settingsPath.exists():
    if compileSettings:
        print(f'ERROR: settings already found for {appName} in {settingsPath}', file=sys.stderr)
        sys.exit(1)
    else:
        print(f'WARNING: there are persistent settings for {appName} in {settingsPath}', file=sys.stderr)
if compileSettings:
    def clearSettings():
        if settingsPath.exists():
            print('ATTENTION! remember to delete settings file with the command below:')
            print('rm', settingsPath)
    atexit.register(clearSettings)

app = QApplication(sys.argv)

app.setOrganizationName('eduardovalle.com')
app.setOrganizationDomain('tests.eduardovalle.com')
app.setApplicationName(appName)
app.setApplicationVersion('0.1')

if compileSettings and QSettings().value('settings_internals/firstExecution'):
    print(f'ERROR: settings active for {appName} in preferences cache', file=sys.stderr)
    sys.exit(1)

# Application resources
applicationPath = Path(__file__).resolve(strict=True)
# imagesDir = applicationPath.parent / 'resources' / 'images'
applicationPath = Path(__file__).resolve(strict=True)
imagesDir = applicationPath.parent / 'resources' / 'images'
fontsDir = applicationPath.parent / 'resources' / 'fonts'
dataDir = applicationPath.parent / 'resources' / 'data'

# Load fonts
for typeface in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Medium.ttf", "Roboto-MediumItalic.ttf",
                 "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf",):
    fontPath = str(fontsDir / typeface)
    QFontDatabase.addApplicationFont(fontPath)


DEEP_DREAM_ENGINE_DEVICES = [d.name for d in tf.config.list_logical_devices()]

# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.dreamengine'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@QmlElement
class DreamEngineInfo(QObject):

    # --- Property DREAM_DEVICES (constant)
    @Property(list, constant=True)
    def DREAM_DEVICES(self):
        return list(DEEP_DREAM_ENGINE_DEVICES)

    # @Property(int, constant=True)
    # def DREAM_DEVICES(self):
    #     return 10

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
    rootContext.setContextProperty('COMPILE_SETTINGS', compileSettings)
    rootContext.setContextProperty('DIALOG_DEBUG', True)
    print('-- global symbols created')

    qml_path = Path(__file__).parent / 'Preferences.qml'
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    result = app.exec()

    if result != 0:
        print('ERROR: program exitted with code:', result)
        sys.exit(result)

    if compileSettings:
        def getTypeAndRepr(value):
            if isinstance(value, str):
                return 'string', value.__repr__()
            elif isinstance(value, list):
                return 'list', value.__repr__()
            elif isinstance(value, bool):
                return 'bool', str(value).lower()
            elif isinstance(value, int):
                return 'int', str(value)
            elif isinstance(value, float):
                return 'double', str(value)
            else:
                return 'var', value.__repr__()

        with open('GlobalSettings.qml', mode='wt', encoding='utf-8') as genFile:
            print('pragma Singleton', file=genFile)
            print('import QtQuick', file=genFile)
            print('', file=genFile)
            print('// THIS FILE WAS GENERATED AUTOMATICALLY:', file=genFile)
            print(f'// python {Path(__file__).name} --compile', file=genFile)
            print('', file=genFile)
            print('QtObject {', file=genFile)
            settings = QSettings()
            settings.beginGroup('settings_internals')
            for n in sorted(settings.childKeys()):
                if n == 'firstExecution':
                    continue
                v = settings.value(n)
                t, r = getTypeAndRepr(v)
                print('    readonly property %s internals_%s: %s' % (t, n, r), file=genFile)
            settings.endGroup()
            print('', file=genFile)
            settings.beginGroup('settings')
            for n in sorted(settings.childKeys()):
                v = settings.value(n)
                t, r = getTypeAndRepr(v)
                print('    readonly property %s %s: %s' % (t, n, r), file=genFile)
            settings.endGroup()
            print('}', file=genFile)

        with open('reset.temp.qml', mode='wt', encoding='utf-8') as genFile:
            print('// THIS FILE WAS GENERATED AUTOMATICALLY:', file=genFile)
            print(f'// python {Path(__file__).name} --compile', file=genFile)
            print('function reset() {', file=genFile)
            print("    console.debug('--')", file=genFile)
            settings.beginGroup('settings_internals')
            for n in sorted(settings.childKeys()):
                if n == 'firstExecution':
                    continue
                print('    %s = GlobalSettings.internals_%s' % (n, n), file=genFile)
            settings.endGroup()
            print('    // CUSTOM CODE HERE !', file=genFile)
            print('    internals.sync()', file=genFile)
            print('    settings.sync()', file=genFile)
            print('}', file=genFile)

        settings.clear()
