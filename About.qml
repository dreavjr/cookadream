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
    id: aboutwindow
    flags: (Qt.Window | Qt.Dialog)
    visible: true
    minimumWidth: aboutheader.contentsWidth + 2*Constants.padding
    minimumHeight: 3*aboutheader.contentsHeight + 2*Constants.spacing + 2*Constants.padding
    modality: Qt.ApplicationModal

    Component.onCompleted: {
        x = Screen.width/2 - width/2
        y = Screen.height/2 - height/2
    }

    // --- Theme-compatible background-pane
    Pane {
        anchors.fill: parent
    }

    AboutInfo {
        id: aboutinfo
    }

    Shortcut {
        sequence: StandardKey.Refresh
        onActivated: {
            if (DIALOG_DEBUG) {
                aboutinfo._refresh()
            }
        }
    }
    Shortcut {
        sequence: StandardKey.Close
        onActivated: aboutwindow.close()
    }
    Shortcut {
        sequence: 'Return'
        onActivated: aboutwindow.close()
    }
    Shortcut {
        sequence: 'Esc'
        onActivated: aboutwindow.close()
    }

    // --- Main contents
    Rectangle {
        id: allcontents
        color: 'transparent'
        anchors.fill: parent
        anchors.margins: Constants.padding

        // ---------> First row : Header
        Rectangle {
            id: aboutheader
            color: 'transparent'
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right

            property real contentsReference: aboutdata.contentsHeight
            property real contentsHeight: contentsReference
            property real contentsWidth: contentsReference + Constants.spacing + aboutdata.contentsWidth

            height: contentsHeight

            Rectangle {
                color: 'transparent'
                anchors.top: parent.top
                anchors.left: parent.left
                height: aboutheader.contentsReference
                width: aboutheader.width * (abouticon.width/aboutheader.contentsWidth)
                Image {
                    id:abouticon
                    height: aboutheader.contentsReference
                    width: aboutheader.contentsReference
                    anchors.centerIn: parent
                    source: (IMAGES_URI + '/application_icon.png')
                }
            }

            ColumnLayout {
                id: aboutdata
                anchors.top: parent.top
                anchors.right: parent.right
                height: contentsHeight
                width: aboutheader.width * (contentsWidth/aboutheader.contentsWidth)
                spacing: Constants.spacing

                property real contentsHeight: aboutdata.implicitHeight
                property real contentsWidth: aboutdata.implicitWidth

                Label {
                    text: qsTr('Cook-a-Dream')
                    textFormat: Text.PlainText
                    font.weight: Font.Bold
                }
                Label {
                    text: qsTr('Version: ') + aboutinfo.version
                    textFormat: Text.PlainText
                }
                Label {
                    text: qsTr('Commit: ') + aboutinfo.commit
                    textFormat: Text.PlainText
                }
                Label {
                    text: qsTr('System Info: ') + aboutinfo.sysinfo
                    textFormat: Text.PlainText
                    font.italic: true
                }
            }
        }
        // <--------- First row : Header

        // ---------> Second row : Licensing contents
        ScrollView {
            id: aboutlicensesscroll
            anchors.top: aboutheader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: aboutbuttons.top
            anchors.margins: Constants.padding
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            Label {
                id: aboutlicenses
                width: aboutlicensesscroll.width
                text: aboutinfo.licenseText
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
            id: aboutbuttons
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            spacing: Constants.spacing
            Button {
                text: qsTr('Copy Info')
                onClicked: aboutinfo.copyInfo()
            }
            Button {
                text: qsTr('Copy Credits')
                onClicked: aboutinfo.copyLicense()
            }
            Button {
                text: qsTr('Close')
                onClicked: aboutwindow.close()
            }
        }
        // <--------- Third row : buttons

    }
}