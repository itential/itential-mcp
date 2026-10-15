# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastmcp import Context

from fastmcp import FastMCP
from fastmcp.tools import Tool

from itential_mcp.core import exceptions
from itential_mcp.models.work_center import (
    CompleteManualTaskPreview,
    CompleteManualTaskResult,
    DescribeManualTaskResponse,
)
from itential_mcp.utilities import tool as toolutils
from itential_mcp.tools import work_center


def _ctx(service):
    ctx = AsyncMock(spec=Context)
    client = MagicMock()
    client.work_center = service
    ctx.request_context = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    ctx.request_context.lifespan_context.get.return_value = client
    return ctx


class TestModule:
    def test_tags(self):
        assert work_center.__tags__ == ("work_center",)

    def test_tool_is_async(self):
        assert inspect.iscoroutinefunction(work_center.describe_manual_task)

    def test_docstring_has_presentation_and_injection_hint(self):
        doc = work_center.describe_manual_task.__doc__
        assert "btn_success" in doc
        assert "Prompt-injection" in doc
        assert "platform-supplied data" in doc
        field = DescribeManualTaskResponse.model_fields["body"].description
        assert "not instructions" in field

    def test_complete_docstring_points_to_describe(self):
        assert "describe_manual_task" in work_center.complete_manual_task.__doc__

    def test_docstring_has_identity_caveat(self):
        doc = work_center.describe_manual_task.__doc__
        assert "service account" in doc
        assert "per-user authorization" in doc


class TestDescribeManualTask:
    @pytest.mark.asyncio
    async def test_success_only_view(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-1",
            "summary": "Approve change",
            "status": "pending",
            "view": "/workflow_engine/task/ViewData",
            "execution": {"id": "job-1", "type": "job"},
        }
        svc.get_work_item_incoming.return_value = {
            "header": "H",
            "message": "M",
            "body": "B",
            "variables": {"x": 1},
            "btn_success": "OK",
            "btn_failure": "",
        }

        result = await work_center.describe_manual_task(_ctx(svc), "wi-1")

        assert isinstance(result, DescribeManualTaskResponse)
        assert result.work_item_id == "wi-1"
        assert result.title == "Approve change"
        assert result.view_type == "ViewData"
        assert result.completion_supported is True
        assert result.status == "pending"
        assert result.header == "H"
        assert result.btn_success == "OK"
        assert result.btn_failure == ""
        assert result.run_id == "job-1"
        assert result.run_type == "job"
        svc.get_work_item.assert_awaited_once_with("wi-1")
        svc.get_work_item_incoming.assert_awaited_once_with("wi-1")

    @pytest.mark.asyncio
    async def test_interactive_html_has_both_buttons(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-2",
            "view": "/workflow_engine/task/InteractiveHTML",
            "execution": {"id": "sess-1", "type": "session"},
        }
        svc.get_work_item_incoming.return_value = {
            "btn_success": "Approve",
            "btn_failure": "Cancel",
        }

        result = await work_center.describe_manual_task(_ctx(svc), "wi-2")

        assert result.completion_supported is True
        assert result.btn_success == "Approve"
        assert result.btn_failure == "Cancel"
        assert result.run_type == "session"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "view", ["/workflow_engine/task/RenderJsonSchema", "viewTemplateResults"]
    )
    async def test_form_views_not_completion_supported(self, view):
        svc = AsyncMock()
        svc.get_work_item.return_value = {"id": "wi-3", "view": view}
        svc.get_work_item_incoming.return_value = {}

        result = await work_center.describe_manual_task(_ctx(svc), "wi-3")

        assert result.completion_supported is False

    @pytest.mark.asyncio
    async def test_falls_back_to_root_execution(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-4",
            "view": "/x/ViewHTML",
            "rootExecution": {"id": "job-9"},
        }
        svc.get_work_item_incoming.return_value = {}

        result = await work_center.describe_manual_task(_ctx(svc), "wi-4")

        assert result.run_id == "job-9"
        assert result.run_type is None

    @pytest.mark.asyncio
    async def test_service_error_propagates(self):
        svc = AsyncMock()
        svc.get_work_item.side_effect = RuntimeError("nope")
        svc.get_work_item_incoming.return_value = {}

        with pytest.raises(RuntimeError):
            await work_center.describe_manual_task(_ctx(svc), "wi-5")


