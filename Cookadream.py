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
# pylint: disable=wrong-import-order,wrong-import-position

# --- Minimal imports, application setup, and splash screen
import sys
from pathlib import Path, PurePath

from PySide6.QtGui import QFontDatabase, QIcon, QKeySequence, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from utils.version_info import PRODUCT_VERSION

appName = 'Cook-a-Dream'
app = QApplication(sys.argv)
app.setOrganizationName('eduardovalle.com')
app.setOrganizationDomain('eduardovalle.com')
app.setApplicationName(appName)
app.setApplicationVersion(PRODUCT_VERSION)

# Application resources
applicationPath = Path(__file__).resolve(strict=True)
applicationDir = applicationPath.parent
imagesDir = applicationDir / 'resources' / 'images'
fontsDir = applicationDir / 'resources' / 'fonts'
dataDir = applicationDir / 'resources' / 'data'
textDir = applicationDir / 'resources' / 'text'
examplesDir = applicationDir / 'resources' / 'examples'
qmlDir = applicationDir / 'gui'

# Application appearance
app.setWindowIcon(QIcon(str(imagesDir / 'application_icon.png')))
app.setApplicationDisplayName(appName)

# Load fonts
for typeface in ("Roboto-Regular.ttf", "Roboto-Italic.ttf", "Roboto-Medium.ttf", "Roboto-MediumItalic.ttf",
                 "Roboto-Bold.ttf", "Roboto-BoldItalic.ttf",):
    fontPath = str(fontsDir / typeface)
    QFontDatabase.addApplicationFont(fontPath)

# Show splash screen
splashPath = str(imagesDir / 'splash.jpg')
splashImg = QPixmap(splashPath)
splash = QSplashScreen(splashImg)
splash.show()

def splashShow(message):
    splash.showMessage(message)

splashShow('loading ui framework')

# --- Remaining imports
import atexit
import inspect
import logging
import os
import re
import tempfile
import traceback
from datetime import datetime

from PySide6.QtCore import (Property, QMutex, QObject, QRunnable, QSettings, QStandardPaths, QSysInfo, Qt, QThreadPool,
                            QtMsgType, QUrl, QWaitCondition, Signal, Slot, qInstallMessageHandler)
from PySide6.QtQml import QmlElement, QQmlApplicationEngine
from PySide6.QtQuick import QQuickImageProvider, QQuickItem
from PySide6.QtQuickControls2 import QQuickStyle

from utils import style_rc  # pylint: disable=unused-import

LOG_ERROR_LEVELS = ('debug', 'info', 'warning', 'error')
LOG_ERROR_LEVELS_PYTHON = tuple((getattr(logging, l.upper()) for l in LOG_ERROR_LEVELS))
LOG_ERROR_LEVELS_TF = ('0', '0', '1', '2') # Set to 3 to ommit all messages including error
LOG_ERROR_LEVEL_DEF = 'info' # Change to warning in final version
LOG_ERROR_LEVEL = os.environ.get('COOKADREAM_LOG_ERROR_LEVEL', LOG_ERROR_LEVEL_DEF)
if LOG_ERROR_LEVEL not in LOG_ERROR_LEVELS:
    print(f'WARNING: LOG_ERROR_LEVEL is not {LOG_ERROR_LEVELS} --- ignoring', file=sys.stderr)
    LOG_ERROR_LEVEL = LOG_ERROR_LEVEL_DEF
LOG_ERROR_LEVEL_PYTHON = LOG_ERROR_LEVELS_PYTHON[LOG_ERROR_LEVELS.index(LOG_ERROR_LEVEL)]
LOG_ERROR_LEVEL_TF = LOG_ERROR_LEVELS_TF[LOG_ERROR_LEVELS.index(LOG_ERROR_LEVEL)]

LOG_ERROR_MODES = ('debug', 'production')
LOG_ERROR_MODE_DEF = 'debug' # Change to production in final version
LOG_ERROR_MODE = os.environ.get('COOKADREAM_LOG_ERROR_MODE', LOG_ERROR_MODE_DEF)
if LOG_ERROR_MODE not in LOG_ERROR_MODES:
    print(f'WARNING: LOG_ERROR_MODE is not {LOG_ERROR_MODES} --- ignoring', file=sys.stderr)
    LOG_ERROR_MODE = LOG_ERROR_MODE_DEF

if LOG_ERROR_MODE == 'debug':
    logWrite = sys.stderr
    logRead = None
    logTFPath = None
else:
    logFileHandle, logPath = tempfile.mkstemp(suffix='.log', prefix='cookadream_main_')
    os.close(logFileHandle)
    logWrite = open(logPath, mode='w', encoding='utf-8', errors='replace')
    logRead  = open(logPath, mode='r', encoding='utf-8')
    print(logPath)
    def deleteLog():
        def discardException(routine):
            try:
                routine()
            except Exception as e: # pylint: disable=broad-except
                print('exception ignored in atexit.deleteLog():', str(e), sys.stderr)
        discardException(logWrite.close)
        discardException(logRead.close)
        discardException(lambda: os.unlink(logPath))
    atexit.register(deleteLog)

# os.environ.pop('TF_CPP_VLOG_FILENAME', None)
# os.environ.pop('TF_CPP_MIN_LOG_LEVEL', None)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = LOG_ERROR_LEVEL_TF

#... loads tensorflow and associate libraries
splashShow('loading ai framework')

