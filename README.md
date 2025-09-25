# Automatyczna Cenzura Nagrań

Aplikacja do automatycznego cenzurowania określonych słów w nagraniach audio i wideo.

## Funkcjonalności

- Rozpoznawanie mowy w plikach audio i wideo (z biblioteką SpeechRecognition)
- Automatyczne znajdowanie określonych słów do cenzury
- Zastępowanie słów dźwiękiem cenzury (beep)
- Obsługa formatów audio: MP3, WAV, M4A
- Obsługa formatów wideo: MP4, AVI, MOV (z biblioteką MoviePy)
- Prosty interfejs graficzny
- Wersja demo działająca bez dodatkowych bibliotek

## Dostępne wersje

### 1. Wersja demo (simple_demo.py)
- Działa bez dodatkowych bibliotek
- Obsługuje tylko pliki WAV
- Cenzuruje fragmenty co 5 sekund (tryb demonstracyjny)
- Uruchom: `python simple_demo.py`

### 2. Pełna wersja (main.py)
- Wymaga dodatkowych bibliotek
- Pełne rozpoznawanie mowy
- Obsługa audio i wideo
- Uruchom: `python main.py`

## Instalacja

### Szybka instalacja (Windows)
Uruchom plik `install_dependencies.bat` - automatycznie zainstaluje wszystkie wymagane biblioteki.

### Ręczna instalacja
1. Zainstaluj wymagane biblioteki:
```bash
pip install SpeechRecognition pydub moviepy
```

2. Uruchom wybraną wersję aplikacji:
```bash
# Wersja demo (bez dodatkowych bibliotek)
python simple_demo.py

# Pełna wersja (z rozpoznawaniem mowy)
python main.py
```

## Użycie

### Wersja demo
1. Uruchom `python simple_demo.py`
2. Wybierz plik WAV
3. Opcjonalnie wpisz słowo (w trybie demo nie ma znaczenia)
4. Kliknij "Rozpocznij cenzurę (DEMO)"
5. Zapisz ocenzurowany plik

### Pełna wersja
1. Uruchom `python main.py`
2. Wybierz plik audio lub wideo
3. Wpisz słowo, które ma zostać ocenzurowane
4. Kliknij "Rozpocznij cenzurę"
5. Zapisz ocenzurowany plik

## Jak to działa

### Wersja demo
- Dodaje dźwięk cenzury (beep) co 5 sekund na 1 sekundę
- Nie wymaga rozpoznawania mowy
- Idealna do testowania funkcjonalności

### Pełna wersja
1. **Rozpoznawanie mowy**: Używa Google Speech Recognition API do transkrypcji audio
2. **Znajdowanie słów**: Wyszukuje określone słowo w transkrypcji
3. **Cenzura**: Zastępuje znalezione słowa dźwiękiem beep (1kHz)
4. **Obsługa wideo**: Wyodrębnia audio, cenzuruje je i łączy z oryginalnym wideo

## Wymagania systemowe

- Python 3.8+
- FFmpeg (dla obsługi wideo w pełnej wersji)
- Połączenie internetowe (dla rozpoznawania mowy Google)

## Rozwiązywanie problemów

### Błędy instalacji bibliotek
- Uruchom `install_dependencies.bat` jako administrator
- Lub zainstaluj biblioteki pojedynczo: `pip install SpeechRecognition`

### Problemy z rozpoznawaniem mowy
- Sprawdź połączenie internetowe
- Upewnij się, że nagranie ma dobrą jakość
- Spróbuj z krótszymi plikami audio

### Problemy z wideo
- Zainstaluj FFmpeg: https://ffmpeg.org/download.html
- Dodaj FFmpeg do zmiennej PATH

## Przykłady użycia

- Cenzurowanie przekleństw w podcastach
- Usuwanie imion z nagrań dla anonimowości  
- Cenzurowanie poufnych informacji w nagraniach
- Automatyczne "beepowanie" określonych słów w materiałach wideo