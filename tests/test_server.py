# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

from itential_mcp import server


class TestRegisterTools:
    def setup_method(self):
        self.tools_dir = os.path.join(os.path.dirname(__file__), "tools")
        self.original_path = server.__file__
        self.mock_tool_code = "def hello(): return 'world'"
        self.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.temp_dir, "tools"))

        # Write a valid tool
        with open(os.path.join(self.temp_dir, "tools", "testtool.py"), "w") as f:
            f.write(self.mock_tool_code)

        # Patch the path
        self._realpath_patch = patch("itential_mcp.server.os.path.realpath", return_value=os.path.join(self.temp_dir, "__init__.py"))
        self._realpath_patch.start()

        # Patch os.listdir
        self._listdir_patch = patch("itential_mcp.server.os.listdir", return_value=["testtool.py"])
        self._listdir_patch.start()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
        self._realpath_patch.stop()
        self._listdir_patch.stop()

    def test_register_tools_attaches_functions(self):
        mcp = MagicMock()
        server.register_tools(mcp)
        mcp.add_tool.assert_called_once()


class TestRun:
    @pytest.mark.asyncio
    async def test_run_invalid_transport_raises(self):
        with pytest.raises(ValueError, match="invalid setting for transport"):
            await server.run(transport="invalid")

    @pytest.mark.asyncio
    async def test_run_invalid_log_level_raises(self):
        with pytest.raises(ValueError, match="invalid setting for log_level"):
            await server.run(log_level="VERBOSE")

    @pytest.mark.asyncio
    async def test_run_stdio_success(self):
        with patch("itential_mcp.server.FastMCP") as mock_mcp:
            instance = mock_mcp.return_value
            instance.run_async = AsyncMock()

            result = await server.run()
            instance.run_async.assert_awaited()
            assert result is None  # run() has no return, only sys.exit on exception


class TestLifespan:
    @pytest.mark.asyncio
    async def test_lifespan_yields_context(self):
        fake_client = MagicMock()
        with patch("itential_mcp.server.config.get", return_value={"want_async": True}), \
             patch("itential_mcp.server.ipsdk.platform_factory", return_value=fake_client):

            async with server.lifespan(MagicMock()) as ctx:
                assert "client" in ctx
                assert ctx["client"] is fake_client

