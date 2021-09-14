## pbrain-reiner (AlphaBeta AI) is the better AI.

## pbrain-reiner


#### A Python Piskvork with Alpha-Beta Pruning

**pbrain-reiner** is the technical core of a "brain" (AI) for [Piskvork gomoku
manager](http://petr.lastovicka.sweb.cz/piskvork.zip) used in [Gomocup AI
tournament](http://gomocup.org), written in Python.

The code is basically the "Python Improvement" of [C++
template](http://petr.lastovicka.sweb.cz/skel_cpp.zip) written by [Petr
Lastovicka](http://petr.lastovicka.sweb.cz/indexEN.html). This README is also
partially copy of the C++ template's README.

#### Prerequisites and compilation

The Piskvork manager is a Win32 application and currently supports only Win32
compatible .exe files (furthermore whose name starts with pbrain- prefix). There
are several ways how to create .exe from Python files.

Here I present the approach using [PyInstaller](http://pyinstaller.org) and
Windows command line:

1.  Install Windows (or [Wine](https://www.winehq.org/) for Linux and macOS,
    originally the project was created and tested on Windows 10 x64)

2.  Install [Python](http://www.python.org) (the code and also following
    instructions were tested with version 3.8.5-64bit(conda)).

3.  Install [pywin32](https://sourceforge.net/projects/pywin32) Python package:
    `pip.exe install pypiwin32` (if not present "by default")

4.  Install [PyInstaller](https://www.pyinstaller.org/): `pip.exe install
    pyinstaller (Version 4.2)`

To compile the example, use the following command line command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cd C:\path\where\the\files\were\saved
pyinstaller.exe example.py pisqpipe.py --name pbrain-reiner.exe --onefile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: the executables `pip.exe` and `pyinstaller.exe` might need full path.

## pbrain-mcts


#### A Python Piskvork with MCTS with UCT RAVE

To compile the example, use the following command line command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cd C:\path\where\the\files\were\saved
pyinstaller.exe example.py pisqpipe.py --name pbrain-mcts.exe --onefile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: the executables `pip.exe` and `pyinstaller.exe` might need full path.

-   Python 3.7.0 with PyInstaller 4.1 MIGHT have better performance.

-   Packaging using Nuitka MIGHT have better performance.

-   However, Python 3.8.5 with PyInstaller 4.2 is currently the stablest suit.
