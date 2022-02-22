@.MenuBar {
    id: menubar
    @.<Menu> {
        title: qsTr("&File")
        action: newaction
        action: openaction
        action: saveaction
        @.MenuSeparator{}
        action: quitaction
    }
    @.<Menu> {
        title: qsTr("&Edit")
        action: copyaction
        action: pasteaction
        action: restoreaction
    }
    @.<Menu> {
        title: qsTr("&Dream")
        action: dreamaction
        action: stopaction
        @.MenuSeparator{}
        action: immediateaction
        action: overwriteaction
        action: preferencesaction
    }
    @.<Menu> {
        title: qsTr("&Help")
        action: aboutaction
        @.MenuSeparator{}
        action: presentationaction
        @.MenuSeparator{}
        action: infoaction
    }
}
