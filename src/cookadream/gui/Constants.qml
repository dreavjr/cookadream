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
pragma Singleton
import QtQuick
import QtQuick.Controls.Material 6.2
import QtQuick.Controls.Universal 6.2


QtObject {
    // --- UI dimensions
    readonly property int defaultWidth: Math.floor(
                                        Math.min( Screen.desktopAvailableWidth  * 0.875,
                                                  Screen.desktopAvailableHeight * 0.875,
                                                 (Screen.desktopAvailableWidth + Screen.desktopAvailableHeight)/6 ) )
    readonly property int defaultHeight: defaultWidth
    readonly property int minimumWindowSize: 64

    readonly property int spacing: 10
    readonly property int padding: 10

    readonly property int slidersSize: 250

    // --- UI colors
    property color successColor:      (CONTROLS_THEME == 'Universal' ? '#008A00' : '#4CAF50') // Universal.Emerald / Material.Green
    property color busyColor:         (CONTROLS_THEME == 'Universal' ? '#F0A30A' : '#FF9800') // Universal.Amber   / Material.Orange
    property color warningColor:      (CONTROLS_THEME == 'Universal' ? '#E51400' : '#E91E63') // Universal.Red     / Material.Pink
    property color interactiveColor:  (CONTROLS_THEME == 'Universal' ? '#3E65FF' : '#3F51B5') // Universal.Cobalt  / Material.Indigo (Accent and Primary)

    property color successTextColor:     (CONTROLS_THEME == 'Universal' ? '#008A00' : (Material.theme === Material.Light ? '#4CAF50' : '#A5D6A7')) // Universal.Emerald  / Material.Green
    property color busyTextColor:        (CONTROLS_THEME == 'Universal' ? '#F0A30A' : (Material.theme === Material.Light ? '#FF9800' : '#FFAA00')) // Universal.Amber    / Material.Orange
    property color warningTextColor:     (CONTROLS_THEME == 'Universal' ? '#E51400' : (Material.theme === Material.Light ? '#E91E63' : '#F48FB1')) // Universal.Red      / Material.Pink
    property color interactiveTextColor: (CONTROLS_THEME == 'Universal' ? '#3E65FF' : (Material.theme === Material.Light ? '#3F51B5' : '#9FA8DA')) // Universal.Cobalt   / Material.Indigo

    // --- AI Models Limits
    readonly property int modelDeepest: 27
    readonly property int layerLargest: 2048
}
