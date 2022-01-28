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
import Qt.labs.settings 6.2

import cookadream.aboutinfo 1.0


Window {
    id: disclaimerswindow
    flags: (Qt.Window | Qt.Dialog)
    visible: true
    minimumWidth: Math.max(disclaimersbuttons.contentsWidth*1.5, disclaimersheader.contentsWidth*5)
    minimumHeight: disclaimersheader.contentsHeight * 10
    modality: Qt.ApplicationModal

    Component.onCompleted: {
        x = Screen.width/2 - width/2
        y = Screen.height/2 - height/2
    }

    Settings {
        id: settings
        category: 'settings'
    }

    // --- Theme-compatible background-pane
    Pane {
        anchors.fill: parent
    }

    AboutInfo {
        id: disclaimersinfo
    }

    Shortcut {
        sequence: StandardKey.Refresh
        onActivated: {
            if (DIALOG_DEBUG) {
                disclaimersinfo._refresh()
            }
        }
    }

    // --- Main contents
    Rectangle {
        id: allcontents
        color: 'transparent'
        anchors.fill: parent
        anchors.margins: Constants.padding * 2

        // ---------> First row : Header
        ColumnLayout {
            id: disclaimersheader
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: contentsHeight
            spacing: Constants.spacing

            property real contentsHeight: disclaimersheader.implicitHeight
            property real contentsWidth: disclaimersheader.implicitWidth

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr('Cook-a-Dream')
                textFormat: Text.PlainText
                font.weight: Font.Bold
            }
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr('Version: ') + disclaimersinfo.version
                textFormat: Text.PlainText
            }
        }
        // <--------- First row : Header

        // ---------> Second row : Licensing contents
        ScrollView {
            id: disclaimerslicensesscroll
            anchors.top: disclaimersheader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: disclaimersbuttons.top
            anchors.margins: Constants.padding
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            Label {
                id: disclaimerslicenses
                width: disclaimerslicensesscroll.width
                text: disclaimersinfo.disclaimersText
                textFormat: Text.RichText
                wrapMode: Text.Wrap
                onLinkActivated: Qt.openUrlExternally(link)
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.NoButton
                    cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }
        }
        // <--------- Second row : Licensing contents

        // ---------> Third row : buttons
        RowLayout {
            id: disclaimersbuttons
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            spacing: Constants.spacing

            property real contentsHeight: disclaimersbuttons.implicitHeight
            property real contentsWidth: disclaimersbuttons.implicitWidth

            Button {
                id: buttonAccept
                text: qsTr('I understand and accept the risks')
                onClicked: {
                    settings.setValue('st_firstExecutionAccepted', true)
                    disclaimerswindow.close()
                }
            }
            Button {
                id: buttonReject
                text: qsTr('Close the application')
                onClicked: disclaimerswindow.close()
            }
        }
        // <--------- Third row : buttons

    }
}