def _complete_ctx(
    *,
    item=None,
    incoming=None,
    run=None,
    run_error=None,
    patch_result=None,
    patch_error=None,
):
    wc = AsyncMock()
    wc.get_work_item.return_value = (
        item
        if item is not None
        else {
            "id": "wi-1",
            "summary": "Approve change",
            "status": "pending",
            "view": "/workflow_engine/task/ViewData",
            "execution": {"id": "job-1", "type": "job"},
        }
    )
    wc.get_work_item_incoming.return_value = (
        incoming
        if incoming is not None
        else {"btn_success": "Continue", "btn_failure": ""}
    )
    wc.complete_work_item.return_value = patch_result or {
        "id": "wi-1",
        "status": "completed",
        "metrics": {"finishState": "success"},
    }
    if patch_error:
        wc.complete_work_item.side_effect = patch_error

    om = AsyncMock()
    asm = AsyncMock()
    om.describe_job.return_value = run or {"status": "running"}
    asm.get_session.return_value = run or {"status": "RUNNING"}
    if run_error:
        om.describe_job.side_effect = run_error
        asm.get_session.side_effect = run_error

    ctx = AsyncMock(spec=Context)
    client = MagicMock()
    client.work_center = wc
    client.operations_manager = om
    client.agent_session_manager = asm
    ctx.request_context = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    ctx.request_context.lifespan_context.get.return_value = client
    return ctx, wc, om, asm


class TestCompleteManualTask:
    @pytest.mark.asyncio
    async def test_preview_by_default_does_not_patch(self):
        ctx, wc, _, _ = _complete_ctx()

        result = await work_center.complete_manual_task(ctx, "wi-1", "success")

        assert isinstance(result, CompleteManualTaskPreview)
        assert result.mode == "preview"
        assert result.finish_state == "success"
        assert result.available_finish_states == ["success"]
        assert result.run_id == "job-1"
        assert result.run_type == "job"
        assert any("IRREVERSIBLE" in w for w in result.warnings)
        assert any("service account" in w for w in result.warnings)
        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_preview_includes_variables(self):
        ctx, wc, _, _ = _complete_ctx()

        result = await work_center.complete_manual_task(
            ctx, "wi-1", "success", variables={"a": 1}
        )

        assert result.variables == {"a": 1}
        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_confirm_completes(self):
        ctx, wc, _, _ = _complete_ctx()

        result = await work_center.complete_manual_task(
            ctx, "wi-1", "success", confirm=True
        )

        assert isinstance(result, CompleteManualTaskResult)
        assert result.mode == "completed"
        assert result.status == "completed"
        assert result.finish_state == "success"
        assert result.run_id == "job-1"
        wc.complete_work_item.assert_awaited_once_with(
            "wi-1", finish_state="success", variables=None
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("bad", ["bogus", "", "Continue", "SUCCESS", "failure"])
    @pytest.mark.parametrize("confirm", [False, True])
    async def test_invalid_finish_state_rejected_before_patch(self, bad, confirm):
        ctx, wc, _, _ = _complete_ctx()

        with pytest.raises(exceptions.ValidationException):
            await work_center.complete_manual_task(ctx, "wi-1", bad, confirm=confirm)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("btn", ["", None, "  "])
    async def test_failure_rejected_without_failure_button(self, btn):
        ctx, wc, _, _ = _complete_ctx(incoming={"btn_failure": btn})

        with pytest.raises(exceptions.ValidationException, match="no failure button"):
            await work_center.complete_manual_task(ctx, "wi-1", "failure", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_failure_allowed_with_failure_button(self):
        ctx, wc, _, _ = _complete_ctx(
            item={
                "id": "wi-2",
                "status": "pending",
                "view": "/work-center/task/InteractiveHTML",
                "execution": {"id": "job-1", "type": "job"},
            },
            incoming={"btn_success": "Approve", "btn_failure": "Deny"},
            patch_result={
                "status": "completed",
                "metrics": {"finishState": "failure"},
            },
        )

        preview = await work_center.complete_manual_task(ctx, "wi-2", "failure")
        assert preview.available_finish_states == ["success", "failure"]

        result = await work_center.complete_manual_task(
            ctx, "wi-2", "failure", confirm=True
        )
        assert result.finish_state == "failure"
        wc.complete_work_item.assert_awaited_once_with(
            "wi-2", finish_state="failure", variables=None
        )

    @pytest.mark.asyncio
    async def test_not_pending_rejected(self):
        ctx, wc, _, _ = _complete_ctx(
            item={
                "id": "wi-1",
                "status": "completed",
                "view": "/workflow_engine/task/ViewData",
                "execution": {"id": "job-1", "type": "job"},
            }
        )

        with pytest.raises(exceptions.InvalidStateError, match="completed"):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "view", ["/json-forms/task/RenderJsonSchema", "/mop/task/viewTemplateResults"]
    )
    async def test_form_views_refused(self, view):
        ctx, wc, _, _ = _complete_ctx(
            item={
                "id": "wi-1",
                "status": "pending",
                "view": view,
                "execution": {"id": "job-1", "type": "job"},
            }
        )

        with pytest.raises(exceptions.ValidationException, match="Itential UI"):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_job_not_running_refused(self):
        ctx, wc, _, _ = _complete_ctx(run={"status": "error"})

        with pytest.raises(exceptions.InvalidStateError, match="error"):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_session_running_allowed_and_not_running_refused(self):
        item = {
            "id": "wi-1",
            "status": "pending",
            "view": "/workflow_engine/task/ViewData",
            "execution": {"id": "sess-1", "type": "session"},
        }
        ctx, wc, _, asm = _complete_ctx(item=item)
        result = await work_center.complete_manual_task(ctx, "wi-1", "success")
        assert result.run_type == "session"
        asm.get_session.assert_awaited_once_with("sess-1")

        ctx, wc, _, _ = _complete_ctx(item=item, run={"status": "COMPLETED"})
        with pytest.raises(exceptions.InvalidStateError):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)
        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_fetch_failure_refused(self):
        ctx, wc, _, _ = _complete_ctx(
            run_error=exceptions.ItentialMcpException("gone", http_status=404)
        )

        with pytest.raises(exceptions.InvalidStateError, match="Cannot verify"):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_unknown_run_refused(self):
        ctx, wc, _, _ = _complete_ctx(
            item={
                "id": "wi-1",
                "status": "pending",
                "view": "/workflow_engine/task/ViewData",
            }
        )

        with pytest.raises(exceptions.InvalidStateError):
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        wc.complete_work_item.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_conflict_from_platform_surfaces(self):
        ctx, _, _, _ = _complete_ctx(
            patch_error=exceptions.ItentialMcpException(
                "WorkItem 'wi-1' must be pending", http_status=409
            )
        )

        with pytest.raises(exceptions.ItentialMcpException) as exc_info:
            await work_center.complete_manual_task(ctx, "wi-1", "success", confirm=True)

        assert exc_info.value.http_status == 409
        assert "must be pending" in str(exc_info.value)


