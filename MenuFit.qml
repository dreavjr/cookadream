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


Menu {
    width: {
        let maxWidth = 0;
        let maxPadding = 0;
        for (let i=0; i<count; i++) {
            let item = itemAt(i)
            maxWidth = Math.max(maxWidth, item.contentItem.implicitWidth)
            maxPadding = Math.max(maxPadding, item.padding)
        }
        return maxWidth + 2 * maxPadding
    }
}
