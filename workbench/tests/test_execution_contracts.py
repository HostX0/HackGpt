import unittest

from workbench.execution_contracts import EXECUTION_SCHEMA, normalize_execution_declaration


def declaration(**updates):
    value = {
        "schema": EXECUTION_SCHEMA,
        "adapter": {"id": "native-project-metadata", "version": "1"},
        "launcher": "native_python",
        "effect_level": "read_only",
        "filesystem": "read_only_metadata",
        "network": "none",
        "subprocess": False,
        "writes": False,
        "follows_symlinks": False,
        "limits": {"max_objects": 1000, "max_requests": 0, "timeout_seconds": 30},
        "coverage_unit": "eligible_project_files",
    }
    value.update(updates)
    return value


class ExecutionDeclarationTests(unittest.TestCase):
    def test_roundtrip_keeps_closed_authority(self):
        result = normalize_execution_declaration(declaration())
        self.assertEqual(result["schema"], EXECUTION_SCHEMA)
        self.assertEqual(result["network"], "none")
        self.assertFalse(result["subprocess"])
        self.assertFalse(result["writes"])
        self.assertEqual(result["limits"]["max_requests"], 0)

    def test_unknown_command_field_is_rejected(self):
        value = declaration()
        value["command"] = "anything"
        with self.assertRaises(ValueError):
            normalize_execution_declaration(value)

    def test_native_launcher_cannot_claim_subprocess(self):
        with self.assertRaises(ValueError):
            normalize_execution_declaration(declaration(subprocess=True))

    def test_read_only_cannot_write(self):
        with self.assertRaises(ValueError):
            normalize_execution_declaration(declaration(writes=True))

    def test_network_none_requires_zero_requests(self):
        value = declaration()
        value["limits"] = dict(value["limits"], max_requests=1)
        with self.assertRaises(ValueError):
            normalize_execution_declaration(value)

    def test_networked_adapter_requires_positive_request_budget(self):
        with self.assertRaises(ValueError):
            normalize_execution_declaration(declaration(network="scoped_target"))

    def test_external_launcher_must_declare_subprocess(self):
        with self.assertRaises(ValueError):
            normalize_execution_declaration(declaration(launcher="fixed_binary"))

    def test_limits_are_bounded_and_typed(self):
        for field, bad in (("max_objects", 0), ("max_objects", 100001), ("max_requests", -1),
                           ("max_requests", 10001), ("timeout_seconds", 0), ("timeout_seconds", 3601)):
            value = declaration()
            value["limits"] = dict(value["limits"], **{field: bad})
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                normalize_execution_declaration(value)


if __name__ == "__main__":
    unittest.main()
