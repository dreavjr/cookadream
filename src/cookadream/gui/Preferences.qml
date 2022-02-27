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
import QtQuick.Layouts 6.2
import QtQuick.Window 6.2
import QtQml.XmlListModel 6.2
import Qt.labs.settings 6.2

import cookadream.dreamengine 1.0


Window {
    id: preferenceswindow
    flags: (Qt.Window | Qt.Dialog)
    visible: true

    // Those layout options resize the window automatically with the contents, and disable resizing by user
    readonly property real targetWidth: (alloptions.width + 2*Constants.padding)
    readonly property real targetHeight: (alloptions.height + 2*Constants.padding)
    width: targetWidth
    height: targetHeight
    minimumWidth: targetWidth
    minimumHeight: targetHeight
    maximumWidth: targetWidth
    maximumHeight: targetHeight

    // --- Window state persistence
    Settings {
        id: windowsstate
        category: 'preferenceswindow'
        property alias x: preferenceswindow.x
        property alias y: preferenceswindow.y
    }

    // --- Settings - Persistence
    Settings {
        id: internals
        category: 'settings_internals'
        property alias firstExecution:        defaultsLoader.firstExecution

        property alias ai_a_aiModel:          aimodel.currentIndex
        property alias ai_b_modelLayer:       modellayer.value
        property alias ai_c_lastLayerConcept: lastlayerconcept.currentIndex
        property alias ai_c_modelNeuronFrom:  modelneuron.first.value
        property alias ai_c_modelNeuronTo:    modelneuron.second.value
        property alias ai_renderingDevice:    renderingdevice.currentIndex
        property alias ai_tiledRendering:     tiledrendering.checkState
        // property alias st_dreamDecorrelate:   dreamdecorrelate.checkState
        property alias st_dreamOctavesFrom:   dreamoctaves.first.value
        property alias st_dreamOctavesTo:     dreamoctaves.second.value
        property alias st_dreamShaking:       dreamshaking.value
        property alias st_dreamSmoothing:     dreamsmoothing.value
        property alias st_dreamSpeed:         dreamspeed.value
        property alias st_imageSaveQuality:   imagesavequality.value
        property alias st_maximumImageSize:   maximumimagesize.currentIndex
        property alias st_octavesBlending:    octavesblending.value
        property alias st_octavesScaling:     octavesscaling.value
        property alias st_stepsPerOctave:     stepsperoctave.value

        function reset() {
            console.debug('--')
            ai_a_aiModel = GlobalSettings.internals_ai_a_aiModel
            ai_b_modelLayer = GlobalSettings.internals_ai_b_modelLayer
            ai_c_lastLayerConcept = GlobalSettings.internals_ai_c_lastLayerConcept
            ai_c_modelNeuronFrom = GlobalSettings.internals_ai_c_modelNeuronFrom
            ai_c_modelNeuronTo = GlobalSettings.internals_ai_c_modelNeuronTo
            ai_renderingDevice = GlobalSettings.internals_ai_renderingDevice
            ai_tiledRendering = GlobalSettings.internals_ai_tiledRendering
            st_dreamOctavesFrom = GlobalSettings.internals_st_dreamOctavesFrom
            st_dreamOctavesTo = GlobalSettings.internals_st_dreamOctavesTo
            st_dreamShaking = GlobalSettings.internals_st_dreamShaking
            st_dreamSmoothing = GlobalSettings.internals_st_dreamSmoothing
            st_dreamSpeed = GlobalSettings.internals_st_dreamSpeed
            st_imageSaveQuality = GlobalSettings.internals_st_imageSaveQuality
            st_maximumImageSize = GlobalSettings.internals_st_maximumImageSize
            st_octavesBlending = GlobalSettings.internals_st_octavesBlending
            st_octavesScaling = GlobalSettings.internals_st_octavesScaling
            st_stepsPerOctave = GlobalSettings.internals_st_stepsPerOctave
            ai_renderingDevice = getRenderingDevice(true)
            internals.sync()
            settings.sync()
        }
    }

    Item {
        id: defaultsLoader
        property bool firstExecution: true
        Component { Item {} }
        Component.onCompleted: {
            internals.sync()
            console.debug('-- firstExecution =', firstExecution)
            if (firstExecution && !COMPILE_SETTINGS) {
                internals.reset()
                firstExecution = false
            }
        }
   }

    // --- Settings UI-indenpendent values
    // --- Settings - Global UI-Indepentent Values
    Settings {
        id: settings
        category: 'settings'
        readonly property string ai_aiModel:          aimodeldata.module
        readonly property int    ai_lastLayerConcept: (modellayer.value == modellayer.to ? lastlayerconcept.currentValue : -1)
        readonly property string ai_modelLayer:       modellayer.layerName
        readonly property int    ai_modelNeuronFrom:  modelneuron.first.value
        readonly property int    ai_modelNeuronTo:    modelneuron.second.value
        readonly property string ai_renderingDevice:  (renderingdevice.currentValue ? renderingdevice.currentValue : '')
        readonly property bool   ai_tiledRendering:   tiledrendering.checkState === Qt.Checked
        // readonly property bool   st_dreamDecorrelate: dreamdecorrelate.checkState === Qt.Checked
        readonly property int    st_dreamOctavesFrom: dreamoctaves.first.value
        readonly property int    st_dreamOctavesTo:   dreamoctaves.second.value
        readonly property int    st_dreamShaking:     dreamshaking.value
        readonly property real   st_dreamSmoothing:   dreamsmoothing.valueValue
        readonly property real   st_dreamSpeed:       dreamspeed.value
        readonly property int    st_imageSaveQuality: imagesavequality.value
        readonly property int    st_maximumImageSize: maximumimagesize.currentValue
        readonly property real   st_octavesBlending:  octavesblending.value
        readonly property real   st_octavesScaling:   octavesscaling.valueValue
        readonly property int    st_stepsPerOctave:   stepsperoctave.valueValue
    }

    property var aiSettingsNames: ''
    property string aiSettings: ''
    property bool aiSettingsHaveChanged: false
    function findSettings() {
        let names = []
        for (let property in settings) {
            if (property.startsWith('ai_') && !property.endsWith('Changed')) {
                names.push(property)
            }
        }
        names.sort()
        aiSettingsNames = names
        console.debug('-- aiSettingsNames =', aiSettingsNames)
    }
    function getSettingsValues() {
        let values = JSON.stringify(aiSettingsNames.map(n => settings[n]))
        return values
    }
    function connectSettings() {
        aiSettingsNames.forEach(n => {
            settings[n + 'Changed'].connect(checkSettings)
        })
    }
    function registerSettings() {
            aiSettings = getSettingsValues()
            aiSettingsHaveChanged = false
            console.debug('-- aiSettings =', aiSettings)
    }
    function checkSettings() {
            aiSettingsHaveChanged = getSettingsValues() != aiSettings
    }

    property bool preferenceswindowReady: false
    onAfterAnimating: {
        if (!preferenceswindowReady) {
            console.debug('--')
            preferenceswindowReady = true
            findSettings()
            registerSettings()
            connectSettings()
        }
    }

    DreamEngineInfo {
        id: dreamengineinfo
    }
    function getRenderingDevice(index) {
        settings.sync()
        let devices = dreamengineinfo.DREAM_DEVICES
        let device = settings.ai_renderingDevice
        console.debug('--', device, devices)
        if (device) {
            let i = devices.indexOf(device)
            if (i >= 0) {
                console.debug('-- CONFIGURED:', i, device)
                return index ? i : device
            }
        }
        for (let i=0; i<devices.length; i++) {
            let device = devices[i]
            if (device.includes('GPU')) {
                console.debug('-- NOT CONFIGURED: using first GPU found:', i, device)
                renderingdevice.currentIndex = i
                return index ? i : device
            }
        }
        console.debug('-- NOT CONFIGURED: GPU not found, falling back to first device listed:', 0, device)
        renderingdevice.currentIndex = 0
        return index ? 0 : devices[0]
    }

    // --- Action from main window to trigger the AI engine reloading
    property var reloadAiEngineAction: null

    // --- Shortcut for closing the window with standard key sequences
    Shortcut {
        sequence: StandardKey.Close
        onActivated: preferenceswindow.close()
    }

    // --- Theme-compatible background-pane
    Pane {
        anchors.fill: parent
    }

    // --- Main contents
    RowLayout {
        id: alloptions
        x: Constants.padding
        y: Constants.padding
        spacing: Constants.spacing
        // ---------> First Column : Image and AI options
        ColumnLayout {
            Layout.alignment: Qt.AlignTop
            Layout.fillHeight: true
            spacing: Constants.spacing

            // >>>>> AI options
            GroupBox {
                title: qsTr('AI options:')
                Layout.fillWidth: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: Constants.spacing

                    // - Rendering TensorFlow device
                    RowLayout {
                        spacing: Constants.spacing
                        Label {
                            text: qsTr('Rendering device:')
                        }
                        ComboBox {
                            id: renderingdevice
                            currentIndex: -1
                            implicitContentWidthPolicy: ComboBox.WidestText
                            model: dreamengineinfo.DREAM_DEVICES
                        }
                    }
                    WarningText {
                        text: qsTr('dreaming on a CPU may be very slow — use a GPU if possible')
                        visible: renderingdevice.currentText.includes(':CPU:')
                    }

                    // -- Tiled rendering
                    CheckBox {
                        id: tiledrendering
                        text: qsTr('Use tiled rendering')
                        checkState: Qt.Checked
                        visible: modellayer.value != modellayer.to
                    }
                    WarningText {
                        text: qsTr('tiled rendering uses less memory and may be faster in some devices')
                        visible: (tiledrendering.visible && tiledrendering.checkState !== Qt.Checked)
                    }
                    CheckBox {
                        id: tiledrenderingdummy
                        text: qsTr('Use tiled rendering')
                        checkState: Qt.Checked
                        enabled: false
                        visible: !tiledrendering.visible
                    }
                    WarningText {
                        text: qsTr('tiled rendering is required when using the highest layer')
                        visible: tiledrenderingdummy.visible
                    }


                    // -- AI model
                    RowLayout {
                        spacing: Constants.spacing
                        Label {
                            text: qsTr('AI model used for dreaming:')
                        }
                        ComboBox { // TODO!!! Decide on the default model
                            id: aimodel
                            implicitContentWidthPolicy: ComboBox.WidestText
                            currentIndex: 0
                            model: aimodelmodel
                            textRole: 'ai_name'
                            valueRole: 'ai_all_info'
                        }
                    }
                    HelpText { // TODO!!! Bind this description to  aimodel
                            text: aimodeldata.description
                    }

                    QtObject {
                        id: aimodeldata
                        property alias encodedInfo: aimodel.currentValue
                        readonly property string jsonInfo: Qt.atob(encodedInfo)
                        readonly property var modelInfo: (jsonInfo ? JSON.parse(jsonInfo) :
                                                                     {'module': '',
                                                                      'description': '',
                                                                      'layers_n': 0,
                                                                      'layers': []})
                        readonly property string module: modelInfo.module
                        readonly property string description: modelInfo.description
                        readonly property int layersN: modelInfo.layers_n
                        readonly property var layersInfo: modelInfo.layers
                        onModelInfoChanged: {
                            console.debug('-- module =', module, 'description =', description, 'layersN =', layersN)
                            if (modelneuron) {
                                modelneuron.update()
                            }
                        }
                    }

                    XmlListModel {
                        id: aimodelmodel
                        source: (DATA_URI + '/models.xml')
                        query: '/models/model'
                        XmlListModelRole { name: 'ai_name';     elementName: 'name' }
                        XmlListModelRole { name: 'ai_all_info'; elementName: 'all_info' }
                    }

                    // -- Model Layer
                    Label {
                        text: qsTr('Model layer to excite for dreaming:')
                    }
                    IndicatorSlider { // TODO!!! Bind the highest layer (to:) on aimodel
                        id: modellayer
                        preferredWidth: Constants.slidersSize
                        from: 1
                        to: (aimodeldata.layersN > 0 ? aimodeldata.layersN : Constants.modelDeepest) // Needed to preserve value during load
                        stepSize: 1
                        value: 6
                        enabled: aimodeldata.layersN > 0
                        readonly property string layerName: getLayerInfo(aimodeldata.layersInfo, value, 'name')
                        readonly property string layerSize: getLayerInfo(aimodeldata.layersInfo, value, 'size')

                        onValueChanged: {
                            console.debug('-- from =', from, 'to =', to, 'value =', value, 'layerName =', layerName, 'layerSize =', layerSize)
                            if (modelneuron) {
                                modelneuron.update()
                            }
                            if (preferenceswindowReady) {
                                modelneuron.first.value = modelneuron.from
                                modelneuron.second.value = modelneuron.to
                            }
                        }

                        function getLayerInfo(layersInfo, layer, info) {
                            let l = layer-1
                            if (layersInfo && l>=0 && layersInfo[l]) {
                                if (info === 'name') {
                                    return layersInfo[l].n
                                }
                                else if (info === 'desc') {
                                    return layersInfo[l].n + ' (' + qsTr('layer') + ' ' + layersInfo[l].i + ')'
                                }
                                else if (info === 'size') {
                                    return layersInfo[l].s
                                }
                            }
                            return info === 'size' ? -1 : ''
                        }

                        ToolTip {
                            parent: modellayer.viewerLabel
                            delay: 500
                            timeout: 5000
                            visible: modellayer.viewer.hovered
                            text: modellayer.getLayerInfo(aimodeldata.layersInfo, modellayer.value, 'desc')
                        }

                    }
                    // ... neurons - if intermediate layer
                    Label {
                        text: qsTr('Layer neurons to excite for dreaming:')
                        visible: modelneuron.visible
                    }
                    IndicatorRangeSlider {
                        id: modelneuron
                        visible: modellayer.value != modellayer.to
                        preferredWidth: Constants.slidersSize
                        from: 1
                        to: (modellayer.layerSize > 0 ? modellayer.layerSize : Constants.layerLargest) // Needed to preserve value during load
                        stepSize: 1
                        first.value: 0
                        second.value: 768
                    }

                    // ... concept - if layer layer
                    RowLayout {
                        spacing: Constants.spacing
                        visible: !modelneuron.visible
                        Label {
                            text: qsTr('Concept to dream about:')
                        }
                        ComboBox {
                            id: lastlayerconcept
                            implicitContentWidthPolicy: ComboBox.WidestText
                            currentIndex: 0
                            model: lastlayerconceptmodel
                            textRole: 'imagenet_name'
                            valueRole: 'keras_id'
                        }
                    }

                    XmlListModel {
                        id: lastlayerconceptmodel
                        source: (DATA_URI + '/imagenet.xml')
                        query: '/imagenet_classes/imagenet_class'
                        XmlListModelRole { name: 'imagenet_name'; elementName: 'imagenet_name' }
                        XmlListModelRole { name: 'keras_id';      elementName: 'keras_id' }
                    }

                    // ... help for layers
                    HelpText {
                        text: qsTr('Low layers tend to create simple textures, high layers tend to generate more complex patterns, including parts of objects. For sharper dreams, you may choose a narrower range of neurons in the intermediate layers, or a particular concept in the highest layer.')
                    }

                }
            }
            // <<<<< AI options

        }
        // <--------- First Column

        // ---------> Second Column
        ColumnLayout {
            Layout.alignment: Qt.AlignTop
            Layout.fillHeight: true
            spacing: Constants.spacing

            // >>>>> Dream options
            GroupBox {
                Layout.fillWidth: true
                title: qsTr('Dream scale:')

                ColumnLayout {
                    anchors.fill: parent
                    spacing: Constants.spacing

                    // -- Octaves
                    // - Octaves for dreaming
                    Label {
                        text: qsTr('Octaves to use for dreaming:')
                    }
                    IndicatorRangeSlider {
                        id: dreamoctaves
                        preferredWidth: Constants.slidersSize
                        from: -5
                        to: 5
                        stepSize: 1
                        first.value: 1
                        second.value: 4
                    }

                    // - Octave scaling
                    Label {
                        text: qsTr('Octave scaling:')
                    }
                    IndicatorSlider {
                        id: octavesscaling
                        preferredWidth: Constants.slidersSize
                        from: 0
                        to: (valueLabels.length-1)
                        stepSize: 1
                        value: 4
                        viewerText: valueLabel
                        viewerLabel.font.pointSize: 22
                        // readonly property var valueLabels: ['⅙', '⅕', '¼', '⅓', '½']
                        // readonly property var valueLabels: ['1/6', '1/5', '1/4', '1/3', '1/2']
                        readonly property var valueLabels: ['¹/₆', '¹/₅', '¹/₄', '¹/₃', '¹/₂', '²/₃', '³/₄', '⁴/₅']
                        readonly property var valueValues: [ 1/6,   1/5,   1/4,   1/3,   1/2,   2/3,   3/4,   4/5 ]
                        readonly property string valueLabel: valueLabels[value]
                        readonly property double valueValue: valueValues[value]
                    }

                    // - Steps per octave
                    Label {
                        text: qsTr('Dream steps in each octave:')
                    }
                    IndicatorSlider {
                        id: stepsperoctave
                        preferredWidth: Constants.slidersSize
                        from: 1
                        to: 15
                        stepSize: 1
                        value: 4
                        viewerText: valueValue
                        readonly property int valueValue: (value**2 * 10)
                    }

                    // - Octave blending
                    Label {
                        text: qsTr('Blend octaves with original:')
                    }
                    IndicatorSlider {
                        id: octavesblending
                        preferredWidth: Constants.slidersSize
                        from: 0
                        to: 99
                        stepSize: 1
                        value: 25
                    }

                    // - Help text for octaves
                    HelpText {
                        text: qsTr('Small (negative) octaves focus on details of the image, while large (positive) octaves focus on larger areas. Scaling adjusts the spread of octaves: smaller fractions make the scales closer.')
                    }
                }
            }
            // <<<<< Dream options

            // >>>>> Buttons: Reset and Reload
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: (resetbutton.height + Constants.padding)
                color: "transparent"
                RowLayout {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    // anchors.margins: Constants.padding
                    spacing: Constants.spacing
                    Button {
                        id: resetbutton
                        text: qsTr('Reset to Defaults')
                        Layout.alignment: (Qt.AlignBottom | Qt.AlignLeft)
                        onClicked: internals.reset()
                    }
                    Button {
                        id: reloadbutton
                        text: qsTr('Apply AI Changes')
                        Layout.alignment: (Qt.AlignBottom | Qt.AlignLeft)
                        visible: aiSettingsHaveChanged
                        highlighted: aiSettingsHaveChanged
                        enabled: (reloadAiEngineAction ? reloadAiEngineAction.enabled : true)
                        onClicked: {
                            if (reloadAiEngineAction) {
                                reloadAiEngineAction.trigger()
                            }
                            registerSettings()
                        }
                    }
                }
            }
            // <<<<< Buttons: Reset and Reload

        }
        // <--------- Second Column

        // ---------> Third Column : Smoothing and Image options
        ColumnLayout {
            Layout.alignment: Qt.AlignTop
            Layout.fillHeight: true
            spacing: Constants.spacing


            // >>>>> Dream smoothing
            GroupBox {
                Layout.fillWidth: true
                title: qsTr('Dream speed and smoothness:')

                ColumnLayout {
                    anchors.fill: parent
                    spacing: Constants.spacing

                    // - Dream speed
                    Label {
                        text: qsTr('Dream speed:')
                    }
                    IndicatorSlider {
                        id: dreamspeed
                        preferredWidth: Constants.slidersSize
                        from: 0.001
                        to: 0.1
                        stepSize: 0.001
                        value: 0.01
                        viewerText: valueLabel
                        readonly property string valueLabel: value.toFixed(3)
                    }

                    // CheckBox {
                    //     id: dreamdecorrelate
                    //     text: qsTr('Adapt colors for better dreaming')
                    //     checkState: Qt.Checked
                    // }

                    // - Total variation penalization
                    Label {
                        text: qsTr('Avoid sudden image variations:')
                    }
                    IndicatorSlider {
                        id: dreamsmoothing
                        preferredWidth: Constants.slidersSize
                        from: -401
                        to: 400
                        stepSize: 1
                        value: 0
                        viewerText: valueLabel
                        viewerLabel.font.pointSize: 20
                        // readonly property var valueLabels: ['0', '10⁻²', '10⁻¹', '1', '10¹', '10²', '10³', '10⁴']
                        // readonly property var valueValues: [ 0,   1e-2,   1e-1,   1,   1e1,  1e2,    1e3,  1e4  ]
                        readonly property string valueLabel: translateLabel(value)
                        readonly property double valueValue: translateValue(value)
                        viewerLabel.textFormat: Text.RichText // [Qt6.22] this should not be necessary, workaround to enforce <sup> tag
                        function translateLabel(v) {
                            if (v === from) {
                                return '0'
                            }
                            let vStr = (v/100.).toFixed(2)
                            return '10<sup>' + vStr + '</sup>'
                        }
                        function translateValue(v) {
                            if (v === from) {
                                return 0.
                            }
                            return 10.**(v/100.)
                        }
                    }

                    // - Image shaking (Jitter)
                    Label {
                        text: qsTr('Shake image between dream steps:')
                    }
                    IndicatorSlider {
                        id: dreamshaking
                        preferredWidth: Constants.slidersSize
                        from: 0
                        to: 128
                        stepSize: 2
                        value: 64
                        visible: tiledrendering.checkState !== Qt.Checked && modellayer.value != modellayer.to
                    }
                    IndicatorSlider {
                        id: dreamshakingdummy
                        preferredWidth: Constants.slidersSize
                        from: 0
                        to: 128
                        stepSize: 2
                        value: 128
                        viewerText: '128+'
                        enabled: false
                        visible: !dreamshaking.visible
                    }

                    // - Help text for octaves
                    HelpText {
                        text: qsTr('Dream smoothing often leads to prettier images, with less noise and artifacts, but too much smoothing may result in very slow dreaming, or in excessive blurring. Tiled rendering always shakes the image.')
                    }
                }
            }
            // <<<<< Dream smoothing


            // >>>>> Image options
            GroupBox {
                Layout.fillWidth: true
                title: qsTr('Image options:')

                ColumnLayout {
                    anchors.fill: parent
                    spacing: Constants.spacing

                    // -- Maximum image size
                    RowLayout {
                        spacing: Constants.spacing
                        Label {
                            text: qsTr('Maximum image size:')
                        }
                        ComboBox {
                            id: maximumimagesize
                            implicitContentWidthPolicy: ComboBox.WidestText
                            currentIndex: 1
                            textRole: "label"
                            valueRole: "value"
                            model: [
                                    { label: '512',  value: 512 },
                                    { label: '1024', value: 1024 },
                                    { label: '2048', value: 2048 },
                                    { label: qsTr('no limit'), value: 0 },
                                ]
                        }
                    }
                    WarningText {
                        text: qsTr('large images may be very slow to render and use more memory than available')
                        visible: maximumimagesize.currentValue == 0
                    }

                    // -- Image quality for lossy compressions on save
                    Label {
                        text: qsTr('Quality for lossy compression when saving dreams:')
                    }
                    IndicatorSlider {
                        id: imagesavequality
                        preferredWidth: Constants.slidersSize
                        from: 0
                        to: 100
                        stepSize: 1
                        value: 85
                    }
                    WarningText {
                        text: qsTr('quality this low will save the images with noticeable distortions')
                        visible: imagesavequality.value < 50
                    }
                }
            }
            // <<<<< Image options

        }
        // ---------> Third Column

    }
}