import numpy as np  # pylint: disable=unused-import
import PIL.Image
import PIL.ImageOps
import PIL.ImageQt
import tensorflow as tf  # pylint: disable=unused-import

if LOG_ERROR_MODE == 'debug':
    LOG_FORMAT = '%(asctime)s: %(levelname)s %(filename)s..%(funcName)s:%(lineno)d] %(message)s'
else:
    LOG_FORMAT = '%(asctime)s: %(levelname)s %(pathname)s:%(lineno)d] %(message)s'

LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def configureLoggers():
    logFormat = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    # Reconfigure all existing "visible" log handlers (those streaming to stdout/stderr)
    for l in logging.root.manager.loggerDict.values():
        visibleHandlers = []
        priorityHandler = None
        for h in l.handlers if hasattr(l, 'handlers') else []:
            if isinstance(h, logging.StreamHandler) and h.stream.fileno() == sys.stderr.fileno():
                visibleHandlers.append(h)
                priorityHandler = h
            elif isinstance(h, logging.StreamHandler) and h.stream.fileno() == sys.stdout.fileno():
                visibleHandlers.append(h)
        if visibleHandlers:
            priorityHandler = priorityHandler or visibleHandlers[0]
            h = logging.StreamHandler(logWrite)
            h.setFormatter(logFormat)
            h.setLevel(priorityHandler.level)
            l.addHandler(h)
        for rh in visibleHandlers:
            l.removeHandler(rh)
    # Adds and returns a new handler for the cookadream module
    for newLoggerName in ('cookadream', 'deep_dream',):
        newLogger = logging.getLogger(newLoggerName)
        newLogger.setLevel(LOG_ERROR_LEVEL_PYTHON)
        h = logging.StreamHandler(logWrite)
        h.setFormatter(logFormat)
        newLogger.addHandler(h)

configureLoggers()
logger = logging.getLogger('cookadream')

def logAndFormatException(etype, evalue, trace):
    errorDescription = traceback.format_exception(etype, evalue, trace)
    logger.error('%s', '⏎'.join(errorDescription))
    errorDescription = traceback.format_exception_only(etype, evalue)[-1].strip()
    errorDescription = re.sub(r'\s+', ' ', errorDescription)
    return errorDescription

#... creates a handler for Qt logging
qtMessageLevels = {
    QtMsgType.QtDebugMsg    : 'DEBUG',
    QtMsgType.QtInfoMsg     : 'INFO',
    QtMsgType.QtWarningMsg  : 'WARNING',
    QtMsgType.QtCriticalMsg : 'CRITICAL',
    QtMsgType.QtFatalMsg    : 'FATAL',
}

if LOG_ERROR_LEVEL_PYTHON > logging.DEBUG:
    del qtMessageLevels[QtMsgType.QtDebugMsg]
if LOG_ERROR_LEVEL_PYTHON > logging.INFO:
    del qtMessageLevels[QtMsgType.QtInfoMsg]
if LOG_ERROR_LEVEL_PYTHON > logging.WARNING:
    del qtMessageLevels[QtMsgType.QtWarningMsg]

def qtMessageHandler(level, context, message):
    if 'Only binding to one of multiple key bindings' in message: # BUG: extraneous message of Qt6.22
        if LOG_ERROR_MODE != 'debug':
            return
    levelName = qtMessageLevels.get(level, None)
    if levelName is None:
        return
    # using old-style format so the same LOG_FORMAT may be used in both contexts
    filename = '<None>' if context.file is None else PurePath(context.file).name
    print(LOG_FORMAT % {
            'asctime': datetime.now().strftime(LOG_DATE_FORMAT), 'levelname': levelName, 'pathname': context.file,
            'filename': filename, 'funcName': context.function, 'lineno': context.line, 'message': message},
          file=logWrite)

qInstallMessageHandler(qtMessageHandler)

#  TODO: QLoggingCategory::setFilterRules(QStringLiteral("qt.qml.binding.removal.info=true"));
#  see: https://doc.qt.io/qt-6/qtqml-syntax-propertybinding.html
#  OBS: Apparently QLoggingCategory is not available in PySide6

logger.debug('loggers configured')


# --- initialization of backend AI engine
# deepdream code based upon these examples
# https://www.tensorflow.org/tutorials/generative/deepdream and
# https://www.tensorflow.org/tutorials/generative/style_transfer
# Licensed under the Apache License, Version 2.0
splashShow('initializing ai engine')

from deep_dream import DEEP_DREAM_ENGINE_DEVICES
from deep_dream import MIN_DIM as MINIMUM_DREAM_IMAGE_SIZE
from deep_dream import DeepDreamEngine

deepDreamEngine = DeepDreamEngine()

# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.dreamengine'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@QmlElement
class DreamEngineInfo(QObject):

    # --- Property DREAM_DEVICES (constant)
    @Property(list, constant=True)
    def DREAM_DEVICES(self): # pylint: disable=invalid-name
        return list(DEEP_DREAM_ENGINE_DEVICES)


# --- Multithreading infra-structure
splashShow('initializing ui')

from utils import about_info

about_info.configureAboutInfo(applicationObject=app, textDirPathObject=textDir)


# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.mainwindow'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

_NO_TASK_ID = -1
_FIRST_TASK_ID = 0
_SOURCE_IMAGE_TASK_ID = -1000

