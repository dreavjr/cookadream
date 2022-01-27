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


Text {
    id: helptext
    Layout.fillWidth: true
    Layout.preferredWidth: 0
    text: 'helptext'
    property bool helpExpanded: false
    elide: (helpExpanded ? Text.ElideNone : Text.ElideRight)
    wrapMode: (helpExpanded ? Text.Wrap : Text.NoWrap)
    color: Constants.interactiveTextColor

    MouseArea {
        anchors.fill: parent
        onClicked: { helpExpanded = !helpExpanded }
    }
}
