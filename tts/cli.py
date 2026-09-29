"""한국어 텍스트 음성 변환 CLI.

예:
    python -m tts.cli "안녕하세요" -o hello.mp3
    python -m tts.cli -f script.txt -o out.mp3
"""
import argparse
import sys

from .engines import ENGINES, get_engine


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="한국어 텍스트를 mp3 음성으로 변환")
    p.add_argument("text", nargs="?", help="변환할 텍스트")
    p.add_argument("-f", "--file", help="텍스트 파일 경로 (UTF-8)")
    p.add_argument("-o", "--output", default="output.mp3", help="출력 mp3 경로")
    p.add_argument("-e", "--engine", default="gtts", choices=list(ENGINES))
    p.add_argument("--lang", default="ko", help="언어 코드 (기본 ko)")
    p.add_argument("--slow", action="store_true", help="느리게 읽기")
    args = p.parse_args(argv)

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = args.text
    if not text or not text.strip():
        p.error("텍스트 또는 --file 이 필요합니다")

    engine = get_engine(args.engine, lang=args.lang, slow=args.slow)
    engine.synthesize(text.strip(), args.output)
    print(f"저장됨: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
