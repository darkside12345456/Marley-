"""Voz no terminal (opcional).

Reconhecimento de fala (STT) e síntese de fala (TTS). As dependências são
opcionais: se não estiverem instaladas, o Jarvis usa o teclado como alternativa.

Para instalar tudo:  pip install -r requirements-voz.txt
"""
from __future__ import annotations


class Voice:
    def __init__(self, language: str = "pt-PT"):
        self.language = language
        self._tts = None
        self._recognizer = None
        self._mic = None
        self._init_tts()
        self._init_stt()

    # --- Síntese de fala (falar) ---
    def _init_tts(self) -> None:
        try:
            import pyttsx3

            self._tts = pyttsx3.init()
            self._tts.setProperty("rate", 175)
            self._escolher_voz_feminina()
        except Exception:
            self._tts = None

    def _escolher_voz_feminina(self) -> None:
        """Tenta escolher uma voz feminina (a Sonny é do género feminino)."""
        hints = ("female", "mulher", "joana", "maria", "catarina", "ines", "inês",
                 "luciana", "fernanda", "helena", "helia", "raquel", "zira", "hazel")
        try:
            vozes = self._tts.getProperty("voices")
        except Exception:
            return
        melhor = None
        for v in vozes or []:
            nome = (getattr(v, "name", "") or "").lower()
            genero = (getattr(v, "gender", "") or "").lower()
            idiomas = " ".join(str(x) for x in (getattr(v, "languages", []) or [])).lower()
            if "female" in genero or any(h in nome for h in hints):
                melhor = v.id
                if "pt" in nome or "pt" in idiomas:
                    break
        if melhor:
            try:
                self._tts.setProperty("voice", melhor)
            except Exception:
                pass

    def say(self, text: str) -> None:
        print(f"🤖 {text}")
        if self._tts is not None:
            try:
                self._tts.say(text)
                self._tts.runAndWait()
            except Exception:
                pass

    # --- Reconhecimento de fala (ouvir) ---
    def _init_stt(self) -> None:
        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone()
        except Exception:
            self._recognizer = None
            self._mic = None

    @property
    def can_listen(self) -> bool:
        return self._recognizer is not None and self._mic is not None

    def listen(self) -> str:
        if not self.can_listen:
            return input("🎤 (escreve) > ").strip()
        import speech_recognition as sr

        with self._mic as source:
            print("🎤 A ouvir…")
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self._recognizer.listen(source, phrase_time_limit=15)
        try:
            texto = self._recognizer.recognize_google(audio, language=self.language)
            print(f"👤 {texto}")
            return texto
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("(reconhecimento online indisponível — escreve)")
            return input("🎤 (escreve) > ").strip()
