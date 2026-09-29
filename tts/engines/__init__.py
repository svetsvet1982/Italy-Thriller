"""TTS 엔진 레지스트리. 새 엔진은 TTSEngine을 구현하고 ENGINES에 등록한다."""
from .base import TTSEngine
from .gtts_engine import GTTSEngine

ENGINES: dict[str, type[TTSEngine]] = {
    "gtts": GTTSEngine,
}


def get_engine(name: str, **kwargs) -> TTSEngine:
    try:
        return ENGINES[name](**kwargs)
    except KeyError:
        raise ValueError(f"알 수 없는 엔진: {name} (사용 가능: {', '.join(ENGINES)})")