@QmlElement
class WorkerSignals(QObject):
    # This class is needed because QRunnable does not descend from QObject and cannot emit signals directly

    startedWorkerSignal = Signal(int, str, bool, name='started')
    stopWorkerSignal = Signal(int, name='stop')
    finishedWorkerSignal = Signal(int, object, bool, str, name='finished')
    progressWorkerSignal = Signal(int, float, dict, name='progress')
    newTaskMutex = QMutex()
    newTaskId = _FIRST_TASK_ID

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isStopped = False
        self._isFinished = False
        self._finishWait = QWaitCondition()
        self._finishMutex = QMutex()
        WorkerSignals.newTaskMutex.lock()
        self._taskId = WorkerSignals.newTaskId
        WorkerSignals.newTaskId += 1
        WorkerSignals.newTaskMutex.unlock()
        logger.debug('-- new taskId = %s', self._taskId)

    @Property(int, constant=True)
    def taskId(self):
        return self._taskId

    @Property(int, constant=True)
    def NO_TASK_ID(self): # pylint: disable=invalid-name
        return _NO_TASK_ID

    @Property(int, constant=True)
    def SOURCE_IMAGE_TASK_ID(self): # pylint: disable=invalid-name
        return _SOURCE_IMAGE_TASK_ID

    @Property(bool)
    def isStopped(self):
        return self._isStopped

    @Property(bool)
    def isFinished(self):
        return self._isFinished

    def _releaseWait(self):
        logger.debug('--')
        self._finishMutex.lock()
        self._isFinished = True
        self._finishMutex.unlock()
        self._finishWait.wakeAll()

    def wait(self):
        logger.debug('>>')
        self._finishMutex.lock()
        if self._isFinished:
            self._finishMutex.unlock()
        else:
            self._finishWait.wait(self._finishMutex)
        logger.debug('<<')

    def started(self, taskName='', *, keepProgress=False):
        '''Signal onStarted(taskId, taskName, keepProgress).'''
        logger.debug('--')
        self.startedWorkerSignal.emit(self.taskId, taskName, keepProgress)

    def stop(self):
        '''Signal onStop(taskId).'''
        logger.debug('--')
        self._isStopped = True
        self.stopWorkerSignal.emit(self.taskId)

    def finished(self, result=None, *, error=False, finalMessage=''):
        '''Signal onFinished(taskId, result, error, finalMessage).'''
        logger.debug('result is None = %s, error = %s, finalMessage = %s', result is None, error, finalMessage)
        self._releaseWait()
        self.finishedWorkerSignal.emit(self.taskId, result, error, finalMessage)

    def progress(self, fractionFinished, /, **kwargs):
        '''Signal onProgress(taskId, fractionFinished, kwargs), 0. <= fractionFinished <= 1.'''
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('fractionFinished = %s, kwargs.keys() = %s', fractionFinished, kwargs.keys())
        self.progressWorkerSignal.emit(self.taskId, fractionFinished, kwargs)

    def connectSelf(self, workerSignals):
        '''Connects signals of one instance to another of the same class.'''
        logger.debug('-- connect %s => %s', self._taskId, workerSignals._taskId)
        for signalAttr in dir(self):
            if signalAttr.endswith('WorkerSignal') and hasattr(workerSignals, signalAttr):
                getattr(self, signalAttr).connect(getattr(workerSignals, signalAttr))

    def connectSignal(self, signal, slot):
        '''Connects a particular signal to a slot.'''
        logger.debug('signal = %s, slot = %s', signal, slot)
        signalAttr = f'{signal}WorkerSignal'
        if hasattr(self, signalAttr):
            getattr(self, signalAttr).connect(slot)
        else:
            raise ValueError(f'unrecognized signal name: "{signal}"')

class Worker(QRunnable):

    def __init__(self, workerFunction, /, *args, taskName='', **kwargs):
        '''
        Creates a worker to run the function workerFunction with the given arguments. A new set of WorkerSignals is
        created for the worker in the public attribute signals. The optional argment taskName is forwarded to the
        start signal of the worker.

        The function workerFunction may have the parameters worker, signals, and either progressCallback or
        progress_callback, which receive, respectively, this worker object, the signals attribute of this worker object,
        and the signals.progress method of this worker object. The value returned by the function is sent as the result
        value in signals.finihed if the execution completes successfully. If the execution is stopped (as indicated by
        signals.isStopped) and the function returns a string, that string is sent as finalMessage in signals.finished.
        '''
        logger.debug('--')
        super().__init__()
        self.workerFunction = workerFunction
        self.args = args
        self.kwargs = kwargs
        self.taskName = taskName
        self.signals = WorkerSignals()

        functionParameters = inspect.signature(workerFunction).parameters
        if 'worker' in functionParameters:
            self.kwargs['worker'] = self
        if 'signals' in functionParameters:
            self.kwargs['signals'] = self.signals
        if 'progressCallback' in functionParameters:
            self.kwargs['progressCallback'] = self.signals.progress
            self.keepProgress = True
        elif 'progress_callback' in functionParameters:
            self.kwargs['progress_callback'] = self.signals.progress
            self.keepProgress = True
        else:
            self.keepProgress = False

    def run(self):
        '''Starts running workerFunction with parameters specified during Worker creation.'''
        try:
            logger.debug('>>')
            self.signals.started(self.taskName, keepProgress=self.keepProgress)
            if self.keepProgress:
                self.signals.progress(0.)
            result = self.workerFunction(*self.args, **self.kwargs)
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            self.signals.finished(error=True, finalMessage=f'error: "{errorDescription}"')
            logger.debug('<< exception')
        else:
            if self.signals.isStopped: # pylint: disable=using-constant-test
                finalMessage = result if isinstance(result, str) \
                                  else 'the execution was halted before completion'
                self.signals.finished(error=True, finalMessage=finalMessage)
                logger.debug('<< stopped')
            else:
                self.signals.finished(result)
                logger.debug('<< success')

