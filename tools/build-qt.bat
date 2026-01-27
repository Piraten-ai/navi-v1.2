@echo off
set "ROOT=E:\aasd v1.2"
set "SUBST_DRIVE=X:"
subst %SUBST_DRIVE% "%ROOT%" >nul 2>&1
set "SRC=%SUBST_DRIVE%/frontend-qt"
set "BLD=%SUBST_DRIVE%/frontend-qt/build"
set "QT=E:/Qt/6.10.1/mingw_64"
set "MINGW=E:/Qt/Tools/mingw1310_64"
set "CMAKE=E:/aasd v1.2/tools/cmake-3.27.9-windows-x86_64/bin/cmake.exe"
set "PATH=%MINGW%/bin;%QT%/bin;E:/aasd v1.2/tools/cmake-3.27.9-windows-x86_64/bin;%PATH%"
set "MAKE=%MINGW%/bin/mingw32-make.exe"
set "CC=%MINGW%/bin/gcc.exe"
set "CXX=%MINGW%/bin/g++.exe"
rmdir /s /q "%BLD%" 2>nul
"%CMAKE%" -S "%SRC%" -B "%BLD%" -G "MinGW Makefiles" -DCMAKE_PREFIX_PATH="%QT%" -DCMAKE_MAKE_PROGRAM="%MAKE%" -DCMAKE_C_COMPILER="%CC%" -DCMAKE_CXX_COMPILER="%CXX%"
"%CMAKE%" --build "%BLD%"
subst %SUBST_DRIVE% /D >nul 2>&1
