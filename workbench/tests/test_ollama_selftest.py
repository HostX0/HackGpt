import json
import unittest
from unittest.mock import Mock

from workbench.ollama import Ollama
from workbench.ollama_runtime import OllamaError
from workbench.ollama_selftest import validate_local_inference


class SelfTestTests(unittest.TestCase):
    def client(self, replies, *, tool_calling=True):
        client = Mock()
        client.inspect_model.return_value = {
            "provider": "ollama",
            "model": "local:test",
            "state": "metadata_checked",
            "tool_calling": tool_calling,
            "inference_tested": False,
        }
        client.chat.side_effect = replies
        return client

    def test_structured_probe_marks_only_compatibility(self):
        client = self.client([{"content": json.dumps({"status": "ready", "scope": "synthetic_self_test"})}])
        result = validate_local_inference(client)
        self.assertEqual(result["state"], "inference_compatible")
        self.assertTrue(result["structured_output_tested"])
        self.assertFalse(result["tool_calling_tested"])
        self.assertFalse(result["assessment_data_sent"])
        self.assertIn("does not", result["note"].lower())
        client.inspect_model.assert_called_once_with(require_tools=False)

    def test_probe_prompt_contains_no_assessment_fields(self):
        client = self.client([{"content": '{"status":"ready","scope":"synthetic_self_test"}'}])
        validate_local_inference(client)
        sent = json.dumps(client.chat.call_args.args[0]).lower()
        for sensitive_field in ("target", "authorization", "finding", "evidence"):
            self.assertNotIn(sensitive_field, sent)

    def test_tool_probe_is_inert_and_strict(self):
        client = self.client([
            {"content": '{"status":"ready","scope":"synthetic_self_test"}'},
            {"content": "", "tool_calls": [{"function": {"name": "workbench_self_test", "arguments": {}}}]},
        ])
        result = validate_local_inference(client, require_tools=True)
        self.assertTrue(result["tool_calling_tested"])
        client.inspect_model.assert_called_once_with(require_tools=True)
        self.assertEqual(client.chat.call_count, 2)
        declared = client.chat.call_args_list[1].kwargs["tools"][0]["function"]
        self.assertEqual(declared["name"], "workbench_self_test")
        self.assertEqual(declared["parameters"]["additionalProperties"], False)

    def test_invalid_structured_output_fails_closed(self):
        for content in ("not-json", '{"status":"ready"}', '{"status":"safe","scope":"synthetic_self_test"}', '[]'):
            with self.subTest(content=content):
                client = self.client([{"content": content}])
                with self.assertRaises(OllamaError) as context:
                    validate_local_inference(client)
                self.assertEqual(context.exception.code, "self_test_failed")

    def test_missing_tool_call_fails_closed(self):
        client = self.client([
            {"content": '{"status":"ready","scope":"synthetic_self_test"}'},
            {"content": "I will not call a tool"},
        ])
        with self.assertRaises(OllamaError) as context:
            validate_local_inference(client, require_tools=True)
        self.assertEqual(context.exception.code, "self_test_failed")

    def test_wrong_tool_name_or_arguments_fails_closed(self):
        bad_calls = [
            [{"function": {"name": "other", "arguments": {}}}],
            [{"function": {"name": "workbench_self_test", "arguments": {"target": "x"}}}],
            [{"function": {"name": "workbench_self_test", "arguments": {}}}, {"function": {"name": "workbench_self_test", "arguments": {}}}],
        ]
        for calls in bad_calls:
            with self.subTest(calls=calls):
                client = self.client([
                    {"content": '{"status":"ready","scope":"synthetic_self_test"}'},
                    {"content": "", "tool_calls": calls},
                ])
                with self.assertRaises(OllamaError):
                    validate_local_inference(client, require_tools=True)

    def test_ollama_method_exposes_probe(self):
        client = Ollama("local:test")
        client.inspect_model = Mock(return_value={"provider": "ollama", "model": "local:test", "tool_calling": False})
        client.chat = Mock(return_value={"content": '{"status":"ready","scope":"synthetic_self_test"}'})
        result = client.self_test()
        self.assertEqual(result["state"], "inference_compatible")
        self.assertFalse(result["assessment_data_sent"])

    def test_require_tools_is_strict_boolean(self):
        client = self.client([])
        with self.assertRaises(ValueError):
            validate_local_inference(client, require_tools="true")
        client.inspect_model.assert_not_called()
        client.chat.assert_not_called()

    def test_metadata_failure_prevents_prompt(self):
        client = self.client([])
        client.inspect_model.side_effect = OllamaError("cloud_model_blocked", "blocked", "choose local")
        with self.assertRaises(OllamaError) as context:
            validate_local_inference(client)
        self.assertEqual(context.exception.code, "cloud_model_blocked")
        client.chat.assert_not_called()


if __name__ == "__main__":
    unittest.main()