globalThreadPool = QThreadPool.globalInstance()

#  --- Supported image formats
DEFAULT_SUFFIX = '.jpg'
OPEN_SUFFIXES = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.pbm', '.pgm', '.ppm'}
SAVE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.ppm'}
OPEN_FILTERS = ['All image files (*.jpg *.jpeg *.bmp *.gif *.png *.pbm *.pgm *.ppm)', 'JPEG Images (*.jpg *.jpeg)',
                'BMP Images (*.bmp)', 'GIF Images (*.gif)', 'PNG Images (*.png)',
                'Portable Bitmap PBM Images (*.pbm)', 'Portable Graymap PGM Images (*.pgm)',
                'Portable Pixelmap PPM Images (*.ppm)']
SAVE_FILTERS = ['All image files (*.jpg *.jpeg *.bmp *.gif *.png *.ppm)', 'JPEG Images (*.jpg *.jpeg)',
                'BMP Images (*.bmp)', 'GIF Images (*.gif)', 'PNG Images (*.png)',
                'Portable Pixelmap PPM Images (*.ppm)']

TRANSPARENT_BACKGROUND = (255, 255, 255,)

#  --- Global clipboard object
clipboard = app.clipboard()

# --- Python-QML bridge element for main window

@QmlElement
class BridgeMainWindow(QObject):
    '''This object bridges the UI functionality to the AI backend.'''

    def __init__(self, *args, **kwargs):
        logger.debug('--')
        super().__init__(*args, **kwargs)
        self._ready = False
        self._dreamMutex = QMutex()
        self._dreamSaved = None
        self._hasImage = False
        self._worker = None
        self._taskId = _NO_TASK_ID
        self._originalImage = None

    # --- Properties .busy, .taskId (read-only, from private property _worker)
    busyChanged = Signal(name='busyChanged')
    taskIdChanged = Signal(name='taskIdChanged')

    def busyGet(self):
        return self._worker is not None

    def taskIdGet(self):
        return _NO_TASK_ID if self._worker is None else self._worker.signals.taskId

    def _workerSet(self, worker):
        wasBusy = self.busyGet()
        oldTaskId = self.taskIdGet()
        self._worker = worker
        if wasBusy != self.busyGet():
            self.busyChanged.emit()
        if oldTaskId != self.taskIdGet():
            self.taskIdChanged.emit()

    busy = Property(bool, busyGet, notify=busyChanged)
    taskId = Property(int, taskIdGet, notify=taskIdChanged)

    # --- Property .ready (read-only, protected write)
    readyChanged = Signal(name='readyChanged')

    def readyGet(self):
        return self._ready

    def _readySet(self, ready):
        if self._ready != ready:
            self._ready = ready
            self.readyChanged.emit()

    ready = Property(bool, readyGet, notify=readyChanged)

    # --- Property .saved (public read, protected write)
    savedChanged = Signal(name='savedChanged')

    def savedGet(self):
        return self._dreamSaved is None or self._dreamSaved

    def _savedSet(self, saved):
        if self._dreamSaved != saved:
            self._dreamSaved = saved
            self.savedChanged.emit()

    saved = Property(bool, savedGet, notify=savedChanged)

    # --- Property .hasImage (public read, protected write)
    hasImageChanged = Signal(name='hasImageChanged')

    def hasImageGet(self):
        return self._hasImage is None or self._hasImage

    def _hasImageSet(self, hasImage):
        if self._hasImage != hasImage:
            self._hasImage = hasImage
            self.hasImageChanged.emit()

    hasImage = Property(bool, hasImageGet, notify=hasImageChanged)

    # --- Property .clipboardHasImage (read-only)
    clipboardHasImageChanged = Signal(name='clipboardHasImageChanged')

    def clipboardHasImageGet(self):
        global clipboard
        image = clipboard.image()
        return image is not None and not image.isNull()

    clipboardHasImage = Property(bool, clipboardHasImageGet, notify=clipboardHasImageChanged)

    # --- Window initialziation
    @Slot(QQuickItem)
    def interfaceReady(self, imageView):
        global splash, neuralImageBridge, deepDreamEngine, clipboard
        logger.debug('>>')
        splash.hide()
        neuralImageBridge.connectSignal('imageChanged', imageView.neuralRefresh)
        clipboard.dataChanged.connect(self.clipboardHasImageChanged)
        logger.debug('<<')

    @Slot(WorkerSignals, str, str, str, int, int, int, bool)
    def loadAiEngine(self, workerSignals, deviceName, modelModuleName, layerName, neuronFrom, neuronTo, imagenetLabel,
                     tiledRendering):
        logger.debug('>>')
        # If the engine is busy does nothing
        if self.busy:
            return
        self._readySet(False)
        if layerName == 'predictions':
            if imagenetLabel == -1 :
                neuronFrom = 0
                neuronTo = 999
            else:
                neuronFrom = neuronTo = imagenetLabel
        setupKwargs = dict(device_name=deviceName, model_name=modelModuleName, layer_name=layerName,
                           neuron_first=neuronFrom, neuron_last=neuronTo, tiled_rendering=tiledRendering)
        logger.debug('-- %s', setupKwargs)
        initWorker = Worker(deepDreamEngine.setup, taskName='loading ai model', **setupKwargs)
        initWorker.signals.connectSelf(workerSignals)
        initWorker.signals.connectSignal('finished', self.finishedSetup)
        self._workerSet(initWorker)
        globalThreadPool.start(initWorker)
        logger.debug('<<')

    @Slot(int, object, bool, str)
    def finishedSetup(self, _taskId, _result, _error, _message):
        logger.debug('--')
        self._workerSet(None)
        self._readySet(True)

    # --- Drag n' drop
    @Slot(list, result=str)
    def checkDragAndDrop(self, uris):
        if not self._ready:
            return ''
        if len(uris) != 1:
            return ''
        uri = uris[0]
        if not uri.isLocalFile():
            return ''
        # https://stackoverflow.com/questions/5977576/is-there-a-convenient-way-to-map-a-file-uri-to-os-path
        path = PurePath(uri.toLocalFile())
        if path.suffix.lower() in OPEN_SUFFIXES:
            return str(path)
        return ''

    # --- URL to path conversion
    @Slot(str, result=str)
    def urlToPath(_self, url):
        return str(PurePath(QUrl(url).toLocalFile()))

    # --- Main functionality
    @Slot(WorkerSignals, int, int, float, int, float, float, float, int)
    def startDreaming(self, workerSignals, octavesFrom, octavesTo, octavesScaling, stepsPerOctave, octavesBlending,
                      stepSize, smoothingFactor, jitterPixels):
        global neuralImageBridge, deepDreamEngine
        logger.debug('--')
        # If the engine is not ready, or if an image is not available, does nothing
        if not (self.ready and self.hasImage):
            return
        # If a dream is ongoing, stops it
        self.stopDreaming()
        # Starts a new dream
        pixmap = neuralImageBridge.getRawPixmap()
        imagePillow = PIL.ImageQt.fromqpixmap(pixmap)
        #... the internal notion of "octaves" is the opposite of the more user-friendly notion used in the interface
        #... the user-friendly octaves_scaling is on a logarithmic scale
        dreamKwargs = dict(octaves=range(-octavesTo, -octavesFrom + 1), octaves_scaling=2.**octavesScaling,
                           octaves_blending=octavesBlending/100., steps_per_octave=stepsPerOctave, step_size=stepSize,
                           smoothing_factor=-smoothingFactor, jitter_pixels=jitterPixels)
        logger.debug('-- %s', dreamKwargs)
        self._workerSet(Worker(deepDreamEngine.dream, imagePillow, dream_kwargs=dreamKwargs,
                               taskName='dreaming — this may take a while...'))
        self._worker.setAutoDelete(False)
        self._worker.signals.connectSelf(workerSignals)
        self._worker.signals.connectSignal('progress', self.updateImage)
        self._worker.signals.connectSignal('finished', self.finishedImage)
        globalThreadPool.start(self._worker)

    @Slot()
    def stopDreaming(self):
        taskId = self.taskId
        logger.debug('>> taskId = %s from worker = %s', taskId, self._worker)
        self._dreamMutex.lock()
        if self._worker is not None and self.taskId == taskId:
            self._worker.signals.stop()
            self._worker.signals.wait()
            self._workerSet(None)
        self._dreamMutex.unlock()
        logger.debug('<< self._worker = %s', self._worker)

    @Slot(int, float, dict)
    def updateImage(self, taskId, _fractionFinished, kwargs):
        global neuralImageBridge
        if  'image_array' in kwargs and self.taskId == taskId:
            logger.debug('-- taskId = %s', taskId)
            neuralImageBridge.setSourceFromArray(kwargs['image_array'], taskId=taskId)
            self._savedSet(False)
            self._hasImageSet(True)

    @Slot(object, bool, str)
    def finishedImage(self, taskId, _result, _error, _finalMessage):
        logger.debug('>> taskId = %s', taskId)
        self._dreamMutex.lock()
        if self.taskId == taskId:
            self._workerSet(None)
        self._dreamMutex.unlock()
        logger.debug('<< %s', taskId)

    # --- Other actions
    @Property(list, constant=True)
    def DEFAULT_SUFFIX(self): # pylint: disable=invalid-name
        return DEFAULT_SUFFIX

    @Property(list, constant=True)
    def OPEN_IMAGE_FILTERS(self): # pylint: disable=invalid-name
        return OPEN_FILTERS

    @Property(list, constant=True)
    def SAVE_IMAGE_FILTERS(self): # pylint: disable=invalid-name
        return SAVE_FILTERS

    @staticmethod
    def _enforceRGB(imagePillow):
        if imagePillow.mode == 'RGB':
            return imagePillow
        if imagePillow.mode == 'RGBA':
            background = PIL.Image.new('RGBA', imagePillow.size, color=TRANSPARENT_BACKGROUND)
            imagePillow = PIL.Image.alpha_composite(background, imagePillow)
        logger.debug('-- %s => RGB', imagePillow.mode)
        return imagePillow.convert('RGB')

    @Slot(float, float, int, result=list)
    def newImage(self, width, height, maximumSize):
        '''Returns list(4): success(bool), width(int), height(int), Image or error message.'''
        global neuralImageBridge, deepDreamEngine
        try:
            # If a dream is ongoing, stops it
            self.stopDreaming()
            logger.debug('width = %s, height = %s, maximumSize = %s', width, height, maximumSize)
            width  = max(int(np.round(width)),  MINIMUM_DREAM_IMAGE_SIZE)
            height = max(int(np.round(height)), MINIMUM_DREAM_IMAGE_SIZE)
            if maximumSize > 0:
                width  = min(width, maximumSize)
                height = min(height, maximumSize)
            imageArray = DeepDreamEngine.noise_to_image_array(DeepDreamEngine.get_noise_array(width, height))
            imagePillow = PIL.Image.fromarray(imageArray)
            self._originalImage = imagePillow
            neuralImageBridge.setSourceFromPillow(imagePillow)
            self._hasImageSet(True)
            self._savedSet(True)
            return [True, imagePillow.size[0], imagePillow.size[1], imagePillow]
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            self._hasImageSet(False)
            return [False, 0, 0, errorDescription]

    @Slot(str, int, result=list)
    def openImage(self, path, maximumSize):
        '''Returns list(4): success(bool), width(int), height(int), Image or error message.'''
        global neuralImageBridge, deepDreamEngine
        try:
            # If a dream is ongoing, stops it
            self.stopDreaming()
            logger.debug('path = "%s", maximumSize = %s', path, maximumSize)
            imageSuffix = PurePath(path).suffix.lower()
            if imageSuffix not in OPEN_SUFFIXES:
                self._hasImageSet(False)
                return [False, 0, 0, f'unrecognized image format: "{imageSuffix}"']
            image = PIL.Image.open(path)
            image = PIL.ImageOps.exif_transpose(image)
            image = self._enforceRGB(image)
            if maximumSize > 0:
                image = DeepDreamEngine.fit_image(image, max_dim=maximumSize)
            self._originalImage = image
            neuralImageBridge.setSourceFromPillow(image)
            self._hasImageSet(True)
            self._savedSet(True)
            return [True, image.size[0], image.size[1], image]
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            self._hasImageSet(False)
            return [False, 0, 0, errorDescription]

    @Slot(int, result=list)
    def pasteImage(self, maximumSize):
        global neuralImageBridge, deepDreamEngine, clipboard
        try:
            # If a dream is ongoing, stops it
            self.stopDreaming()
            image = clipboard.image()
            logger.debug('-- image = %s, maximumSize = %s', image, maximumSize)
            if image is None or image.isNull():
                return [None, 0, 0, 'no image available in clipboard']
            image = PIL.ImageQt.fromqpixmap(image)
            image = self._enforceRGB(image)
            if maximumSize > 0:
                image = DeepDreamEngine.fit_image(image, max_dim=maximumSize)
            self._originalImage = image
            neuralImageBridge.setSourceFromPillow(image)
            self._hasImageSet(True)
            self._savedSet(False)
            return [True, image.size[0], image.size[1], image]
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            self._hasImageSet(False)
            return [False, 0, 0, errorDescription]

    @Slot(result=list)
    def restoreImage(self):
        global neuralImageBridge, deepDreamEngine, clipboard
        try:
            # If a dream is ongoing, stops it
            self.stopDreaming()
            image = self._originalImage
            logger.debug('-- image = %s', image)
            if image is None:
                return [None, 0, 0, 'no image to restore to']
            neuralImageBridge.setSourceFromPillow(image)
            self._hasImageSet(True)
            self._savedSet(False)
            return [True, image.size[0], image.size[1], image]
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            self._hasImageSet(False)
            return [False, 0, 0, errorDescription]

    @Slot(str, int, result=str)
    def saveImage(self, path, quality):
        '''Quality is an integer in [0, 100] or -1 for Qt default. Returns str: error message ("" if ok).'''
        try :
            logger.debug('path = "%s"', path)
            pixmap = neuralImageBridge.getRawPixmap()
            imageSuffix = PurePath(path).suffix.lower()
            if imageSuffix not in SAVE_SUFFIXES:
                return f'unrecognized image format: "{imageSuffix}"'
            pixmap.save(path, quality=quality)
            self._savedSet(True)
            return ''
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            errorDescription = logAndFormatException(etype, evalue, trace)
            return errorDescription

    @Slot(result=bool)
    def copyImage(self):
        global neuralImageBridge, clipboard
        try:
            image = neuralImageBridge.getRawPixmap().toImage()
            clipboard.setImage(image)
            logger.debug('copy ok, image = %s', image)
            return True
        except Exception: # pylint: disable=broad-except
            etype, evalue, trace = sys.exc_info()
            _errorDescription = logAndFormatException(etype, evalue, trace)
            return False

