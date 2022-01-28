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


RowLayout {
    id: indicatorslider
    Layout.fillWidth: true
    spacing: Constants.spacing
    property real preferredWidth: 200 // QML didn't allow aliasing here
    property alias from: slider.from
    property alias to: slider.to
    property alias stepSize: slider.stepSize
    property alias snapMode: slider.snapMode
    property alias first: slider.first
    property alias second: slider.second
    property int decimalPlaces: 0
    property string viewerText: (first.value.toFixed(decimalPlaces) + ' ~ ' +
                                 second.value.toFixed(decimalPlaces))
    property alias viewerLabel: viewerlabel
    property alias viewer: viewercontainer
    RangeSlider {
        id: slider
        from: 1
        to: 100
        stepSize: 1
        snapMode: Slider.SnapAlways
        first.value: 25
        second.value: 75
        Layout.preferredWidth: indicatorslider.preferredWidth
    }
    MouseArea {
        id: viewercontainer
        hoverEnabled: Qt.styleHints.useHoverEffects
        property alias hovered: viewercontainer.containsMouse
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumHeight: viewerlabel.height
        Layout.minimumWidth: viewerlabel.width
        Label {
            id: viewerlabel
            text: viewerText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}