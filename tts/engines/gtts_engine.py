from gtts import gTTS

from .base import TTSEngine


class GTTSEngine(TTSEngine):
    """Google Translate TTS (API 키 불필요, 인터넷 필요)."""

    def __init__(self, lang: str = "ko", slow: bool = False):
        self.lang = lang
        self.slow = slow

    def synthesize(self, text: str, output_path: str) -> None:
        gTTS(text=text, lang=self.lang, slow=self.slow).save(output_path)
