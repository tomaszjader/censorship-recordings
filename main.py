import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import tempfile

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
        
        # Frame dla wyboru pliku
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
        
        # Frame dla słowa do cenzury
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
        
        # Frame dla wyboru modelu Whisper (tylko jeśli dostępny)
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
        
        # Przycisk cenzury
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
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Gotowy do pracy",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#333'
        )
        self.status_label.pack(pady=5)
        
        # Obszar logów
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
        """Dodaje wiadomość do logów"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_file(self):
        """Wybiera plik do cenzury"""
        filetypes = [
            ("Wszystkie obsługiwane", "*.mp3;*.wav;*.m4a;*.mp4;*.avi;*.mov"),
            ("Pliki audio", "*.mp3;*.wav;*.m4a"),
            ("Pliki wideo", "*.mp4;*.avi;*.mov"),
            ("Wszystkie pliki", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Wybierz plik do cenzury",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename), fg='#333')
            self.censor_button.config(state='normal')
            self.log_message(f"Wybrano plik: {os.path.basename(filename)}")
            
    def start_censoring(self):
        """Rozpoczyna proces cenzury w osobnym wątku"""
        if not self.input_file or not self.word_to_censor.get().strip():
            messagebox.showerror("Błąd", "Wybierz plik i wpisz słowo do cenzury!")
            return
            
        # Wybór pliku wyjściowego
        output_file = filedialog.asksaveasfilename(
            title="Zapisz ocenzurowany plik jako...",
            defaultextension=os.path.splitext(self.input_file)[1],
            filetypes=[
                ("Plik audio", "*.mp3"),
                ("Plik wideo", "*.mp4"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        if not output_file:
            return
            
        self.output_file = output_file
        
        # Uruchom cenzurę w osobnym wątku
        self.censor_button.config(state='disabled')
        self.progress.start()
        
        thread = threading.Thread(target=self.censor_file)
        thread.daemon = True
        thread.start()
        
    def censor_file(self):
        """Główna funkcja cenzury"""
        try:
            self.status_label.config(text="Przetwarzanie...")
            word = self.word_to_censor.get().strip().lower()
            
            if not PYDUB_AVAILABLE:
                messagebox.showerror("Błąd", "Brak wymaganych bibliotek audio. Zainstaluj pydub.")
                return
            
            # Sprawdź czy to plik wideo czy audio
            file_ext = os.path.splitext(self.input_file)[1].lower()
            is_video = file_ext in ['.mp4', '.avi', '.mov']
            
            if is_video and not MOVIEPY_AVAILABLE:
                messagebox.showerror("Błąd", "Brak obsługi wideo. Zainstaluj moviepy.")
                return
            
            if is_video:
                self.log_message("Wykryto plik wideo - wyodrębnianie audio...")
                audio_file = self.extract_audio_from_video()
            else:
                audio_file = self.input_file
                
            self.log_message("Konwertowanie audio do formatu WAV...")
            wav_file = self.convert_to_wav(audio_file)
            
            if SPEECH_RECOGNITION_AVAILABLE:
                self.log_message("Rozpoznawanie mowy...")
                segments = self.transcribe_audio(wav_file)
                
                self.log_message(f"Szukanie słowa '{word}' w nagraniu...")
                censored_segments = self.find_and_censor_word(segments, word, wav_file)
            else:
                # Fallback - cenzuruj całe nagranie co 5 sekund (demo)
                self.log_message("Używanie trybu demo - cenzura co 5 sekund...")
                audio = AudioSegment.from_wav(wav_file)
                censored_segments = []
                for i in range(0, len(audio), 5000):  # co 5 sekund
                    censored_segments.append({
                        'start': i,
                        'end': min(i + 1000, len(audio))  # 1 sekunda cenzury
                    })
                
            if not censored_segments:
                self.log_message(f"Nie znaleziono słowa '{word}' w nagraniu.")
                messagebox.showinfo("Info", f"Nie znaleziono słowa '{word}' w nagraniu.")
                return
                
            self.log_message(f"Znaleziono {len(censored_segments)} wystąpień do cenzury")
            censored_audio = self.apply_censorship(wav_file, censored_segments)
            
            if is_video:
                self.log_message("Łączenie ocenzurowanego audio z wideo...")
                self.combine_audio_with_video(censored_audio)
            else:
                self.log_message("Zapisywanie ocenzurowanego audio...")
                censored_audio.export(self.output_file, format="mp3")
                
            self.log_message("✅ Cenzura zakończona pomyślnie!")
            messagebox.showinfo("Sukces", "Plik został pomyślnie ocenzurowany!")
            
        except Exception as e:
            self.log_message(f"❌ Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas cenzury: {str(e)}")
            
        finally:
            self.progress.stop()
            self.censor_button.config(state='normal')
            self.status_label.config(text="Gotowy do pracy")
            
    def extract_audio_from_video(self):
        """Wyodrębnia audio z pliku wideo"""
        video = mp.VideoFileClip(self.input_file)
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio.close()  # Zamknij plik przed użyciem
        video.audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
        video.close()
        return temp_audio.name
        
    def convert_to_wav(self, audio_file):
        """Konwertuje plik audio do formatu WAV"""
        audio = AudioSegment.from_file(audio_file)
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav.close()  # Zamknij plik przed użyciem
        audio.export(temp_wav.name, format="wav")
        return temp_wav.name
        
    def transcribe_audio(self, wav_file):
        """Rozpoznaje mowę w pliku audio używając OpenAI Whisper lub Google Speech Recognition"""
        
        if WHISPER_AVAILABLE:
            return self.transcribe_with_whisper(wav_file)
        elif SPEECH_RECOGNITION_AVAILABLE:
            return self.transcribe_with_google(wav_file)
        else:
            raise Exception("Brak dostępnych bibliotek do rozpoznawania mowy!")
    
    def transcribe_with_whisper(self, wav_file):
        """Rozpoznaje mowę używając OpenAI Whisper"""
        self.log_message(f"Ładowanie modelu Whisper: {self.whisper_model.get()}")
        
        try:
            model = whisper.load_model(self.whisper_model.get())
            self.log_message("Model załadowany, rozpoczynanie transkrypcji...")
            
            # Whisper automatycznie dzieli audio na segmenty i zwraca timestampy
            result = model.transcribe(wav_file, language='pl', word_timestamps=True)
            
            segments = []
            
            # Przetwarzaj segmenty z Whisper
            for segment in result['segments']:
                segment_data = {
                    'start_time': int(segment['start'] * 1000),  # Konwertuj na milisekundy
                    'end_time': int(segment['end'] * 1000),
                    'text': segment['text'].lower().strip(),
                    'words': []  # Dodajemy informacje o pojedynczych słowach
                }
                
                # Jeśli dostępne są timestampy słów, dodaj je
                if 'words' in segment:
                    for word_info in segment['words']:
                        segment_data['words'].append({
                            'word': word_info['word'].lower().strip(),
                            'start': int(word_info['start'] * 1000),
                            'end': int(word_info['end'] * 1000)
                        })
                
                segments.append(segment_data)
                
                start_sec = segment['start']
                end_sec = segment['end']
                self.log_message(f"Segment {start_sec:.1f}s-{end_sec:.1f}s: {segment['text']}")
            
            self.log_message(f"✅ Transkrypcja Whisper zakończona. Znaleziono {len(segments)} segmentów.")
            return segments
            
        except Exception as e:
            self.log_message(f"❌ Błąd Whisper: {str(e)}")
            # Fallback do Google Speech Recognition jeśli dostępne
            if SPEECH_RECOGNITION_AVAILABLE:
                self.log_message("Próba użycia Google Speech Recognition jako fallback...")
                return self.transcribe_with_google(wav_file)
            else:
                raise e
    
    def transcribe_with_google(self, wav_file):
        """Rozpoznaje mowę używając Google Speech Recognition (oryginalny kod)"""
        r = sr.Recognizer()
        
        # Podziel audio na segmenty (co 30 sekund)
        audio = AudioSegment.from_wav(wav_file)
        segment_length = 30 * 1000  # 30 sekund w milisekundach
        segments = []
        
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i + segment_length]
            
            # Zapisz segment do tymczasowego pliku
            temp_segment = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_segment.close()  # Zamknij plik przed użyciem
            segment.export(temp_segment.name, format="wav")
            
            try:
                with sr.AudioFile(temp_segment.name) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language='pl-PL')
                    
                    segments.append({
                        'start_time': i,
                        'end_time': min(i + segment_length, len(audio)),
                        'text': text.lower(),
                        'words': []  # Google SR nie zwraca timestampów słów
                    })
                    
                    self.log_message(f"Segment {i//1000}s-{min((i + segment_length)//1000, len(audio)//1000)}s: {text}")
                    
            except sr.UnknownValueError:
                self.log_message(f"Nie można rozpoznać mowy w segmencie {i//1000}s-{min((i + segment_length)//1000, len(audio)//1000)}s")
            except sr.RequestError as e:
                self.log_message(f"Błąd serwisu rozpoznawania mowy: {e}")
                
            os.unlink(temp_segment.name)
            
        return segments
        
    def find_and_censor_word(self, segments, word, wav_file):
        """Znajduje wystąpienia słowa w segmentach z ulepszoną dokładnością timestampów"""
        import re
        censored_segments = []
        
        # Przygotuj wzorzec do dokładnego dopasowania słowa (z granicami słów)
        word_pattern = r'\b' + re.escape(word.lower()) + r'\b'
        
        for segment in segments:
            # Znajdź wszystkie wystąpienia słowa w tekście segmentu
            matches = list(re.finditer(word_pattern, segment['text'].lower()))
            
            if matches:
                # Jeśli mamy timestampy słów z Whisper, użyj ich dla większej dokładności
                if segment.get('words') and len(segment['words']) > 0:
                    self.log_message(f"Używanie precyzyjnych timestampów słów z Whisper")
                    
                    for word_info in segment['words']:
                        # Sprawdź czy to słowo pasuje do wzorca
                        if re.search(word_pattern, word_info['word'].lower()):
                            censored_segments.append({
                                'start': word_info['start'],
                                'end': word_info['end']
                            })
                            
                            self.log_message(f"✅ Znaleziono precyzyjne dopasowanie '{word_info['word']}' w pozycji {word_info['start']//1000:.1f}s-{word_info['end']//1000:.1f}s")
                else:
                    # Fallback do oryginalnej metody dla Google Speech Recognition
                    self.log_message(f"Używanie przybliżonych timestampów (brak danych o słowach)")
                    
                    words = segment['text'].split()
                    segment_duration = segment['end_time'] - segment['start_time']
                    
                    for match in matches:
                        # Znajdź pozycję słowa w liście słów
                        text_before_match = segment['text'][:match.start()].lower()
                        words_before = len(text_before_match.split())
                        
                        # Oblicz przybliżoną pozycję czasową
                        if len(words) > 0:
                            word_start = segment['start_time'] + (words_before / len(words)) * segment_duration
                            word_end = segment['start_time'] + ((words_before + 1) / len(words)) * segment_duration
                        else:
                            word_start = segment['start_time']
                            word_end = segment['end_time']
                        
                        censored_segments.append({
                            'start': word_start,
                            'end': word_end
                        })
                        
                        matched_word = match.group()
                        self.log_message(f"⚠️ Znaleziono przybliżone dopasowanie '{matched_word}' w pozycji {word_start//1000:.1f}s-{word_end//1000:.1f}s")
        
        # Sortuj segmenty według czasu rozpoczęcia
        censored_segments.sort(key=lambda x: x['start'])
        
        # Usuń nakładające się segmenty
        if len(censored_segments) > 1:
            merged_segments = []
            current = censored_segments[0]
            
            for next_segment in censored_segments[1:]:
                # Jeśli segmenty się nakładają lub są bardzo blisko siebie (mniej niż 100ms)
                if next_segment['start'] <= current['end'] + 100:
                    # Połącz segmenty
                    current['end'] = max(current['end'], next_segment['end'])
                else:
                    merged_segments.append(current)
                    current = next_segment
            
            merged_segments.append(current)
            censored_segments = merged_segments
            
            self.log_message(f"Połączono nakładające się segmenty. Finalna liczba: {len(censored_segments)}")
                        
        return censored_segments
        
    def apply_censorship(self, wav_file, censored_segments):
        """Zastępuje znalezione słowa dźwiękiem cenzury"""
        audio = AudioSegment.from_wav(wav_file)
        
        # Generuj dźwięk cenzury (beep)
        beep_freq = 1000  # 1kHz
        
        for segment in censored_segments:
            start_ms = int(segment['start'])
            end_ms = int(segment['end'])
            duration = end_ms - start_ms
            
            # Generuj beep o odpowiedniej długości
            beep = Sine(beep_freq).to_audio_segment(duration=duration)
            
            # Dostosuj głośność beep do otoczenia
            original_volume = audio[start_ms:end_ms].dBFS
            beep = beep + (original_volume - beep.dBFS)
            
            # Zastąp fragment beepem
            audio = audio[:start_ms] + beep + audio[end_ms:]
            
        return audio
        
    def combine_audio_with_video(self, censored_audio):
        """Łączy ocenzurowane audio z oryginalnym wideo"""
        # Zapisz ocenzurowane audio do tymczasowego pliku
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio.close()  # Zamknij plik przed użyciem
        censored_audio.export(temp_audio.name, format="wav")
        
        # Załaduj oryginalne wideo i zastąp audio
        video = mp.VideoFileClip(self.input_file)
        new_audio = mp.AudioFileClip(temp_audio.name)
        
        final_video = video.set_audio(new_audio)
        final_video.write_videofile(self.output_file, verbose=False, logger=None)
        
        video.close()
        new_audio.close()
        final_video.close()
        
        os.unlink(temp_audio.name)

def main():
    root = tk.Tk()
    app = CensorshipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()