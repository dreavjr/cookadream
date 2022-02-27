/* ===================================================================================================================
   Copyright 2022 Eduardo Valle.

   This file is part of Cook-a-Dream.

   Cook-a-Dream is free software: you can redistribute it and/or modify it under the terms of the version 3 of the GNU
   General Public License as published by the Free Software Foundation.

   Cook-a-Dream is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with Cook-a-Dream. If not, see
   https://www.gnu.org/licenses.
   ================================================================================================================== */
import QtQuick 6.2
import QtQuick.Controls 6.2
import QtQuick.Window 6.2
import Qt.labs.platform as QtPl
import Qt.labs.settings 6.2

import cookadream.mainwindow 1.0
import cookadream.dynamicmenus 1.0


ApplicationWindow {
    // --- Basic properties
    id: mainwindow
    width: Constants.defaultWidth
    height: Constants.defaultHeight
    visible: true
    title: qsTr('Cook-a-Dream')

    // --- Window state persistence
    Settings {
        category: 'mainwindow'
        property alias x: mainwindow.x
        property alias y: mainwindow.y
        property alias width: mainwindow.width
        property alias height: mainwindow.height
    }

    // --- Settings - Persistence
    Settings {
        category: 'settings_internals'
        property alias dreamImmediate: immediateaction.checked
        property alias overwriteConfirmation: overwriteaction.checked
    }

    // --- Settings - Global UI-Indepentent Values
    Settings {
        id: settings
        category: 'settings'
        readonly property bool dreamImmediate: immediateaction.checked
        readonly property bool overwriteConfirmation: overwriteaction.checked
    }

    // --- Settings - Open and Save Paths
    // Settings {
    //     category: 'document_paths'
    //     property alias openFolderUri: opendialog.folder
    //     property alias saveFolderUri: savedialog.folder
    // }

    Settings {
        id: settingspaths
        category: 'document_paths'
        property string openFolderUri
        property string saveFolderUri
    }

    readonly property real extraHeight: (height-contentItem.height)
    readonly property real extraWidth: (width-contentItem.width)
    readonly property real imageHeight: contentItem.height
    readonly property real imageWidth: contentItem.width

    function resize(w, h) {
        let W = Screen.desktopAvailableWidth
        let H = Screen.desktopAvailableHeight
        console.debug('desktop =', W, H, 'chosen size =', w, h, 'extra =', extraWidth, extraHeight)
        w += extraWidth
        h += extraHeight
        // if image does not fit, computes the maximum size with right ratio
        if (w > W || h > H) {
            if (h/w > H/W) {
                w = H * w/h
                h = H
            }
            else {
                h = W * h/w
                w = W
            }
        }
        // tries to keep mid-point horizontal position in same place
        let wDelta = w - mainwindow.width
        w = Math.max(Constants.minimumWindowSize, w)
        h = Math.max(Constants.minimumWindowSize, h)
        mainwindow.x = Math.max(0, mainwindow.x - Math.trunc(wDelta / 2))
        // tries to keep top title bar in same place
        mainwindow.y = Math.min(mainwindow.y, H-h)
        mainwindow.width = w
        mainwindow.height = h
        console.debug('computed size =', w, h, 'new size =', mainwindow.width, mainwindow.height)
    }

    // --- Main connections
    BridgeMainWindow {
        id: bridge
    }

    property bool mainwindowReady: false

    onAfterAnimating: {
        if (!mainwindowReady) {
            console.debug('>>')
            console.debug(Constants.defaultWidth, Constants.defaultHeight, mainwindow.width, mainwindow.height)
            statusprogress.contentItem.color = Qt.binding(function(){ return Constants.busyColor })
            mainwindowReady = true
            bridge.interfaceReady(imageview)
            reloadaiengineaction.trigger()
            console.debug('<<')
        }
    }

    WorkerSignals {
        id: mainsignals
    }

    // --- UI Actions and menus
    // Used accelerators: a c d e f h i k l n m o p q r s w x
    KeySequences {
        id: mksq
    }

    Action {
        id: dreamaction
        text: qsTr('&Dream')
        shortcut: "Return"
        enabled: (bridge.hasImage && !bridge.busy)
        onTriggered: bridge.startDreaming(mainsignals,
                                          settings.value('st_dreamOctavesFrom', GlobalSettings.st_dreamOctavesFrom),
                                          settings.value('st_dreamOctavesTo',   GlobalSettings.st_dreamOctavesTo),
                                          settings.value('st_octavesScaling',   GlobalSettings.st_octavesScaling),
                                          settings.value('st_stepsPerOctave',   GlobalSettings.st_stepsPerOctave),
                                          settings.value('st_octavesBlending',  GlobalSettings.st_octavesBlending),
                                          settings.value('st_dreamSpeed',       GlobalSettings.st_dreamSpeed),
                                          settings.value('st_dreamSmoothing',   GlobalSettings.st_dreamSmoothing),
                                          settings.value('st_dreamShaking',     GlobalSettings.st_dreamSmoothing))
    }
    Action {
        id: stopaction
        text: qsTr('&Halt Dreaming')
        shortcut: StandardKey.Cancel
        enabled: bridge.ready && bridge.busy
        onTriggered: bridge.stopDreaming()
    }
    Action {
        id: restoreaction
        text: qsTr('&Restore Original Image')
        shortcut: StandardKey.Refresh
        enabled: (bridge.hasImage && !bridge.busy)
        onTriggered: maybeOpenImage('restore://')
    }
    Action {
        id: immediateaction
        text: qsTr('Start Dream &Immediately')
        checkable: true
        checked: true
        enabled: true
    }
    Action {
        id: overwriteaction
        text: qsTr('Confirm Before Dream Over&write')
        checkable: true
        checked: true
        enabled: true
    }
    Action {
        id: copyaction
        text: qsTr('&Copy')
        shortcut: StandardKey.Copy
        enabled: bridge.hasImage
        onTriggered: bridge.copyImage()
    }
    Action {
        id: pasteaction
        text: qsTr('&Paste')
        shortcut: StandardKey.Paste
        enabled: (bridge.ready && bridge.clipboardHasImage)
        onTriggered: maybeOpenImage('clipboard://')
    }
    Action {
        id: newaction
        text: qsTr('&New From Noise')
        shortcut: StandardKey.New
        enabled: bridge.ready
        onTriggered: maybeOpenImage('new://')
    }
    Action {
        id: openaction
        text: qsTr('&Open...')
        shortcut: StandardKey.Open
        enabled: bridge.ready
        onTriggered: {
            opendialog.folder = settingspaths.openFolderUri;
            opendialog.saveFolderOnClose = true;
            console.debug('opendialog.folder =', opendialog.folder,
                          'settingspaths.openFolderUri =', settingspaths.openFolderUri)
            opendialog.open()
        }
    }
    Action {
        id: exampleaction
        text: qsTr('Open E&xample...')
        enabled: bridge.ready
        onTriggered: {
            opendialog.folder = EXAMPLES_URI;
            opendialog.saveFolderOnClose = false;
            console.debug('opendialog.folder =', opendialog.folder,
                          'settingspaths.openFolderUri =', settingspaths.openFolderUri)
            opendialog.open()
        }
    }
    Action {
        id: saveaction
        text: qsTr('&Save As...')
        shortcut: StandardKey.Save
        enabled: bridge.hasImage
        onTriggered: {
            savedialog.folder = settingspaths.saveFolderUri;
            console.debug('savedialog.folder =', savedialog.folder,
                          'settingspaths.saveFolderUri =', settingspaths.saveFolderUri)
            savedialog.open()
        }
    }
    Action {
        id: preferencesaction
        text: qsTr('Pre&ferences...')
        shortcut: StandardKey.Preferences
        enabled: true
        onTriggered: { preferences.show(); preferences.raise(); preferences.requestActivate() }
    }
    Action {
        id: reloadaiengineaction
        text: qsTr('Reload AI &Engine')
        enabled: !bridge.busy
        onTriggered: {
            settings.sync()
            let renderingDevice = preferences.getRenderingDevice(false)
            console.debug('-- reload AI action triggered, renderingDevice =', renderingDevice)
            bridge.loadAiEngine(mainsignals,
                                renderingDevice,
                                settings.value('ai_aiModel', GlobalSettings.ai_aiModel),
                                settings.value('ai_modelLayer', GlobalSettings.ai_modelLayer),
                                settings.value('ai_modelNeuronFrom', GlobalSettings.ai_modelNeuronFrom),
                                settings.value('ai_modelNeuronTo', GlobalSettings.ai_modelNeuronTo),
                                settings.value('ai_lastLayerConcept', GlobalSettings.ai_lastLayerConcept),
                                settings.value('ai_tiledRendering', GlobalSettings.ai_tiledRendering))
        }
    }
    Action {
        id: quitaction
        text: qsTr('&Quit')
        shortcut: StandardKey.Quit
        enabled: true
        onTriggered: mainwindow.close()
    }
    Action {
        id: aboutaction
        text: qsTr('&About')
        enabled: true
        onTriggered: { about.show() }
    }
    Action {
        id: presentationaction
        text: qsTr('Quic&k Intro')
        enabled: false
        // onTriggered: TODO!
    }
    Action {
        id: infoaction
        text: qsTr('Renderers Infor&mation')
        enabled: false
        // onTriggered: TODO!
    }

    Shortcut {
        sequence: StandardKey.Close
        onActivated: mainwindow.close()
    }

    //<<<application_menubar>>>//

    //<<<application_menucontext>>>//

    // --- File opening, saving, and application closing
    property bool closingConfirmed: false

    onClosing: close => {
        console.debug('closingConfirmed =', closingConfirmed, 'bridge.saved =', bridge.saved)
        if (!closingConfirmed && !bridge.saved) {
            close.accepted = false
            closedialog.open()
        }
    }

    QtPl.MessageDialog {
        id: closedialog
        buttons: (QtPl.MessageDialog.Yes | QtPl.MessageDialog.No)
        text: qsTr('You have an unsaved dream. Close anyway?')
        informativeText: qsTr('You have a dream that was not saved to an image file. Closing the application will lose the dream. Close anyway?')
        onYesClicked: function() {
            console.debug('--')
            closingConfirmed = true
            mainwindow.close()
        }
    }

    // --- Preferences window

    Preferences {
        id: preferences
        visible: false
        reloadAiEngineAction: reloadaiengineaction
    }

    // --- About window

    About {
        id: about
        visible: false
    }

    // --- Disclaimers window

    Disclaimers {
        id: disclaimers
        visible: false
    }

    // --- Dreaming (main functionality) facilities
    property string dreamImagePath: ''

    function maybeOpenImage(imagePath) {
        console.debug('imagePath =', imagePath)
        if (bridge.busy) {
            newtaskdialog.imagePath = imagePath
            newtaskdialog.open()
        }
        else if (bridge.hasImage && !bridge.saved && settings.overwriteConfirmation) {
            checksavedialog.imagePath = imagePath
            checksavedialog.open()
        }
        else {
            openImage(imagePath)
        }
    }

    function openImage(imagePath) {
        let maximumImageSize = settings.value('st_maximumImageSize', GlobalSettings.st_maximumImageSize)
        console.debug('imagePath =', imagePath, 'maximumImageSize =', maximumImageSize)
        let result = null
        let ignoreImmediate = false
        if (imagePath === 'clipboard://') {
            result = bridge.pasteImage(maximumImageSize)
        }
        else if (imagePath === 'restore://') {
            result = bridge.restoreImage()
            ignoreImmediate = true
        }
        else if (imagePath === 'new://') {
            result = bridge.newImage(imageWidth, imageHeight, maximumImageSize)
        }
        else {
            if (String(imagePath).startsWith('file://')) {
                imagePath = bridge.urlToPath(imagePath)
            }
            result = bridge.openImage(imagePath, maximumImageSize)
        }
        console.debug('result =', result)
        if (result[0]) {
            dreamImagePath = imagePath
            statusbar.state = 'ready'
            statustext.text = ''
            let w = result[1]
            let h = result[2]
            mainwindow.resize(w, h)
            if (settings.dreamImmediate && !ignoreImmediate) {
                dreamaction.trigger()
            }
        }
        else {
            statusbar.state = 'error'
            statustext.text = result[3]
            imageview.source = IMAGES_URI + '/broken.png'
        }
    }

    function saveImage(imagePath) {
        let imageSaveQuality = settings.value('st_imageSaveQuality', GlobalSettings.st_imageSaveQuality)
        console.debug('imagePath =', imagePath, 'imageSaveQuality =', imageSaveQuality)
        if (String(imagePath).startsWith('file://')) {
            imagePath = bridge.urlToPath(imagePath)
        }
        let result = bridge.saveImage(imagePath, imageSaveQuality)
        if (result === '') {
            statusbar.state = 'ready'
            statustext.text = 'dream saved'
        }
        else {
            statusbar.state = 'error'
            statustext.text = result
        }
    }

    QtPl.MessageDialog {
        id: checksavedialog
        buttons: (QtPl.MessageDialog.Yes | QtPl.MessageDialog.No)
        text: qsTr('You have an unsaved dream. Overwrite it?')
        informativeText: qsTr('You have a dream that was not saved to an image file. Changing the current image will lose it. Proceed anyway?')
        property string imagePath: ''
        onYesClicked: function() {
            console.debug('imagePath =', imagePath)
            openImage(imagePath)
        }
    }

    QtPl.MessageDialog {
        id: newtaskdialog
        buttons: (QtPl.MessageDialog.Yes | QtPl.MessageDialog.No)
        text: qsTr('A dream is still cooking. Proceed?')
        informativeText: qsTr('If you start a dream with a new image, your progress on the previous dream will be lost. Proceed anyway?')
        property string imagePath: ''
        onYesClicked: function() {
            console.debug('imagePath =', imagePath)
            openImage(imagePath)
        }
    }

    QtPl.FileDialog {
        id: opendialog
        fileMode: QtPl.FileDialog.OpenFile
        defaultSuffix: bridge.DEFAULT_SUFFIX
        nameFilters: bridge.OPEN_IMAGE_FILTERS
        property bool saveFolderOnClose: true
        onAccepted: {
            console.debug('file =', file, 'folder =', folder)
            if (saveFolderOnClose) {
                settingspaths.openFolderUri = bridge.parentUrl(file)
            }
            maybeOpenImage(file)
        }
        onRejected: {
            console.debug('folder =', folder)
            if (saveFolderOnClose) {
                settingspaths.openFolderUri = folder
            }
        }
    }

    QtPl.FileDialog {
        id: savedialog
        fileMode: QtPl.FileDialog.SaveFile
        defaultSuffix: bridge.DEFAULT_SUFFIX
        nameFilters: bridge.SAVE_IMAGE_FILTERS
        onAccepted: {
            console.debug('file =', file, 'folder =', folder)
            settingspaths.saveFolderUri = bridge.parentUrl(file)
            saveImage(file)
        }
        onRejected: {
            console.debug('folder =', folder)
            settingspaths.saveFolderUri = folder
        }
    }


    // --- Drag-n-drop to main area
    MouseArea {
        anchors.fill: parent

        acceptedButtons: Qt.LeftButton | Qt.RightButton

        onClicked: mouse => {
            if (mouse.button === Qt.RightButton) {
                console.debug('--')
                menucontext.application_menucontext_open_function()
            }
        }

        onPressAndHold: mouse =>  {
            if (mouse.source === Qt.MouseEventNotSynthesized) {
                console.debug('--')
                menucontext.application_menucontext_open_function()
            }
        }

        onDoubleClicked: mouse => {
            if (mouse.button === Qt.LeftButton) {
                console.debug('--')
                preferencesaction.trigger()
            }
        }

        DropArea {
            anchors.fill: parent

            onEntered: drag => { // DragEvent drag
                drag.accept(bridge.checkDragAndDrop(drag.urls) ? Qt.CopyAction : Qt.IgnoreAction)
            }

            onPositionChanged: drag => { // DragEvent drag
                drag.accept(bridge.checkDragAndDrop(drag.urls) ? Qt.CopyAction : Qt.IgnoreAction)
            }

            onDropped: drop => { // DragEvent drop
                console.debug('bridge.ready =', bridge.ready, 'bridge.busy =', bridge.busy)
                let imagePath = bridge.checkDragAndDrop(drop.urls)
                if (imagePath && bridge.ready) {
                    maybeOpenImage(imagePath)
                    drop.accept()
                }
            }

            Image {
                id: imageview
                source: (IMAGES_URI + '/placeholder.png')
                cache: false
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit

                readonly property string neuralSource: 'image://neural_images/current/'
                property int neuralSeq: 0
                function neuralRefresh(taskId) {
                    if (taskId === bridge.taskId || taskId === mainsignals.SOURCE_IMAGE_TASK_ID) {
                        imageview.neuralSeq = imageview.neuralSeq + 1
                        imageview.source = imageview.neuralSource + imageview.neuralSeq
                        console.debug('-- taskId =', taskId, 'imageview.source =', imageview.source)
                    }
                }
            }
        }

    }


    // --- Bottom status bar
    Row {
        id: statusbar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        padding: 5
        spacing: 5
        state: 'ready'

        states: [
            State {
                name: 'ready'
                PropertyChanges { target: statuslight; color: Constants.successColor }
                PropertyChanges { target: statusprogress; visible: false }
            },
            State {
                name: 'busy'
                PropertyChanges { target: statuslight; color: Constants.busyColor }
                PropertyChanges { target: statusprogress; visible: false }
            },
            State {
                name: 'progressing'
                PropertyChanges { target: statuslight; color: Constants.busyColor }
                PropertyChanges { target: statusprogress; visible: true }
            },
            State {
                name: 'error'
                PropertyChanges { target: statuslight; color: Constants.warningColor }
                PropertyChanges { target: statusprogress; visible: false }
            }
        ]

        Rectangle {
            width: 24
            height: 24
            anchors.verticalCenter: parent.verticalCenter
            color: 'transparent'

            Rectangle {
                id: statuslight
                width: 12
                height: 12
                radius: 6
                anchors.centerIn: parent
                clip: true
                border.color: Qt.lighter(color, 1.5)
                border.width: 1
            }
        }

        ProgressBar {
            id: statusprogress
            width: 200
            height: 24
            value: 0.0
            anchors.verticalCenter: parent.verticalCenter
            visible: false
        }

        Rectangle {
            width: (statustext.width + 15)
            height: (statustext.height + 10)
            anchors.verticalCenter: parent.verticalCenter
            color: '#40ffffff'
            radius: 5
            visible: (statustext.text != '')

            Text {
                id: statustext
                color: '#AA000000'
                anchors.centerIn: parent
                font.pixelSize: 12
                font.bold: true
                verticalAlignment: Text.AlignVCenter
                text: ''
            }

        }

        Connections {
            target: mainsignals
            property int lastTaskId: mainsignals.NO_TASK_ID

            function onStarted(taskId, taskName, keepProgress) {
                console.debug('>> taskId =', taskId)
                lastTaskId = taskId
                statustext.text = taskName
                statusprogress.value = 0.0
                statusbar.state = keepProgress ? 'progressing' : 'busy'
                console.debug('<< taskId =', taskId)
            }

            function onProgress(taskId, fractionFinished, kwargs) {
                if (taskId === bridge.taskId) {
                    console.debug('-- taskId =', taskId)
                    lastTaskId = taskId
                    statusprogress.value = fractionFinished
                }
            }

            function onFinished(taskId, result, error, finalMessage) {
                if (taskId === bridge.taskId || (taskId === lastTaskId && !bridge.busy)) {
                    console.debug('>> taskId =', taskId)
                    statusbar.state = error ? 'error' : 'ready'
                    statustext.text = finalMessage
                    console.debug('<< taskId =', taskId)
                }
            }
        }
    }
}
