REM REQUIRES: pyinstaller
REM note the use of the ^ to continue the command on the next line, must be at the end of the line and not followed by a space


REM Build the executable for the process supervisor using pyinstaller with console
pyinstaller --icon=img\icon.png --onefile --name=processsupervisor main_tksupervisor.py --distpath=dist --workpath=build ^
--exclude-module matplotlib --exclude-module qt5 --exclude-module numpy --exclude-module scipy 

REM Build the executable for the process supervisor using pyinstaller without console
REM the exclusion so that the executable is smaller
pyinstaller --icon=img\icon.png --onefile --noconsole --name=processsupervisorw main_tksupervisor.py --distpath=dist --workpath=build ^
--exclude-module matplotlib --exclude-module qt5 --exclude-module numpy --exclude-module scipy 