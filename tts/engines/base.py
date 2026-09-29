from abc import ABC, abstractmethod


class TTSEngine(ABC):
    """모든 TTS 엔진이 따르는 공통 인터페이스."""

    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> None:
        """text를 음성으로 변환해 output_path(mp3)에 저장한다."""