# --- Dynamic image provider for Main window

class NeuralImageBridge(QQuickImageProvider):

    imageChangedSignal = Signal(int, name = 'imageChanged')

    def __init__(self, flags=None):
        logger.debug('--')
        if flags is None:
            super().__init__(QQuickImageProvider.ImageType.Pixmap)
        else:
            super().__init__(QQuickImageProvider.ImageType.Pixmap, flags=flags)
        self.currentPixmap = None
        self.currentWidth = None
        self.currentHeight = None
        self.taskId = _NO_TASK_ID

    def _updatePixmap(self, pixmap, taskId):
        logger.debug('taskId = %s', taskId)
        self.currentPixmap = pixmap
        self.currentWidth  = pixmap.width()
        self.currentHeight = pixmap.height()
        self.taskId = taskId
        self.imageChanged()

    def setSourceFromPath(self, imagePath, /, *, taskId=_SOURCE_IMAGE_TASK_ID):
        self._updatePixmap(QPixmap(imagePath), taskId=taskId)

    def setSourceFromPillow(self, imagePillow, /, *, taskId=_SOURCE_IMAGE_TASK_ID):
        self._updatePixmap(PIL.ImageQt.toqpixmap(imagePillow), taskId=taskId)

    def setSourceFromArray(self, imageArray, /, *, taskId=_SOURCE_IMAGE_TASK_ID):
        imagePillow = PIL.Image.fromarray(imageArray)
        self._updatePixmap(PIL.ImageQt.toqpixmap(imagePillow), taskId=taskId)

    def setSourceFromPixmap(self, pixmap, /, *, taskId=_SOURCE_IMAGE_TASK_ID):
        self._updatePixmap(pixmap, taskId=taskId)

    def requestPixmap(self, imageId, size, requestedSize):
        if self.currentPixmap is None:
            raise ValueError('no image available in image bridge!')
        if not imageId.startswith('current/'):
            raise ValueError(f'unrecognized image requested: {imageId}')
        size.width  = self.currentWidth
        size.height = self.currentHeight
        requestedWidth  = requestedSize.width()
        requestedHeight = requestedSize.height()
        width  = requestedWidth  if requestedWidth>0  else self.currentWidth
        height = requestedHeight if requestedHeight>0 else self.currentHeight
        scaledPixmap =  self.currentPixmap.scaled(width, height, mode=Qt.SmoothTransformation)
        logger.debug('id: "%s", requestedSize: %s, width: %s, height: %s, scaled: %s',
                     imageId, requestedSize, width, height, scaledPixmap)
        return scaledPixmap

    def getRawPixmap(self):
        logger.debug('--')
        if self.currentPixmap is None:
            raise ValueError('no image available in image bridge!')
        return self.currentPixmap

    def connectSignal(self, signal, slot):
        '''Connects a particular signal to a slot'''
        if signal == 'imageChanged':
            self.imageChangedSignal.connect(slot)
        else:
            raise ValueError(f'unrecognized signal name: "{signal}"')

    def imageChanged(self):
        logger.debug('--')
        self.imageChangedSignal.emit(self.taskId)

