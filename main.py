import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import tempfile
import math
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Sprawdź dostępność bibliotek
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Uwaga: SpeechRecognition nie jest zainstalowany. Używanie prostego rozpoznawania.")

try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ OpenAI Whisper dostępny - używanie dla lepszego rozpoznawania polskiej mowy")
except ImportError:
    WHISPER_AVAILABLE = False
    print("Uwaga: OpenAI Whisper nie jest zainstalowany. Używanie Google Speech Recognition.")

try:
    import openai
    from openai import OpenAI
    OPENAI_API_AVAILABLE = True
    # Sprawdź czy klucz API jest dostępny
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        print("✅ OpenAI API klucz załadowany - dostępne Whisper API")
    else:
        print("⚠️ Brak klucza OPENAI_API_KEY w pliku .env - tylko lokalny Whisper")
        OPENAI_API_AVAILABLE = False
except ImportError:
    OPENAI_API_AVAILABLE = False
    print("Uwaga: Biblioteka openai nie jest zainstalowana.")

try:
    from pydub import AudioSegment
    from pydub.generators import Sine
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Uwaga: pydub nie jest zainstalowany. Ograniczona funkcjonalność audio.")

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Uwaga: moviepy nie jest zainstalowany. Brak obsługi wideo.")

class CensorshipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatyczna Cenzura Nagrań")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        self.input_file = None
        self.output_file = None
        self.word_to_censor = tk.StringVar()
        self.whisper_model = tk.StringVar(value="small")  # Domyślny model Whisper
        self.use_api = tk.BooleanVar(value=False)  # Domyślnie używaj lokalnego Whisper
        
        # Stałe dla rozmiaru pliku
        self.MAX_FILE_SIZE_MB = 25
        self.MAX_FILE_SIZE_BYTES = self.MAX_FILE_SIZE_MB * 1024 * 1024
        
        self.setup_ui()
        
    def setup_ui(self):
        # Tytuł
        title_label = tk.Label(
            self.root, 
            text="Automatyczna Cenzura Nagrań", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Sekcja wyboru pliku
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(file_frame, text="Wybierz plik:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        
        file_button_frame = tk.Frame(file_frame, bg='#f0f0f0')
        file_button_frame.pack(fill='x', pady=5)
        
        self.file_button = tk.Button(
            file_button_frame,
            text="Wybierz plik audio/wideo",
            command=self.select_file,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        self.file_button.pack(side='left')
        
        self.file_label = tk.Label(
            file_button_frame,
            text="Nie wybrano pliku",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.file_label.pack(side='left', padx=(10, 0))
        
        # Sekcja słowa do cenzury
        word_frame = tk.Frame(self.root, bg='#f0f0f0')
        word_frame.pack(pady=20, padx=20, fill='x')
        
        tk.Label(word_frame, text="Słowo do ocenzurowania:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        
        self.word_entry = tk.Entry(
            word_frame,
            textvariable=self.word_to_censor,
            font=("Arial", 12),
            width=30
        )
        self.word_entry.pack(pady=5, fill='x')
        
        # Sekcja wyboru modelu Whisper (tylko jeśli dostępny)
        if WHISPER_AVAILABLE:
            model_frame = tk.Frame(self.root, bg='#f0f0f0')
            model_frame.pack(pady=10, padx=20, fill='x')
            
            tk.Label(model_frame, text="Model rozpoznawania mowy:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
            
            model_options = ["tiny", "base", "small", "medium", "large"]
            model_combo = ttk.Combobox(
                model_frame,
                textvariable=self.whisper_model,
                values=model_options,
                state="readonly",
                font=("Arial", 10),
                width=15
            )
            model_combo.pack(pady=5, anchor='w')
            
            # Informacja o modelach
            info_text = "tiny/base: szybkie, small: zalecane, medium/large: dokładniejsze ale wolniejsze"
            tk.Label(
                model_frame, 
                text=info_text, 
                font=("Arial", 9), 
                bg='#f0f0f0', 
                fg='#666'
            ).pack(anchor='w', pady=(2, 0))
        
        # Sekcja wyboru API vs lokalny Whisper
        if WHISPER_AVAILABLE or OPENAI_API_AVAILABLE:
            api_frame = tk.Frame(self.root, bg='#f0f0f0')
            api_frame.pack(pady=10, padx=20, fill='x')
            
            tk.Label(api_frame, text="Sposób rozpoznawania mowy:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
            
            # Checkbox dla API (tylko jeśli dostępne)
            if OPENAI_API_AVAILABLE:
                api_checkbox = tk.Checkbutton(
                    api_frame,
                    text="Użyj OpenAI Whisper API (wymaga klucza w .env)",
                    variable=self.use_api,
                    font=("Arial", 10),
                    bg='#f0f0f0',
                    activebackground='#f0f0f0'
                )
                api_checkbox.pack(anchor='w', pady=5)
                
                # Informacja o różnicach
                api_info = "API: szybsze, dokładniejsze, płatne | Lokalny: darmowy, wymaga więcej RAM"
                tk.Label(
                    api_frame, 
                    text=api_info, 
                    font=("Arial", 9), 
                    bg='#f0f0f0', 
                    fg='#666'
                ).pack(anchor='w', pady=(2, 0))
            else:
                # Informacja o braku API
                no_api_label = tk.Label(
                    api_frame,
                    text="OpenAI API niedostępne - używanie lokalnego Whisper",
                    font=("Arial", 10),
                    bg='#f0f0f0',
                    fg='#666'
                )
                no_api_label.pack(anchor='w', pady=5)
        
        # Przycisk rozpoczęcia cenzury
        self.censor_button = tk.Button(
            self.root,
            text="Rozpocznij cenzurę",
            command=self.start_censoring,
            bg='#FF5722',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            state='disabled'
        )
        self.censor_button.pack(pady=20)
        
        # Pasek postępu
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Gotowy do pracy",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#333'
        )
        self.status_label.pack(pady=5)
        
        # Logi
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(log_frame, text="Logi:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            width=70,
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#333'
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Scrollbar dla logów
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
    def log_message(self, message):
        """Dodaj wiadomość do logów"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def select_file(self):
        """Wybierz plik do przetworzenia"""
        filetypes = [
            ("Pliki audio/wideo", "*.wav *.mp3 *.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4a *.aac *.ogg *.flac"),
            ("Pliki audio", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac"),
            ("Pliki wideo", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
            ("Wszystkie pliki", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Wybierz plik audio lub wideo",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename), fg='#333')
            self.censor_button.config(state='normal')
            self.log_message(f"Wybrano plik: {os.path.basename(filename)}")
            
    def start_censoring(self):
        """Rozpocznij proces cenzurowania w osobnym wątku"""
        if not self.input_file:
            messagebox.showerror("Błąd", "Proszę wybrać plik!")
            return
            
        if not self.word_to_censor.get().strip():
            messagebox.showerror("Błąd", "Proszę podać słowo do ocenzurowania!")
            return
        
        # Wybierz plik wyjściowy
        output_file = filedialog.asksaveasfilename(
            title="Zapisz ocenzurowany plik jako...",
            defaultextension=os.path.splitext(self.input_file)[1],
            filetypes=[
                ("Plik wideo", "*.mp4"),
                ("Plik audio", "*.wav"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if not output_file:
            return
            
        self.output_file = output_file
        
        # Wyłącz przycisk i rozpocznij przetwarzanie
        self.censor_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Przetwarzanie...")
        
        # Uruchom w osobnym wątku
        thread = threading.Thread(target=self.censor_file)
        thread.daemon = True
        thread.start()
        
    def censor_file(self):
        """Główna funkcja cenzurowania pliku"""
        try:
            self.log_message(f"Wybrano plik: {os.path.basename(self.input_file)}")
            
            # Sprawdź czy to plik wideo czy audio
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
            file_extension = os.path.splitext(self.input_file)[1].lower()
            
            if file_extension in video_extensions:
                # Wyciągnij audio z wideo
                self.log_message("Wykryto plik wideo - wyciąganie audio...")
                audio_file = self.extract_audio_from_video()
                if not audio_file:
                    return
            else:
                audio_file = self.input_file
            
            # Konwertuj do WAV jeśli potrzeba
            self.log_message("Konwertowanie audio do formatu WAV...")
            wav_file = self.convert_to_wav(audio_file)
            if not wav_file:
                return
            
            # Rozpoznaj mowę
            self.log_message("Rozpoznawanie mowy...")
            transcription = self.transcribe_audio(wav_file)
            if not transcription:
                return
            
            # Znajdź i ocenzuruj słowo
            word = self.word_to_censor.get().strip().lower()
            self.log_message(f"Szukanie słowa '{word}' w transkrypcji...")
            
            censored_segments = self.find_and_censor_word(transcription['segments'], word, wav_file)
            
            if not censored_segments:
                self.log_message(f"❌ Nie znaleziono słowa '{word}' w nagraniu")
                messagebox.showinfo("Informacja", f"Nie znaleziono słowa '{word}' w nagraniu")
                return
            
            # Zastosuj cenzurę
            self.log_message(f"Znaleziono {len(censored_segments)} wystąpień. Stosowanie cenzury...")
            censored_audio = self.apply_censorship(wav_file, censored_segments)
            
            if file_extension in video_extensions:
                # Połącz z wideo
                self.log_message("Łączenie ocenzurowanego audio z wideo...")
                self.combine_audio_with_video(censored_audio)
            else:
                # Skopiuj ocenzurowane audio
                import shutil
                shutil.copy2(censored_audio, self.output_file)
            
            self.log_message("✅ Cenzura zakończona pomyślnie!")
            messagebox.showinfo("Sukces", f"Plik został ocenzurowany i zapisany jako:\n{self.output_file}")
            
        except Exception as e:
            self.log_message(f"❌ Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas przetwarzania:\n{str(e)}")
        finally:
            # Przywróć interfejs
            self.progress.stop()
            self.censor_button.config(state='normal')
            self.status_label.config(text="Gotowy do pracy")
            
    def extract_audio_from_video(self):
        """Wyciągnij audio z pliku wideo"""
        if not MOVIEPY_AVAILABLE:
            self.log_message("❌ Nie można wyciągnąć audio - brak biblioteki moviepy")
            return None
            
        try:
            video = mp.VideoFileClip(self.input_file)
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            video.audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
            video.close()
            return temp_audio.name
        except Exception as e:
            self.log_message(f"❌ Błąd wyciągania audio: {str(e)}")
            return None
            
    def convert_to_wav(self, audio_file):
        """Konwertuj plik audio do formatu WAV"""
        if audio_file.lower().endswith('.wav'):
            return audio_file
            
        if not PYDUB_AVAILABLE:
            self.log_message("❌ Nie można konwertować - brak biblioteki pydub")
            return None
            
        try:
            audio = AudioSegment.from_file(audio_file)
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_wav.name, format='wav')
            return temp_wav.name
        except Exception as e:
            self.log_message(f"❌ Błąd konwersji: {str(e)}")
            return None
            
    def transcribe_audio(self, wav_file):
        """Rozpoznaj mowę w pliku audio"""
        # Sprawdź rozmiar pliku
        file_size = os.path.getsize(wav_file)
        
        # Wybierz metodę transkrypcji
        if OPENAI_API_AVAILABLE and self.use_api.get():
            self.log_message("Używanie OpenAI Whisper API...")
            return self.transcribe_with_whisper_api(wav_file)
        elif WHISPER_AVAILABLE:
            self.log_message(f"Ładowanie modelu Whisper: {self.whisper_model.get()}")
            return self.transcribe_with_whisper(wav_file)
        elif SPEECH_RECOGNITION_AVAILABLE:
            self.log_message("Używanie Google Speech Recognition...")
            return self.transcribe_with_google(wav_file)
        else:
            self.log_message("❌ Brak dostępnych metod rozpoznawania mowy")
            return None
            
    def transcribe_with_whisper_api(self, wav_file, is_segment=False):
        """Rozpoznaj mowę używając OpenAI Whisper API"""
        try:
            # Sprawdź rozmiar pliku
            file_size = os.path.getsize(wav_file)
            if file_size > self.MAX_FILE_SIZE_BYTES and not is_segment:
                self.log_message(f"📂 Plik jest za duży ({file_size / (1024*1024):.1f}MB). Dzielenie na mniejsze części...")
                return self.transcribe_large_file_with_api(wav_file)
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            with open(wav_file, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Konwertuj format odpowiedzi do zgodnego z lokalnym Whisper
            segments = []
            if hasattr(transcript, 'words') and transcript.words:
                current_segment = {
                    'start': 0,
                    'end': 0,
                    'text': '',
                    'words': []
                }
                
                for word in transcript.words:
                    if not current_segment['words']:
                        current_segment['start'] = word.start
                    
                    current_segment['end'] = word.end
                    current_segment['text'] += word.word + ' '
                    current_segment['words'].append({
                        'start': word.start,
                        'end': word.end,
                        'word': word.word.strip(),
                        'probability': getattr(word, 'probability', 1.0)
                    })
                
                if current_segment['words']:
                    current_segment['text'] = current_segment['text'].strip()
                    segments.append(current_segment)
            
            return {
                'segments': segments
            }
            
        except Exception as e:
            error_msg = str(e)
            if "413" in error_msg:
                self.log_message(f"❌ Błąd Whisper API: {error_msg}")
                self.log_message("Próba użycia lokalnego Whisper jako fallback...")
                return self.transcribe_with_whisper(wav_file)
            else:
                self.log_message(f"❌ Błąd Whisper API: {error_msg}")
                if WHISPER_AVAILABLE:
                    self.log_message("Próba użycia lokalnego Whisper jako fallback...")
                    return self.transcribe_with_whisper(wav_file)
                return None
    
    def transcribe_large_file_with_api(self, wav_file):
        """Podziel duży plik audio i transkrybuj każdy segment używając API"""
        try:
            segments = self.split_audio_file(wav_file)
            
            all_segments = []
            for i, segment_file in enumerate(segments):
                self.log_message(f"Przetwarzanie segmentu {i+1}/{len(segments)}...")
                result = self.transcribe_with_whisper_api(segment_file, is_segment=True)
                if result and 'segments' in result:
                    all_segments.extend(result['segments'])
                
                # Usuń tymczasowy segment
                if segment_file != wav_file:
                    try:
                        os.unlink(segment_file)
                    except:
                        pass
            
            return {'segments': all_segments}
        except Exception as e:
            self.log_message(f"❌ Błąd podczas dzielenia pliku: {str(e)}")
            # Fallback do lokalnego Whisper
            if WHISPER_AVAILABLE:
                self.log_message("Próba użycia lokalnego Whisper jako fallback...")
                return self.transcribe_with_whisper(wav_file)
            return None

    def transcribe_with_whisper(self, wav_file):
        """Rozpoznaj mowę używając lokalnego Whisper"""
        try:
            model = whisper.load_model(self.whisper_model.get())
            self.log_message("Model załadowany, rozpoczynanie transkrypcji...")
            
            result = model.transcribe(wav_file, language='pl', word_timestamps=True)
            
            return {
                'segments': result['segments']
            }
            
        except Exception as e:
            self.log_message(f"❌ Błąd lokalnego Whisper: {str(e)}")
            if SPEECH_RECOGNITION_AVAILABLE:
                self.log_message("Próba użycia Google Speech Recognition jako fallback...")
                return self.transcribe_with_google(wav_file)
            return None
            
    def transcribe_with_google(self, wav_file):
        """Rozpoznaj mowę używając Google Speech Recognition (fallback)"""
        try:
            r = sr.Recognizer()
            
            with sr.AudioFile(wav_file) as source:
                audio = r.record(source)
            
            text = r.recognize_google(audio, language='pl-PL')
            
            # Utwórz prosty segment (bez timestampów słów)
            audio_duration = self.get_audio_duration(wav_file)
            
            segment = {
                'start': 0.0,
                'end': audio_duration,
                'text': text,
                'words': []  # Google SR nie dostarcza timestampów słów
            }
            
            # Podziel tekst na słowa i przypisz przybliżone timestampy
            words = text.split()
            if words:
                word_duration = audio_duration / len(words)
                for i, word in enumerate(words):
                    word_start = i * word_duration
                    word_end = (i + 1) * word_duration
                    segment['words'].append({
                        'start': word_start,
                        'end': word_end,
                        'word': word,
                        'probability': 1.0
                    })
            
            return {
                'segments': [segment]
            }
            
        except Exception as e:
            self.log_message(f"❌ Błąd Google Speech Recognition: {str(e)}")
            return None
            
    def get_audio_duration(self, wav_file):
        """Pobierz długość pliku audio"""
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_wav(wav_file)
                return len(audio) / 1000.0  # Konwertuj ms na sekundy
            except:
                pass
        return 60.0  # Domyślna wartość jeśli nie można określić
        
    def find_and_censor_word(self, segments, word, wav_file):
        """Znajdź wystąpienia słowa w segmentach i zwróć informacje o cenzurze"""
        censored_segments = []
        word_lower = word.lower()
        
        for segment in segments:
            segment_text = segment['text'].lower()
            
            # Sprawdź czy słowo występuje w segmencie
            if word_lower in segment_text:
                # Jeśli mamy timestampy słów, użyj ich
                if 'words' in segment and segment['words']:
                    for word_info in segment['words']:
                        if word_lower in word_info['word'].lower():
                            censored_segments.append({
                                'start': word_info['start'],
                                'end': word_info['end'],
                                'word': word_info['word']
                            })
                            self.log_message(f"Znaleziono '{word_info['word']}' w czasie {word_info['start']:.2f}s - {word_info['end']:.2f}s")
                else:
                    # Fallback: użyj całego segmentu
                    censored_segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'word': word
                    })
                    self.log_message(f"Znaleziono '{word}' w segmencie {segment['start']:.2f}s - {segment['end']:.2f}s")
        
        return censored_segments
        
    def apply_censorship(self, wav_file, censored_segments):
        """Zastosuj cenzurę do pliku audio"""
        if not PYDUB_AVAILABLE:
            self.log_message("❌ Nie można zastosować cenzury - brak biblioteki pydub")
            return None
            
        try:
            audio = AudioSegment.from_wav(wav_file)
            
            # Utwórz dźwięk cenzury (beep)
            beep_duration = 1000  # 1 sekunda w ms
            beep_freq = 1000  # 1000 Hz
            beep = Sine(beep_freq).to_audio_segment(duration=beep_duration)
            
            # Zastosuj cenzurę dla każdego segmentu (od końca do początku, żeby nie zmieniać indeksów)
            for segment in reversed(censored_segments):
                start_ms = int(segment['start'] * 1000)
                end_ms = int(segment['end'] * 1000)
                
                # Upewnij się, że nie przekraczamy długości audio
                end_ms = min(end_ms, len(audio))
                
                if start_ms < end_ms:
                    # Dostosuj długość beepa do długości słowa
                    word_duration = end_ms - start_ms
                    if word_duration < len(beep):
                        beep_adjusted = beep[:word_duration]
                    else:
                        beep_adjusted = beep
                    
                    # Zastąp fragment beepem
                    audio = audio[:start_ms] + beep_adjusted + audio[end_ms:]
            
            # Zapisz ocenzurowane audio
            temp_censored = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_censored.name, format='wav')
            
            return temp_censored.name
            
        except Exception as e:
            self.log_message(f"❌ Błąd stosowania cenzury: {str(e)}")
            return None
            
    def combine_audio_with_video(self, censored_audio):
        """Połącz ocenzurowane audio z oryginalnym wideo"""
        if not MOVIEPY_AVAILABLE:
            self.log_message("❌ Nie można połączyć z wideo - brak biblioteki moviepy")
            return
            
        try:
            # Utwórz tymczasowy plik audio
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            # Skopiuj ocenzurowane audio
            import shutil
            shutil.copy2(censored_audio, temp_audio.name)
            
            # Załaduj oryginalne wideo i zastąp audio
            video = mp.VideoFileClip(self.input_file)
            new_audio = mp.AudioFileClip(temp_audio.name)
            
            final_video = video.set_audio(new_audio)
            final_video.write_videofile(self.output_file, verbose=False, logger=None)
            
            video.close()
            new_audio.close()
            final_video.close()
            
            os.unlink(temp_audio.name)
            
        except Exception as e:
            self.log_message(f"❌ Błąd łączenia z wideo: {str(e)}")
            
    def split_audio_file(self, wav_file, max_size_mb=20):
        """Dzieli plik audio na mniejsze części jeśli przekracza maksymalny rozmiar"""
        if not PYDUB_AVAILABLE:
            self.log_message("❌ Nie można podzielić pliku - brak biblioteki pydub")
            return [wav_file]
        
        file_size = os.path.getsize(wav_file)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size <= max_size_bytes:
            return [wav_file]
        
        self.log_message(f"📂 Plik jest za duży ({file_size / (1024*1024):.1f}MB). Dzielenie na mniejsze części...")
        
        try:
            audio = AudioSegment.from_wav(wav_file)
            
            # Oblicz ile segmentów potrzebujemy
            num_segments = (file_size // max_size_bytes) + 1
            segment_duration = len(audio) // num_segments
            
            segments = []
            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, len(audio))
                
                segment = audio[start_time:end_time]
                
                # Zapisz segment do tymczasowego pliku
                temp_segment = tempfile.NamedTemporaryFile(suffix=f'_segment_{i}.wav', delete=False)
                segment.export(temp_segment.name, format='wav')
                segments.append(temp_segment.name)
                
                self.log_message(f"Utworzono segment {i+1}/{num_segments}: {os.path.basename(temp_segment.name)}")
            
            return segments
            
        except Exception as e:
            self.log_message(f"❌ Błąd dzielenia pliku: {str(e)}")
            return [wav_file]
    
    def merge_transcription_results(self, results, segment_durations):
        """Łączy wyniki transkrypcji z podzielonych segmentów"""
        merged_segments = []
        time_offset = 0
        
        for i, result in enumerate(results):
            if result and 'segments' in result:
                for segment in result['segments']:
                    # Dostosuj timestampy
                    adjusted_segment = segment.copy()
                    adjusted_segment['start'] += time_offset
                    adjusted_segment['end'] += time_offset
                    
                    # Dostosuj timestampy słów jeśli istnieją
                    if 'words' in adjusted_segment:
                        adjusted_words = []
                        for word in adjusted_segment['words']:
                            adjusted_word = word.copy()
                            adjusted_word['start'] += time_offset
                            adjusted_word['end'] += time_offset
                            adjusted_words.append(adjusted_word)
                        adjusted_segment['words'] = adjusted_words
                    
                    merged_segments.append(adjusted_segment)
            
            # Dodaj czas trwania tego segmentu do offsetu
            if i < len(segment_durations):
                time_offset += segment_durations[i]
        
        return {'segments': merged_segments}

def main():
    root = tk.Tk()
    app = CensorshipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()