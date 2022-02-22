#!/bin/bash
# Remove large, unused components in dependencies prior to packaging

rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Assistant.app/
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Designer.app
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/examples
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Linguist.app
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Qt/lib/QtDesigner.framework
# rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Qt/lib/QtDesignerComponents.framework # 5.2 M
# rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Qt/lib/QtShaderTools.framework  # 7.7 Mi
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Qt/lib/QtWebEngineCore.framework
# rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/PySide6/Qt/plugins/virtualkeyboard # 6.4 Mi

rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/tensorflow/include
rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/tensorflow/python/_pywrap_tfcompile.so

# rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/clang # 36 MiB
# rm -rv macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages/grpc # 13 MiB