neuralImageBridge = NeuralImageBridge()

# --- Menu source translations to uniformize platform and Qt menus

def validateOverride(override):
    override = override.upper()
    if override in ('YES', 'Y', 'NO', 'N'):
        return override[0]
    else:
        return ''
UNIVERSAL_THEME_OVERRIDE = validateOverride(os.environ.get('COOKADREAM_UNIVERSAL_THEME', ''))
PLATFORM_MENUS_OVERRIDE  = validateOverride(os.environ.get('COOKADREAM_PLATFORM_MENUS', ''))
NATIVE_MENUS_SHORTCUTS   = validateOverride(os.environ.get('COOKADREAM_MENU_SHORTCUTS', 'Y'))

PLATFORM_SYSTEM = QSysInfo.kernelType()
PLATFORM_VERSION = QSysInfo.kernelType()
PLATFORM_MACOS = PLATFORM_SYSTEM == 'darwin'
PLATFORM_WIN10 = PLATFORM_SYSTEM == 'winnt' and PLATFORM_VERSION >= '10.'
PLATFORM_MENUS = (PLATFORM_MENUS_OVERRIDE == 'Y') if PLATFORM_MENUS_OVERRIDE else (PLATFORM_MACOS or PLATFORM_WIN10)
CONTROLS_THEME = ('Material' if UNIVERSAL_THEME_OVERRIDE == 'N' or (UNIVERSAL_THEME_OVERRIDE == '' and PLATFORM_MACOS)
                             else 'Universal')

