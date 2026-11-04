"""Starts the MCP server over stdio, lists tools, and calls convert_to_markdown."""
import asyncio, os, sys, unittest
HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None


async def _run():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(ROOT, "doc2md_lite_mcp.py")], cwd=ROOT)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            listed = (await s.list_tools()).tools
            tools = [t.name for t in listed]
            ann = listed[0].annotations
            res = await s.call_tool("convert_to_markdown", {"path": os.path.abspath(os.path.join(HERE, "fixtures", "store-report.pdf"))})
            bad = await s.call_tool("convert_to_markdown", {"path": "/nope/missing.pdf"})
            return tools, res, bad, ann


@unittest.skipIf(ClientSession is None, "mcp not installed")
class MCP(unittest.TestCase):
    def test_lists_and_calls_tool(self):
        tools, res, bad, ann = asyncio.run(_run())
        self.assertIsNotNone(ann)
        self.assertIs(ann.readOnlyHint, False)
        self.assertIs(ann.destructiveHint, True)
        self.assertIs(ann.idempotentHint, True)
        self.assertIs(ann.openWorldHint, False)
        self.assertEqual(tools, ["convert_to_markdown"])
        self.assertFalse(res.isError)
        text = " ".join(c.text for c in res.content if getattr(c, "type", "") == "text")
        self.assertIn("# Spring Store Report", text)
        self.assertIn("| North | 12 | $48,200 |", text)
        self.assertTrue(bad.isError)


if __name__ == "__main__":
    unittest.main()
