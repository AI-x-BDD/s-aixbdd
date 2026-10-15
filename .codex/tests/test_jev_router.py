"""不呼叫外部 API；使用隔離的狀態檔驗證路由與失敗回退。"""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "hooks" / "jev_router.py"
spec = importlib.util.spec_from_file_location("jev_router", SCRIPT)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)
EVENT = {
    "hook_event_name": "UserPromptSubmit", "cwd": str(router.PROJECT_ROOT),
    "prompt": "列出 docs 中 Markdown 檔案的數量。",
}
ANSWER = {
    "type": "choice", "choice": "light", "confidence": 0.96,
    "probabilities": {"light": 0.98, "main": 0.01, "insufficient": 0.01},
}


def test_local_gates():
    with tempfile.TemporaryDirectory() as temp:
        state = Path(temp) / "enabled"
        with patch.object(router, "STATE_FILE", state), patch.dict(
            os.environ, {"TYPESAFE_API_KEY": "test-only", "JEV_ROUTER_DISABLE": "0"}
        ), patch.object(router, "fetch_answer", return_value=ANSWER) as fetch:
            assert router.route(EVENT) is None
            fetch.assert_not_called()
            state.touch()
            result = router.route(EVENT)
            assert "jev_light" in result["hookSpecificOutput"]["additionalContext"]
            assert EVENT["prompt"] not in json.dumps(result, ensure_ascii=False)
            for change in (
                {"prompt": "apikey_fake_do_not_send"},
                {"prompt": "password=example"},
                {"prompt": "Bearer example"},
                {"prompt": "文" * router.MAX_PROMPT_BYTES},
                {"prompt": ""}, {"prompt": None},
                {"cwd": "/outside-project"}, {"cwd": ""},
                {"agent_id": "child"}, {"agent_type": "jev_light"},
                {"hook_event_name": "Stop"},
            ):
                fetch.reset_mock()
                assert router.route({**EVENT, **change}) is None, change
                fetch.assert_not_called()
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}), patch.object(
                router, "keychain_api_key", return_value=""
            ):
                fetch.reset_mock()
                assert router.route(EVENT) is None
                fetch.assert_not_called()
            with patch.dict(os.environ, {"JEV_ROUTER_DISABLE": "1"}):
                fetch.reset_mock()
                assert router.route(EVENT) is None
                fetch.assert_not_called()


def test_answer_validation():
    assert router.valid_light_answer(ANSWER)
    for answer in (
        None, [], {}, {**ANSWER, "choice": "main"},
        {**ANSWER, "choice": "insufficient"}, {**ANSWER, "choice": "invented"},
        {**ANSWER, "confidence": 0.4}, {**ANSWER, "confidence": float("nan")},
        {**ANSWER, "confidence": True},
        {**ANSWER, "probabilities": {"light": 1}},
        {**ANSWER, "probabilities": {"light": 0.8, "main": 0.1, "insufficient": 0.1}},
        {**ANSWER, "probabilities": {"light": 1, "main": 1, "insufficient": 1}},
    ):
        assert not router.valid_light_answer(answer), answer


def test_http_contract():
    # 模擬 HTTP response；核對實際送出的 body 與標頭，不含檔案或預期答案。
    response = io.BytesIO(json.dumps({"answers": {"tier": ANSWER}}).encode())
    response.status = 200
    opener = Mock()
    opener.open.return_value = response
    with patch.object(router.urllib.request, "OpenerDirector", return_value=opener):
        assert router.fetch_answer(EVENT["prompt"], "test-only") == ANSWER
    request = opener.open.call_args.args[0]
    body = json.loads(request.data)
    assert body["state"] == {"prompt": EVENT["prompt"]}
    assert body["questions"]["tier"]["criteria"] == router.CRITERIA
    assert request.get_header("Authorization") == "Bearer test-only"
    assert opener.open.call_args.kwargs["timeout"] == router.REQUEST_TIMEOUT
    assert not any(isinstance(call.args[0], router.urllib.request.HTTPRedirectHandler)
                   for call in opener.add_handler.call_args_list)


def test_main_failure_and_control():
    with tempfile.TemporaryDirectory() as temp:
        state = Path(temp) / "enabled"
        with patch.object(router, "STATE_FILE", state), patch.dict(
            os.environ, {"TYPESAFE_API_KEY": "test-only", "JEV_ROUTER_DISABLE": "0"}
        ):
            with patch("sys.stdout", new_callable=io.StringIO):
                assert router.control("on") == 0
            assert state.exists()
            for failure in (TimeoutError(), ValueError(), OSError()):
                stdin = Mock(buffer=io.BytesIO(json.dumps(EVENT).encode()))
                with patch("sys.argv", [str(SCRIPT)]), patch("sys.stdin", stdin), patch(
                    "sys.stdout", new_callable=io.StringIO
                ) as output, patch("sys.stderr", new_callable=io.StringIO) as error, patch.object(
                    router, "fetch_answer", side_effect=failure
                ):
                    assert router.main() == 0
                    assert output.getvalue() == error.getvalue() == ""
            with patch("sys.stdout", new_callable=io.StringIO):
                assert router.control("off") == 0
            assert not state.exists()
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}), patch.object(
                router, "keychain_api_key", return_value=""
            ), patch(
                "sys.stderr", new_callable=io.StringIO
            ):
                assert router.control("on") == 1
                assert not state.exists()


def test_disabled_subprocess():
    env = {**os.environ, "JEV_ROUTER_DISABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], input="不是 JSON", text=True,
        capture_output=True, env=env, timeout=3,
    )
    assert result.returncode == 0
    assert result.stdout == result.stderr == ""


def test_keychain_fallback():
    with patch.dict(os.environ, {"TYPESAFE_API_KEY": "env-test"}), patch.object(
        router, "keychain_api_key", return_value="keychain-test"
    ) as keychain:
        assert router.load_api_key() == "env-test"
        keychain.assert_not_called()
    with patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}), patch.object(
        router, "keychain_api_key", return_value="keychain-test"
    ):
        assert router.load_api_key() == "keychain-test"
    with patch.object(router.sys, "platform", "darwin"), patch.object(
        router.subprocess, "run", side_effect=subprocess.TimeoutExpired("security", 1)
    ):
        assert router.keychain_api_key() == ""


if __name__ == "__main__":
    tests = [test_local_gates, test_answer_validation, test_http_contract,
             test_main_failure_and_control, test_disabled_subprocess,
             test_keychain_fallback]
    for test in tests:
        test()
        print("通過：" + test.__name__)
    print(f"共 {len(tests)} 組檢查通過；未呼叫外部 API。")