# To be used on the @QmlElement decorator
QML_IMPORT_NAME = 'cookadream.dynamicmenus'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@QmlElement
class KeySequences(QObject):
    '''This ancillary element is to solve the problem of missing key shortcuts in QML non-native menus.'''
    @Slot(int, result=str)
    @Slot(str, result=str)
    def get(self, sequence):
        if isinstance(sequence, int):
            sequence = QKeySequence.StandardKey(sequence)
        sequence = QKeySequence(sequence)
        native = sequence.toString(QKeySequence.SequenceFormat.NativeText)
        return native

    @Slot(int, result=str)
    @Slot(str, result=str)
    def inMenu(self, sequence):
        if isinstance(sequence, str) and sequence=='':
            return ''
        shortcut_text = self.get(sequence)
        if shortcut_text == '':
            return ''
        return  f' <i>{shortcut_text}</i>'

def openUTF8Resource(resourcePath, lines=False):
    with open(resourcePath, 'rt', encoding='utf-8') as resourceFile:
        resource = resourceFile.readlines() if lines else resourceFile.read()
    return resource

def qmlProcessMenu(menuSource, platform, platformPrefix='QtPl.', qtPrefix='', sequenceGetter='mksq'):
    '''Processes menu source, using or not platform version.'''
    if platform:
        menuSource = re.sub(r'action:\s*([A-Za-z0-9_]+)',
                            r'QtPl.MenuItem { text: \1.text; shortcut: \1.shortcut; checkable: \1.checkable; '
                            r'checked: \1.checked; enabled: \1.enabled; onTriggered: \1.trigger() }', menuSource)
        importPrefix = platformPrefix
        menuElement = 'Menu'
        openFunction = 'open'
    else:
        if sequenceGetter:
            replacement  = r'MenuItem { text: \1.text + '
            replacement += sequenceGetter + r'.inMenu(\1.shortcut ? \1.shortcut  : ""); action: \1 }'
        else:
            replacement = r'MenuItem { action: \1 }'
        menuSource = re.sub(r'action:\s*([A-Za-z0-9_]+)', replacement, menuSource)
        importPrefix = qtPrefix
        menuElement = 'MenuFit'
        openFunction = 'popup'
    menuSource = re.sub(r'^\s*@\.', importPrefix, menuSource, flags=re.MULTILINE)
    menuSource = re.sub(r'<Menu>', menuElement, menuSource)
    menuSource = re.sub(r'{([\t ]*\n)*[\t ]*', '{ ', menuSource)
    menuSource = re.sub(r'}([\t ]*\n)*[\t ]*', '} ', menuSource)
    menuSource = re.sub(r'([\t ]*\n)+[\t ]*', '; ', menuSource)
    return menuSource, openFunction

