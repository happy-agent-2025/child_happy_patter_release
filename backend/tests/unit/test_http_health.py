import asyncio
import pytest
import aiohttp

@pytest.mark.asyncio
async def test_health_includes_version_and_components():
    from utils.util import Util
    from utils.protocol.http_server import create_http_server
    cfg = Util.get_config()
    server = await create_http_server(cfg, host="127.0.0.1", port=8081)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8081/health') as resp:
                assert resp.status == 200
                data = await resp.json()
                assert 'version' in data
                assert 'components' in data
                assert 'LLM' in data['components']
                assert 'TTS' in data['components']
                assert 'ASR' in data['components']
                assert 'VAD' in data['components']
                assert 'env' in data['components']
                assert 'opuslib_next_available' in data['components']['env']
                assert 'ffmpeg_available' in data['components']['env']
    finally:
        await server.stop()
