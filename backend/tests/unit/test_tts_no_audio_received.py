def test_edge_tts_no_audio_received_handled(monkeypatch):
    import edge_tts
    from ai_core.tts.edge import TTSModule

    class DummyCommunicate:
        def __init__(self, text, voice):
            self.text = text
            self.voice = voice
        async def save(self, path):
            raise edge_tts.exceptions.NoAudioReceived("No audio")

    monkeypatch.setattr(edge_tts, 'Communicate', DummyCommunicate)

    cfg = {"output_dir": "ai_core/tts/temp", "voice": "zh-CN-XiaoxiaoNeural"}
    mod = TTSModule(cfg)
    opus, dur, txt = mod.text_to_opus_data("测试")
    assert isinstance(opus, list)
    assert dur == 0
    assert txt != ""

def test_is_only_punctuation_filtering():
    from utils.protocol.message_process import MessageProcess
    class Dummy:
        ai = type('A', (), {'vad': None})()
    mp = MessageProcess({}, Dummy())
    assert mp.is_only_punctuation("...") is True
    assert mp.is_only_punctuation("你好！") is False
