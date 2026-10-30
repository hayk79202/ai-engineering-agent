import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path

from mcp import Client

from analyze_log import analyze_log
from inspect_repo import inspect
from server import allowed_path, mcp


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.previous = os.environ.get("ENGINEERING_ROOT")
        os.environ["ENGINEERING_ROOT"] = str(self.root)
        (self.root / "sample.py").write_text("# TODO: add docs\nprint('hi')\n", encoding="utf-8")
        (self.root / "app.log").write_text("INFO started\nWARN slow\nERROR failed\n", encoding="utf-8")

    def tearDown(self):
        if self.previous is None:
            os.environ.pop("ENGINEERING_ROOT", None)
        else:
            os.environ["ENGINEERING_ROOT"] = self.previous
        self.temp.cleanup()

    def test_repository_report(self):
        result = inspect(self.root)
        self.assertEqual(result["extensions"][".py"], 1)
        self.assertEqual(result["markers"][0]["line"], 1)

    def test_log_summary(self):
        result = analyze_log(self.root / "app.log")
        self.assertEqual(result["counts"], {"error": 1, "warning": 1})
        self.assertEqual(result["lines"], 3)

    def test_mcp_workspace_boundary(self):
        self.assertIsNotNone(mcp)
        self.assertEqual(allowed_path("sample.py"), self.root / "sample.py")
        with self.assertRaises(ValueError):
            allowed_path(str(self.root.parent))

    def test_mcp_tool_call(self):
        async def call_tool():
            async with Client(mcp) as client:
                return await client.call_tool("analyze_log_file", {"path": "app.log"})

        result = asyncio.run(call_tool())
        self.assertFalse(result.is_error)
        self.assertEqual(json.loads(result.content[0].text)["counts"]["error"], 1)


if __name__ == "__main__":
    unittest.main()
