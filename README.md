# Italy-Thriller

## 한국어 TTS 프로토타입 (`tts/`)

텍스트(또는 텍스트 파일)를 한국어 mp3 음성으로 변환하는 간단한 CLI입니다. 기본 엔진은 gTTS(API 키 불필요, 인터넷 필요)입니다.

### 설치

```bash
pip install -r requirements.txt
```

### 사용법

```bash
python -m tts.cli "안녕하세요. 한국어 음성 변환 테스트입니다." -o hello.mp3
python -m tts.cli -f script.txt -o out.mp3      # UTF-8 텍스트 파일
python -m tts.cli "천천히 읽기" --slow -o slow.mp3
```

### 엔진 교체 (클라우드 API / 오픈소스 모델로 확장)

`tts/engines/base.py`의 `TTSEngine`을 구현하고 `tts/engines/__init__.py`의 `ENGINES`에 등록하면 `--engine 이름`으로 선택할 수 있습니다.
API 키는 코드에 넣지 말고 환경 변수(예: `GOOGLE_APPLICATION_CREDENTIALS`, `AZURE_SPEECH_KEY`)로 읽으세요.

### 테스트

```bash
pip install pytest && python -m pytest
```

### 참고

gTTS는 `translate.google.com`에 접속해야 합니다. 네트워크가 이 주소를 막으면 실패합니다.