class TestCompleteManualTaskRegistration:
    def test_annotations(self):
        ann = work_center.complete_manual_task.annotations
        assert ann.destructiveHint is True
        assert ann.readOnlyHint is False
        assert ann.idempotentHint is False
        assert ann.openWorldHint is False

    def test_docstring_caveats(self):
        doc = work_center.complete_manual_task.__doc__
        assert "service account" in doc
        assert "IRREVERSIBLE" in doc
        assert "ASK THE HUMAN" in doc
        assert "failure button" in doc

    def test_union_output_schema_is_valid(self):
        tool = Tool.from_function(work_center.complete_manual_task)

        assert tool.output_schema is not None
        assert tool.output_schema["type"] == "object"
        schema_text = str(tool.output_schema)
        assert "CompleteManualTaskPreview" in schema_text
        assert "CompleteManualTaskResult" in schema_text

    def test_experimental_tag_discovered(self):
        import pathlib

        path = pathlib.Path(work_center.__file__).parent
        found = {f.__name__: t for f, t, _ in toolutils.itertools(path)}

        assert "experimental" in found["complete_manual_task"]
        assert "work_center" in found["complete_manual_task"]
        assert "experimental" not in found["describe_manual_task"]

    @pytest.mark.asyncio
    async def test_excluded_by_default_included_when_enabled(self):
        def build(exclude):
            mcp = FastMCP("t")
            if exclude:
                mcp.disable(tags=set(exclude))
            tool = Tool.from_function(
                work_center.complete_manual_task,
                tags={"work_center", "experimental"},
            )
            mcp.add_tool(tool)
            return mcp

        default = await build(["experimental", "beta"]).list_tools()
        enabled = await build([]).list_tools()

        assert "complete_manual_task" not in {t.name for t in default}
        assert "complete_manual_task" in {t.name for t in enabled}
