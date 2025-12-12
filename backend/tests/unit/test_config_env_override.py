import os
import importlib

def reload_util():
    if 'utils.util' in importlib.sys.modules:
        importlib.reload(importlib.import_module('utils.util'))
    else:
        import utils.util  # noqa


def test_env_override_basic_port():
    os.environ['SERVER_PORT'] = '4001'
    reload_util()
    from utils.util import Util
    cfg = Util.get_config()
    assert cfg['server']['port'] == 4001


def test_env_override_llm_openai_api_key_and_base_url():
    os.environ['LLM_OPENAI_API_KEY'] = 'TESTKEY'
    os.environ['APP_LLM_OPENAI_BASE_URL'] = 'https://example.com'
    reload_util()
    from utils.util import Util
    cfg = Util.get_config()
    assert cfg['LLM']['openai']['api_key'] == 'TESTKEY'
    assert cfg['LLM']['openai']['base_url'] == 'https://example.com'
