:: DONT OVVERIDE:
:: how to use it: "G:\Drive partagés\skmss-ai\automatisation de linstallation de venv requirements.txt installation module activate 20240217_154218.mp4"
:: how to  : https://chat.openai.com/g/g-n7Rs0IK86-grimoire/c/49caee00-54c3-41c6-b983-2b48de80dc25

@echo off
setlocal EnableDelayedExpansion

:: Define a subroutine for the animation
goto :main

:animate
setlocal EnableDelayedExpansion
set "operation=%~1"
set "loading=."
for /L %%i in (1,1,5) do (
    cls
    echo !operation! !loading!
    set "loading=!loading!."
    ping localhost -n 2 >nul
)
endlocal
goto :eof

:main
:: Verify Python installation
echo Verification de Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo Python n'est pas accessible. Assurez-vous que Python est installe et dans votre PATH.
    exit /b %ERRORLEVEL%
)

:: Set environment variables
set "ENV_DIR=%~dp0"
set "ENV_NAME=.venv"
set "REQUIREMENTS_PATH=%ENV_DIR%requirements.txt"

:: Create the virtual environment with animation
echo Creation de l'environnement virtuel %ENV_NAME% dans le repertoire courant...
call :animate "Creation de l'environnement virtuel"
python -m venv "%ENV_DIR%%ENV_NAME%"

:: Activate the virtual environment
echo Activation de l'environnement virtuel...
call "%ENV_DIR%%ENV_NAME%\Scripts\activate.bat"

:: Automatically choose the method to generate requirements.txt
echo Generation de requirements.txt a partir des fichiers Python...
if not exist "%REQUIREMENTS_PATH%" echo. 2> "%REQUIREMENTS_PATH%"
del "%REQUIREMENTS_PATH%"
for /r %%f in (*.py) do (
    findstr /R "^\s*import\s" "%%f" >> "%REQUIREMENTS_PATH%"
    findstr /R "^\s*from\s+.*\s+import\s" "%%f" >> "%REQUIREMENTS_PATH%"
)
:: Manually add the openai module if necessary
:: echo openai>> "%REQUIREMENTS_PATH%"

:: Let the user verify the requirements.txt file
echo.
echo Le fichier requirements.txt a ete genere. Veuillez verifier son contenu avant de continuer.
echo Appuyez sur une touche apres la verification pour continuer...
pause >nul

:: Change to the script's directory
echo Changement du contexte a l'emplacement du script...
cd /d "%ENV_DIR%"

:: Install the modules from requirements.txt with animation
echo Installation des modules a partir de requirements.txt...
call :animate "Installation des modules"
pip install -r "%REQUIREMENTS_PATH%"

echo Les modules ont ete installes avec succes.

:: At the end of your batch script
echo.
echo Copiez et collez la commande suivante:
echo cd /d "%ENV_DIR%" ^&^& call "%ENV_DIR%%ENV_NAME%\Scripts\activate.bat"
echo Ensuite la commande suivante:
echo cd /d "%ENV_DIR%python app.py"
pause


echo Copiez et collez la commande suivante dans votre terminal pour desactiver l'environnement Anaconda, activer l'environnement virtuel et vous positionner dans le repertoire du projet :
echo conda deactivate ^&^& cd /d "%ENV_DIR%" ^&^& call "%ENV_DIR%%ENV_NAME%\Scripts\activate.bat"


endlocal
