@echo off
echo Instalowanie bibliotek dla aplikacji cenzury...
echo.

echo Instalowanie podstawowych bibliotek...
pip install SpeechRecognition
if %errorlevel% neq 0 (
    echo Błąd podczas instalacji SpeechRecognition
    pause
    exit /b 1
)

pip install pydub
if %errorlevel% neq 0 (
    echo Błąd podczas instalacji pydub
    pause
    exit /b 1
)

pip install moviepy
if %errorlevel% neq 0 (
    echo Błąd podczas instalacji moviepy
    pause
    exit /b 1
)

echo.
echo ✅ Instalacja zakończona pomyślnie!
echo.
echo Możesz teraz uruchomić:
echo - python simple_demo.py (wersja demo bez dodatkowych bibliotek)
echo - python main.py (pełna wersja z rozpoznawaniem mowy)
echo.
pause