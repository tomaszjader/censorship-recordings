import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import wave
import struct
import math

# Sprawdź dostępność pydub dla obsługi MP3
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class SimpleCensorshipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prosta Cenzura Audio - Demo")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        self.input_file = None
        self.output_file = None
        self.word_to_censor = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Tytuł
        title_label = tk.Label(
            self.root, 
            text="Prosta Cenzura Audio - Demo", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # Informacja o demo
        if PYDUB_AVAILABLE:
            info_text = "DEMO: Obsługuje WAV i MP3. Cenzuruje fragmenty co 5 sekund (1 sekunda beep)"
        else:
            info_text = "DEMO: Tylko WAV (zainstaluj pydub dla MP3). Cenzuruje co 5 sekund (1 sekunda beep)"
            
        info_label = tk.Label(
            self.root,
            text=info_text,
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#666'
        )
        info_label.pack(pady=5)
        
        # Frame dla wyboru pliku
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(file_frame, text="Wybierz plik audio:", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        
        file_button_frame = tk.Frame(file_frame, bg='#f0f0f0')
        file_button_frame.pack(fill='x', pady=5)
        
        self.file_button = tk.Button(
            file_button_frame,
            text="Wybierz plik audio",
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
        
        tk.Label(word_frame, text="Słowo do ocenzurowania (opcjonalne):", font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        
        self.word_entry = tk.Entry(
            word_frame,
            textvariable=self.word_to_censor,
            font=("Arial", 12),
            width=30
        )
        self.word_entry.pack(pady=5, fill='x')
        
        # Przycisk cenzury
        self.censor_button = tk.Button(
            self.root,
            text="Rozpocznij cenzurę (DEMO)",
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
            height=6,
            width=60,
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#333'
        )
        self.log_text.pack(fill='both', expand=True)
        
    def log_message(self, message):
        """Dodaje wiadomość do logów"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_file(self):
        """Wybiera plik do cenzury"""
        if PYDUB_AVAILABLE:
            filetypes = [
                ("Pliki audio", "*.wav;*.mp3"),
                ("Pliki WAV", "*.wav"),
                ("Pliki MP3", "*.mp3"),
                ("Wszystkie pliki", "*.*")
            ]
            title = "Wybierz plik audio do cenzury"
        else:
            filetypes = [
                ("Pliki WAV", "*.wav"),
                ("Wszystkie pliki", "*.*")
            ]
            title = "Wybierz plik WAV do cenzury"
        
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename), fg='#333')
            self.censor_button.config(state='normal')
            self.log_message(f"Wybrano plik: {os.path.basename(filename)}")
            
    def start_censoring(self):
        """Rozpoczyna proces cenzury w osobnym wątku"""
        if not self.input_file:
            messagebox.showerror("Błąd", "Wybierz plik audio!")
            return
            
        # Sprawdź czy plik MP3 wymaga pydub
        file_ext = os.path.splitext(self.input_file)[1].lower()
        if file_ext == '.mp3' and not PYDUB_AVAILABLE:
            messagebox.showerror("Błąd", "Pliki MP3 wymagają biblioteki pydub. Zainstaluj ją lub użyj pliku WAV.")
            return
            
        # Wybór pliku wyjściowego
        if file_ext == '.mp3':
            default_ext = ".mp3"
            filetypes = [("Plik MP3", "*.mp3"), ("Plik WAV", "*.wav"), ("Wszystkie pliki", "*.*")]
        else:
            default_ext = ".wav"
            filetypes = [("Plik WAV", "*.wav"), ("Plik MP3", "*.mp3"), ("Wszystkie pliki", "*.*")]
            
        output_file = filedialog.asksaveasfilename(
            title="Zapisz ocenzurowany plik jako...",
            defaultextension=default_ext,
            filetypes=filetypes
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
            self.log_message("Rozpoczynanie cenzury...")
            
            file_ext = os.path.splitext(self.input_file)[1].lower()
            
            if file_ext == '.mp3':
                # Obsługa MP3 przez pydub
                self.log_message("Ładowanie pliku MP3...")
                audio = AudioSegment.from_mp3(self.input_file)
                
                # Konwertuj na WAV dla przetwarzania
                temp_wav = "temp_audio.wav"
                audio.export(temp_wav, format="wav")
                
                # Przetwórz jako WAV
                censored_audio = self.process_wav_file(temp_wav)
                
                # Usuń tymczasowy plik
                os.unlink(temp_wav)
                
                # Zapisz w odpowiednim formacie
                output_ext = os.path.splitext(self.output_file)[1].lower()
                if output_ext == '.mp3':
                    self.log_message("Zapisywanie jako MP3...")
                    censored_audio.export(self.output_file, format="mp3")
                else:
                    self.log_message("Zapisywanie jako WAV...")
                    censored_audio.export(self.output_file, format="wav")
                    
            else:
                # Obsługa WAV (oryginalny kod)
                censored_audio = self.process_wav_file(self.input_file)
                
                # Zapisz w odpowiednim formacie
                output_ext = os.path.splitext(self.output_file)[1].lower()
                if output_ext == '.mp3' and PYDUB_AVAILABLE:
                    self.log_message("Konwertowanie do MP3...")
                    censored_audio.export(self.output_file, format="mp3")
                else:
                    # Zapisz jako WAV (oryginalny sposób)
                    with wave.open(self.output_file, 'wb') as wav_out:
                        wav_out.setparams(censored_audio['params'])
                        wav_out.writeframes(censored_audio['frames'])
                        
            self.log_message("✅ Cenzura zakończona pomyślnie!")
            messagebox.showinfo("Sukces", "Plik został pomyślnie ocenzurowany!")
            
        except Exception as e:
            self.log_message(f"❌ Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas cenzury: {str(e)}")
            
        finally:
            self.progress.stop()
            self.censor_button.config(state='normal')
            self.status_label.config(text="Gotowy do pracy")
            
    def process_wav_file(self, wav_file):
        """Przetwarza plik WAV i dodaje cenzurę"""
        # Otwórz plik WAV
        with wave.open(wav_file, 'rb') as wav_in:
            params = wav_in.getparams()
            frames = wav_in.readframes(params.nframes)
            
        # Sprawdź i ustaw domyślne wartości jeśli nie są określone
        nchannels = params.nchannels if params.nchannels > 0 else 1
        framerate = params.framerate if params.framerate > 0 else 44100
        sampwidth = params.sampwidth if params.sampwidth > 0 else 2
        
        self.log_message(f"Parametry audio: {nchannels} kanały, {framerate} Hz, {sampwidth} bajtów na próbkę")
        
        # Konwertuj na listę próbek
        if sampwidth == 1:
            fmt = 'B'
            max_val = 127
        elif sampwidth == 2:
            fmt = 'h'
            max_val = 32767
        else:
            raise ValueError("Nieobsługiwana szerokość próbki")
            
        samples = list(struct.unpack(f'{len(frames)//sampwidth}{fmt}', frames))
        
        # Generuj beep co 5 sekund
        sample_rate = framerate
        beep_freq = 1000  # 1kHz
        beep_duration = 1.0  # 1 sekunda
        interval = 5.0  # co 5 sekund
        
        beep_samples = int(beep_duration * sample_rate)
        interval_samples = int(interval * sample_rate * nchannels)
        
        self.log_message("Dodawanie dźwięków cenzury...")
        
        censored_count = 0
        for i in range(0, len(samples), interval_samples):
            if i + beep_samples * nchannels < len(samples):
                # Generuj beep
                for j in range(beep_samples):
                    beep_val = int(max_val * 0.3 * math.sin(2 * math.pi * beep_freq * j / sample_rate))
                    for ch in range(nchannels):
                        if i + j * nchannels + ch < len(samples):
                            samples[i + j * nchannels + ch] = beep_val
                censored_count += 1
                self.log_message(f"Dodano cenzurę w pozycji {i//sample_rate//nchannels}s")
        
        self.log_message(f"Dodano {censored_count} fragmentów cenzury.")
        
        # Zwróć przetworzone dane
        if PYDUB_AVAILABLE:
            # Konwertuj z powrotem na AudioSegment
            censored_frames = struct.pack(f'{len(samples)}{fmt}', *samples)
            
            # Utwórz nowe parametry z poprawionymi wartościami
            corrected_params = wave._wave_params(
                nchannels=nchannels,
                sampwidth=sampwidth,
                framerate=framerate,
                nframes=len(samples)//nchannels,
                comptype='NONE',
                compname='not compressed'
            )
            
            # Zapisz do tymczasowego pliku WAV
            temp_censored = "temp_censored.wav"
            with wave.open(temp_censored, 'wb') as wav_out:
                wav_out.setparams(corrected_params)
                wav_out.writeframes(censored_frames)
            
            # Załaduj jako AudioSegment
            result = AudioSegment.from_wav(temp_censored)
            os.unlink(temp_censored)
            return result
        else:
            # Zwróć surowe dane dla zapisu WAV z poprawionymi parametrami
            censored_frames = struct.pack(f'{len(samples)}{fmt}', *samples)
            corrected_params = wave._wave_params(
                nchannels=nchannels,
                sampwidth=sampwidth,
                framerate=framerate,
                nframes=len(samples)//nchannels,
                comptype='NONE',
                compname='not compressed'
            )
            return {'params': corrected_params, 'frames': censored_frames}

def main():
    root = tk.Tk()
    app = SimpleCensorshipApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()