def qmlTranslateAllMenus(qmlSource, menuPathPrefix, platform, sequenceGetter='mksq'):
    for menuType in ('menubar', 'menucontext',):
        qmlMenuPath = menuPathPrefix + f'-{menuType}.qml'
        qmlMenuSource = openUTF8Resource(qmlMenuPath)
        qmlMenuSource, openFunction = qmlProcessMenu(qmlMenuSource, platform=platform, sequenceGetter=sequenceGetter)
        if menuType == 'menubar' and not platform:
            qmlMenuSource = f'menuBar: {qmlMenuSource}'
        qmlSource = qmlSource.replace(f'//<<<application_{menuType}>>>//', qmlMenuSource)
        qmlSource = qmlSource.replace(f'application_{menuType}_open_function', openFunction)
    return qmlSource

# --- main routine
def main():
    # registers application fonts

    # prepares the application
    # app = QGuiApplication(sys.argv)
    # see https://doc.qt.io/qt-6/qtquickcontrols2-configuration.html
    QQuickStyle.setStyle(CONTROLS_THEME)
    engine = QQmlApplicationEngine()
    logger.debug('theme = "%s", engine = "%s"', CONTROLS_THEME, engine)
    logger.debug('name = "%s", displayName = "%s"', app.applicationName(), app.applicationDisplayName())

    # registers image provider
    engine.addImageProvider('neural_images', neuralImageBridge)

    # initialize open and save document paths with defaults
    settings = QSettings()
    settings.beginGroup('document_paths')
    examplesUri = examplesDir.as_uri()
    openFolderUri = settings.value('openFolderUri') or examplesUri
    settings.setValue('openFolderUri', openFolderUri)
    picturesDir = Path(QStandardPaths.writableLocation(QStandardPaths.PicturesLocation))
    picturesUri = picturesDir.as_uri()
    saveFolderUri = settings.value('saveFolderUri') or picturesUri
    settings.setValue('saveFolderUri', saveFolderUri)
    settings.endGroup()

    # Adds global symbols to QML
    rootContext = engine.rootContext()
    imagesUri = imagesDir.as_uri()
    rootContext.setContextProperty('IMAGES_URI', imagesUri)
    dataUri = dataDir.as_uri()
    rootContext.setContextProperty('DATA_URI', dataUri)
    rootContext.setContextProperty('CONTROLS_THEME', CONTROLS_THEME)
    rootContext.setContextProperty('COMPILE_SETTINGS', False)
    rootContext.setContextProperty('DIALOG_DEBUG', False)
    logger.debug('-- global symbols created')

    if not settings.value('settings/st_firstExecutionAccepted', False):
        qmlPath = qmlDir / 'Disclaimers.qml'
        engine.load(qmlPath.as_uri())
        splash.hide()
        app.exec()
    settings.sync()
    if not settings.value('settings/st_firstExecutionAccepted', False):
        return -1

    # opens the QML source and applies necessary translations
    qmlPath = qmlDir / 'Cookadream.qml'
    qmlSource = openUTF8Resource(qmlPath)
    qmlSource = qmlTranslateAllMenus(qmlSource, str(qmlPath.with_suffix('')), platform=PLATFORM_MENUS,
                                     sequenceGetter = '' if NATIVE_MENUS_SHORTCUTS == 'N' else 'mksq')
    # qmlTarget = qmlDir / 'translated_source.qml'
    # with open(qmlTarget , 'wt', encoding='utf-8') as debugSorce:
    #     print(qmlSource, file=debugSorce)
    logger.debug('-- QML source translated')

    # loads the QML engine
    qmlSource = qmlSource.encode()
    qmlPathToEngine = qmlPath.as_uri()
    engine.loadData(qmlSource, url=qmlPathToEngine)
    rootObjects = engine.rootObjects()
    if not rootObjects:
        sys.exit(-1)
    logger.debug('-- ui loaded')

    # runs the GUI
    logger.debug('>> app.exec')
    status = app.exec()
    logger.debug('<< app.exec')
    return status

if __name__ == '__main__':
    sys.exit(main())
