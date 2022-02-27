rem  Remove large, unused components in dependencies prior to packaging

rmdir windows\msi\Cook-a-Dream\src\app_packages\PySide6\examples /s /q
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\QtWebEngine*.*
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\Qt6WebEngine*.*

del windows\msi\Cook-a-Dream\src\app_packages\PySide6\assistant.exe
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\designer.exe
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\linguist.exe
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\lrelease.exe
del windows\msi\Cook-a-Dream\src\app_packages\PySide6\lupdate.exe

rmdir windows\msi\Cook-a-Dream\src\app_packages\tensorflow\include /s /q
del windows\msi\Cook-a-Dream\src\app_packages\tensorflow\python\_pywrap_tfcompile.pyd
