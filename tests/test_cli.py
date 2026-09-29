from unittest.mock import patch

from tts import cli


def test_text_argument_saves_file(tmp_path):
    out = tmp_path / "a.mp3"
    with patch("tts.engines.gtts_engine.gTTS") as g:
        g.return_value.save.side_effect = lambda p: open(p, "wb").write(b"ID3")
        assert cli.main(["안녕하세요", "-o", str(out)]) == 0
    g.assert_called_once_with(text="안녕하세요", lang="ko", slow=False)
    assert out.exists()


def test_file_input(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("한국어 문장\n", encoding="utf-8")
    with patch("tts.engines.gtts_engine.gTTS") as g:
        cli.main(["-f", str(src), "-o", str(tmp_path / "b.mp3")])
    assert g.call_args.kwargs["text"] == "한국어 문장"
