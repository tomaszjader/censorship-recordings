# Automatyczna Cenzura Nagrań

Aplikacja do automatycznego cenzurowania określonych słów w nagraniach audio i wideo.

## Funkcjonalności

- **Zaawansowane rozpoznawanie mowy** z trzema opcjami:
  - OpenAI Whisper API (najlepsza jakość, wymaga klucza API)
  - Lokalny OpenAI Whisper (dobra jakość, działa offline)
  - Google Speech Recognition (podstawowa jakość, wymaga internetu)
- Automatyczne znajdowanie określonych słów do cenzury z precyzyjnymi timestampami
- Zastępowanie słów dźwiękiem cenzury (beep) z zachowaniem oryginalnej długości
- Obsługa formatów audio: MP3, WAV, M4A, MPEG, MPGA, WEBM
- Obsługa formatów wideo: MP4, AVI, MOV (z biblioteką MoviePy)
- Inteligentne dzielenie dużych plików (>25MB) na mniejsze segmenty
- Prosty interfejs graficzny z logami w czasie rzeczywistym
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
pip install -r requirements.txt
```

2. **Konfiguracja OpenAI API (opcjonalna, ale zalecana)**:
   - Skopiuj plik `.env.example` do `.env`
   - Dodaj swój klucz OpenAI API do pliku `.env`:
     ```
     OPENAI_API_KEY=twój_klucz_api_tutaj
     ```
   - Klucz API możesz uzyskać na: https://platform.openai.com/api-keys

3. Uruchom wybraną wersję aplikacji:
```bash
# Wersja demo (bez dodatkowych bibliotek)
python simple_demo.py

# Pełna wersja (z rozpoznawaniem mowy)
python main.py
```

## Konfiguracja rozpoznawania mowy

Aplikacja automatycznie wybiera najlepszą dostępną opcję rozpoznawania mowy:

1. **OpenAI Whisper API** (priorytet 1) - najlepsza jakość <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
   - Wymaga klucza API w pliku `.env`
   - Obsługuje pliki do 25MB
   - Automatyczne dzielenie większych plików
   - Precyzyjne timestampy na poziomie słów
   - Obsługuje 100+ języków

2. **Lokalny OpenAI Whisper** (priorytet 2) - dobra jakość, offline
   - Nie wymaga klucza API
   - Działa offline
   - Wolniejszy niż API

3. **Google Speech Recognition** (priorytet 3) - podstawowa jakość
   - Wymaga połączenia internetowego
   - Darmowy, ale z ograniczeniami

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
1. **Rozpoznawanie mowy**: Używa najlepszej dostępnej metody (OpenAI Whisper API > lokalny Whisper > Google)
2. **Precyzyjne timestampy**: Identyfikuje dokładne pozycje słów w nagraniu <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
3. **Inteligentne dzielenie**: Automatycznie dzieli duże pliki (>25MB) na mniejsze segmenty
4. **Cenzura**: Zastępuje znalezione słowa dźwiękiem beep (1kHz) z zachowaniem oryginalnej długości
5. **Obsługa wideo**: Wyodrębnia audio, cenzuruje je i łączy z oryginalnym wideo

### Techniczne szczegóły OpenAI API

Projekt wykorzystuje najnowsze możliwości OpenAI Whisper API:
- **Model**: `whisper-1` z parametrem `timestamp_granularities=["word"]` <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
- **Format odpowiedzi**: `verbose_json` dla precyzyjnych timestampów
- **Limit plików**: 25MB (automatyczne dzielenie większych plików)
- **Obsługiwane formaty**: mp3, mp4, mpeg, mpga, m4a, wav, webm <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
- **Fallback**: Automatyczne przełączanie na lokalny Whisper w przypadku błędów API

## Wymagania systemowe

- Python 3.8+
- FFmpeg (dla obsługi wideo w pełnej wersji)
- Połączenie internetowe (dla rozpoznawania mowy Google)

## Rozwiązywanie problemów

### Błędy instalacji bibliotek
- Uruchom `install_dependencies.bat` jako administrator
- Lub zainstaluj biblioteki pojedynczo: `pip install openai`

### Problemy z OpenAI API
- Sprawdź czy klucz API jest poprawny w pliku `.env`
- Upewnij się, że masz środki na koncie OpenAI
- Sprawdź limity API na: https://platform.openai.com/usage
- W przypadku błędów API aplikacja automatycznie przełączy się na lokalny Whisper

### Problemy z rozpoznawaniem mowy
- **OpenAI API**: Sprawdź klucz API i saldo konta
- **Lokalny Whisper**: Może wymagać więcej RAM (zalecane 8GB+)
- **Google**: Sprawdź połączenie internetowe
- Upewnij się, że nagranie ma dobrą jakość
- Spróbuj z krótszymi plikami audio

### Problemy z wideo
- Zainstaluj FFmpeg: https://ffmpeg.org/download.html
- Dodaj FFmpeg do zmiennej PATH

### Duże pliki audio
- Pliki >25MB są automatycznie dzielone na mniejsze segmenty <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
- Proces może trwać dłużej dla bardzo dużych plików
- Upewnij się, że masz wystarczająco miejsca na dysku dla plików tymczasowych

## Przykłady użycia

- **Cenzurowanie przekleństw w podcastach** - automatyczne usuwanie niestosownych słów
- **Usuwanie imion z nagrań dla anonimowości** - ochrona prywatności w nagraniach
- **Cenzurowanie poufnych informacji** - usuwanie numerów telefonów, adresów, danych osobowych
- **Automatyczne "beepowanie" określonych słów w materiałach wideo** - przygotowanie treści do publikacji
- **Cenzura brandów i nazw firm** - neutralizacja materiałów marketingowych
- **Usuwanie wulgaryzmów z materiałów edukacyjnych** - przygotowanie treści dla młodszej publiczności

## Koszty użytkowania

### OpenAI Whisper API <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
- **Koszt**: $0.006 za minutę audio
- **Przykład**: 1 godzina audio = $0.36
- **Zalety**: Najlepsza jakość, szybkość, precyzyjne timestampy
- **Limity**: 25MB na plik (automatyczne dzielenie większych plików)

### Alternatywy darmowe
- **Lokalny Whisper**: Całkowicie darmowy, działa offline
- **Google Speech Recognition**: Darmowy z ograniczeniami dziennymi

## Aktualizacje i zgodność

**Ostatnia aktualizacja**: Grudzień 2024

**Zgodność z OpenAI API**:
- ✅ Najnowsze modele Whisper API (whisper-1)
- ✅ Parametr `timestamp_granularities=["word"]` dla precyzyjnych timestampów
- ✅ Format `verbose_json` z pełnymi metadanymi
- ✅ Automatyczne dzielenie plików >25MB
- ✅ Obsługa wszystkich formatów audio obsługiwanych przez API
- ✅ Fallback na lokalny Whisper w przypadku problemów z API

**Planowane funkcje**:
- Obsługa nowych modeli `gpt-4o-transcribe` i `gpt-4o-mini-transcribe` <mcreference link="https://platform.openai.com/docs/guides/speech-to-text" index="2">2</mcreference>
- Wsparcie dla parametru `temperature` do kontroli losowości transkrypcji
- Integracja z Realtime API dla transkrypcji w czasie rzeczywistym