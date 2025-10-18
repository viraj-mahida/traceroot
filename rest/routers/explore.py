import asyncio
import logging
from collections import deque
from datetime import datetime, timezone
import os
from typing import Any

from aiocache import SimpleMemoryCache
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter

from rest.agent import Chat
from rest.service.provider import ObservabilityProvider
from rest.tools.github import GitHubClient

try:
    from rest.dao.ee.mongodb_dao import TraceRootMongoDBClient
except ImportError:
    from rest.dao.mongodb_dao import TraceRootMongoDBClient

from rest.agent.context.tree import SpanNode, build_heterogeneous_tree
from rest.agent.summarizer.chatbot_output import summarize_chatbot_output
from rest.agent.summarizer.github import SeparateIssueAndPrInput, separate_issue_and_pr
from rest.agent.summarizer.title import summarize_title
from rest.config import (
    ChatbotResponse,
    ChatHistoryResponse,
    ChatMetadata,
    ChatMetadataHistory,
    ChatRequest,
    CodeRequest,
    CodeResponse,
    GetChatHistoryRequest,
    GetChatMetadataHistoryRequest,
    GetChatMetadataRequest,
    GetLogByTraceIdRequest,
    GetLogByTraceIdResponse,
    ListTraceRawRequest,
    ListTraceRequest,
    ListTraceResponse,
    Trace,
    TraceLogs,
)
from rest.config.rate_limit import get_rate_limit_config
from rest.dao.sqlite_dao import TraceRootSQLiteClient
from rest.typing import (
    ActionStatus,
    ActionType,
    ChatMode,
    ChatModel,
    MessageType,
    Operation,
    Provider,
    Reference,
    ResourceType,
)
from rest.utils.trace import collect_spans_latency_recursively

try:
    from rest.utils.ee.auth import get_user_credentials, hash_user_sub
except ImportError:
    from rest.utils.auth import get_user_credentials, hash_user_sub

from rest.agent.agent import Agent
from rest.agent.summarizer.github import is_github_related, set_github_related
from rest.utils.github import parse_github_url


class ExploreRouter:
    r"""Explore router."""

    def __init__(
        self,
        local_mode: bool,
        limiter: Limiter,
    ):
        self.router = APIRouter()
        self.local_mode = local_mode
        self.chat = Chat()
        self.agent = Agent()
        self.logger = logging.getLogger(__name__)

        # Choose client based on REST_LOCAL_MODE environment variable
        if self.local_mode:
            self.db_client = TraceRootSQLiteClient()
        else:
            self.db_client = TraceRootMongoDBClient()

        # Create default observability provider
        if self.local_mode:
            self.default_observe_provider = ObservabilityProvider.create_jaeger_provider()
        else:
            self.default_observe_provider = ObservabilityProvider.create_aws_provider()

        self.github = GitHubClient()
        self.limiter = limiter
        self.rate_limit_config = get_rate_limit_config()
        # Cache for 10 minutes
        self.cache = SimpleMemoryCache(ttl=60 * 10)
        self._setup_routes()

    async def get_observe_provider(self, request: Request) -> ObservabilityProvider:
        """Get observability provider based on request.

        For local mode, always use the default Jaeger provider.
        For non-local mode, fetch provider configuration from request params and MongoDB.

        Args:
            request: FastAPI request object

        Returns:
            ObservabilityProvider instance
        """
        if self.local_mode:
            return self.default_observe_provider

        # Extract provider parameters from request
        query_params = request.query_params
        trace_provider = query_params.get("trace_provider", "aws")
        log_provider = query_params.get("log_provider", "aws")
        trace_region = query_params.get("trace_region")
        log_region = query_params.get("log_region")

        # Get user email to fetch MongoDB config
        user_email, _, _ = get_user_credentials(request)

        # Prepare configurations
        trace_config: dict[str, Any] = {}
        log_config: dict[str, Any] = {}

        # For Tencent, fetch credentials from MongoDB
        if trace_provider == "tencent":
            trace_provider_config = await self.db_client.get_trace_provider_config(
                user_email
            )
            if trace_provider_config and trace_provider_config.get("tencentTraceConfig"):
                tencent_config = trace_provider_config["tencentTraceConfig"]
                trace_config = {
                    "region": trace_region or tencent_config.get("region",
                                                                 "ap-hongkong"),
                    "secret_id": tencent_config.get("secretId"),
                    "secret_key": tencent_config.get("secretKey"),
                    "apm_instance_id": tencent_config.get("apmInstanceId"),
                }
            else:
                # Fallback to region only if no MongoDB config
                trace_config = {"region": trace_region or "ap-hongkong"}
        elif trace_provider == "aws":
            trace_config = {"region": trace_region}
        elif trace_provider == "jaeger":
            # Fetch jaeger config from MongoDB if available
            trace_provider_config = await self.db_client.get_trace_provider_config(
                user_email
            )
            if trace_provider_config and trace_provider_config.get("jaegerTraceConfig"):
                jaeger_config = trace_provider_config["jaegerTraceConfig"]
                trace_config = {"url": jaeger_config.get("endpoint")}
            else:
                trace_config = {}

        if log_provider == "tencent":
            log_provider_config = await self.db_client.get_log_provider_config(user_email)
            if log_provider_config and log_provider_config.get("tencentLogConfig"):
                tencent_config = log_provider_config["tencentLogConfig"]
                log_config = {
                    "region": log_region or tencent_config.get("region",
                                                               "ap-hongkong"),
                    "secret_id": tencent_config.get("secretId"),
                    "secret_key": tencent_config.get("secretKey"),
                    "cls_topic_id": tencent_config.get("clsTopicId"),
                }
            else:
                # Fallback to region only if no MongoDB config
                log_config = {"region": log_region or "ap-hongkong"}
        elif log_provider == "aws":
            log_config = {"region": log_region}
        elif log_provider == "jaeger":
            # Fetch jaeger config from MongoDB if available
            log_provider_config = await self.db_client.get_log_provider_config(user_email)
            if log_provider_config and log_provider_config.get("jaegerLogConfig"):
                jaeger_config = log_provider_config["jaegerLogConfig"]
                log_config = {"url": jaeger_config.get("endpoint")}
            else:
                log_config = {}

        # Create and return the provider
        return ObservabilityProvider.create(
            trace_provider=trace_provider,
            log_provider=log_provider,
            trace_config=trace_config,
            log_config=log_config,
        )

    def _setup_routes(self):
        r"""Set up API routes"""
        # Apply rate limiting to routes using configuration
        self.router.get("/list-traces")(
            self.limiter.limit(self.rate_limit_config.list_traces_limit
                               )(self.list_traces)
        )
        self.router.get("/get-logs-by-trace-id")(
            self.limiter.limit(self.rate_limit_config.get_logs_limit
                               )(self.get_logs_by_trace_id)
        )
        self.router.post("/post-chat")(
            self.limiter.limit(self.rate_limit_config.post_chat_limit)(self.post_chat)
        )
        self.router.get("/get-chat-metadata-history")(
            self.limiter.limit(self.rate_limit_config.get_chat_metadata_history_limit
                               )(self.get_chat_metadata_history)
        )
        self.router.get("/get-chat-metadata")(
            self.limiter.limit(self.rate_limit_config.get_chat_metadata_limit
                               )(self.get_chat_metadata)
        )
        self.router.get("/get-chat-history")(
            self.limiter.limit(self.rate_limit_config.get_chat_history_limit
                               )(self.get_chat_history)
        )
        self.router.get("/chat/{chat_id}/reasoning")(
            self.limiter.limit("1200/minute")(self.get_chat_reasoning)
        )
        self.router.get("/get-line-context-content")(
            self.limiter.limit(self.rate_limit_config.get_line_context_content_limit
                               )(self.get_line_context_content)
        )

    async def handle_github_file(
        self,
        owner: str,
        repo: str,
        file_path: str,
        ref: str,
        line_num: int,
        github_token: str | None,
        line_context_len: int = 100,
    ) -> dict[str,
              Any]:
        r"""Handle GitHub file content and cache it.

        Args:
            owner (str): Owner of the repository.
            repo (str): Name of the repository.
            file_path (str): Path of the file.
            ref (str): Reference of the file.
            line_num (int): Line number of the file.
            github_token (str | None): GitHub token.

        Returns:
            dict[str, Any]: Dictionary of CodeResponse.model_dump().
        """
        context_key = (owner, repo, file_path, ref, line_num)
        # Try to get cached context lines
        context_lines = await self.cache.get(context_key)

        # Cache hit
        if context_lines is not None:
            lines_above, line, lines_below = context_lines
            response = CodeResponse(
                line=line,
                lines_above=lines_above,
                lines_below=lines_below,
            )
            return response.model_dump()

        # Cache miss then need to get file content at first
        file_key = (owner, repo, file_path, ref)
        file_content = await self.cache.get(file_key)

        # File content is cached, get context lines from file content
        if file_content is not None:
            context_lines = await self.github.get_line_context_content(
                file_content,
                line_num
            )
            # Cache the context lines
            await self.cache.set(context_key, context_lines)
            if context_lines is not None:
                lines_above, line, lines_below = context_lines
                response = CodeResponse(
                    line=line,
                    lines_above=lines_above,
                    lines_below=lines_below,
                )
                return response.model_dump()

        # File content is not cached then need to get file content
        file_content, error_message = await self.github.get_file_content(
            owner, repo, file_path, ref, github_token)

        # If file content is not found or cannot be retrieved,
        # return the error message
        if file_content is None:
            response = CodeResponse(
                line=None,
                lines_above=None,
                lines_below=None,
                error_message=error_message,
            )
            return response.model_dump()

        # Cache the file content at first
        await self.cache.set(file_key, file_content)
        context_lines = await self.github.get_line_context_content(
            file_content,
            line_num,
            line_context_len=line_context_len,
        )
        if context_lines is None:
            error_message = (
                f"Failed to get line context content "
                f"for line number {line_num} "
                f"in {owner}/{repo}@{ref}"
            )
            response = CodeResponse(
                line=None,
                lines_above=None,
                lines_below=None,
                error_message=error_message,
            )
            return response.model_dump()

        # Cache the context lines
        await self.cache.set(context_key, context_lines)
        lines_above, line, lines_below = context_lines
        response = CodeResponse(
            line=line,
            lines_above=lines_above,
            lines_below=lines_below,
        )
        return response.model_dump()

    async def get_line_context_content(
        self,
        request: Request,
        req_data: CodeRequest = Depends(),
    ) -> dict[str,
              Any]:
        """Get file line context content from GitHub URL.
        This is called to show the code in the UI.

        Args:
            req_data (CodeRequest): Request containing GitHub URL

        Returns:
            dict[str, Any]: Dictionary of CodeResponse.model_dump().

        Raises:
            HTTPException: If URL is invalid or file cannot be
                retrieved
        """
        # Get user credentials (fake in local mode, real in remote mode)
        user_email, _, _ = get_user_credentials(request)
        github_token = await self.get_github_token(user_email)

        owner, repo, ref, file_path, line_num = parse_github_url(req_data.url)
        return await self.handle_github_file(
            owner,
            repo,
            file_path,
            ref,
            line_num,
            github_token,
            line_context_len=4,
        )

    async def list_traces(
        self,
        request: Request,
        raw_req: ListTraceRawRequest = Depends(),
    ) -> dict[str,
              Any]:
        r"""Get trace data with optional timestamp filtering or trace ID.

        Args:
            request (Request): FastAPI request object
            raw_req (ListTraceRawRequest): Raw request data from
                query parameters

        Returns:
            dict[str, Any]: Dictionary containing list of trace data.
        """
        _, _, user_sub = get_user_credentials(request)
        log_group_name = hash_user_sub(user_sub)

        # Convert raw request to proper ListTraceRequest
        # with correct list parsing
        req_data: ListTraceRequest = raw_req.to_list_trace_request(request)
        start_time = req_data.start_time
        end_time = req_data.end_time
        categories = req_data.categories.copy()  # Make a copy to modify
        values = req_data.values.copy()
        operations = req_data.operations.copy()
        trace_id = req_data.trace_id

        # If trace_id is provided, fetch that specific trace directly
        if trace_id:
            try:
                observe_provider = await self.get_observe_provider(request)

                # Use the new get_trace_by_id method which handles everything
                trace = await observe_provider.trace_client.get_trace_by_id(
                    trace_id=trace_id,
                    categories=categories,
                    values=values,
                    operations=[Operation(op)
                                for op in operations] if operations else None,
                )

                # If trace not found, return empty list
                if trace is None:
                    resp = ListTraceResponse(traces=[])
                    return resp.model_dump()

                resp = ListTraceResponse(traces=[trace])
                return resp.model_dump()

            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                self.logger.error(f"Error fetching trace by ID {trace_id}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch trace: {str(e)}"
                )

        keys = (
            start_time,
            end_time,
            tuple(categories),
            tuple(values),
            tuple(operations),
            log_group_name
        )

        # Extract service names, service environment, and log search
        # values from categories/values/operations
        service_name_values = []
        service_name_operations = []
        service_environment_values = []
        service_environment_operations = []
        log_search_values = []
        log_search_operations = []

        # Create lists to hold remaining categories/values/operations
        # after extraction
        remaining_categories = []
        remaining_values = []
        remaining_operations = []

        # Process each category/value/operation triplet
        for i, category in enumerate(categories):
            if i < len(values) and i < len(operations):
                value = values[i]
                operation = operations[i]

                if category == "service_name":
                    service_name_values.append(value)
                    service_name_operations.append(operation)
                elif category == "service_environment":
                    service_environment_values.append(value)
                    service_environment_operations.append(operation)
                elif category == "log":
                    log_search_values.append(value)
                    log_search_operations.append(operation)
                else:
                    # Keep non-service categories
                    remaining_categories.append(category)
                    remaining_values.append(value)
                    remaining_operations.append(operation)
            else:
                # Keep categories without corresponding values/operations
                remaining_categories.append(category)

        # Update categories/values/operations with remaining items
        categories = remaining_categories
        values = remaining_values
        operations = remaining_operations

        # Convert operations to Operation enum
        operations = [Operation(op) for op in operations]
        service_name_operations = [Operation(op) for op in service_name_operations]
        service_environment_operations = [
            Operation(op) for op in service_environment_operations
        ]

        cached_traces: list[Trace] | None = await self.cache.get(keys)
        if cached_traces:
            resp = ListTraceResponse(traces=cached_traces)
            return resp.model_dump()

        try:
            observe_provider = await self.get_observe_provider(request)
            traces: list[Trace] = await observe_provider.trace_client.get_recent_traces(
                start_time=start_time,
                end_time=end_time,
                log_group_name=log_group_name,
                service_name_values=service_name_values,
                service_name_operations=service_name_operations,
                service_environment_values=service_environment_values,
                service_environment_operations=service_environment_operations,
                categories=categories,
                values=values,
                operations=operations,
            )

            # Filter traces by log content if log search is specified
            if log_search_values:
                traces = await self._filter_traces_by_log_content(
                    request=request,
                    traces=traces,
                    start_time=start_time,
                    end_time=end_time,
                    log_group_name=log_group_name,
                    log_search_values=log_search_values,
                    log_search_operations=log_search_operations
                )

            # Cache the traces for 10 minutes
            await self.cache.set(keys, traces)
            resp = ListTraceResponse(traces=traces)
            return resp.model_dump()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_chat_history(
        self,
        request: Request,
        req_data: GetChatHistoryRequest = Depends(),
    ) -> dict[str,
              Any]:
        # Get user credentials (fake in local mode, real in remote mode)
        _, _, _ = get_user_credentials(request)

        history: list[dict[str,
                           Any]
                      ] = await self.db_client.get_chat_history(chat_id=req_data.chat_id)
        chat_history = ChatHistoryResponse(history=[])
        for item in history:
            # For user only shows the user message
            # without the context information
            if item["role"] == "user":
                if "user_message" in item:
                    message = item["user_message"]
                else:
                    message = item["content"]
            else:
                message = item["content"]
            # Reference is only for assistant message
            if item["role"] == "assistant" and "reference" in item:
                reference = [Reference(**ref) for ref in item["reference"]]
            else:
                reference = []

            # Skip chunk messages except the first one
            # For now chunk_id is only used for user message
            # where we cut the user message + context into chunks
            chunk_id = 0
            if "chunk_id" in item and item["chunk_id"] > 0:
                continue
            if "chunk_id" in item:
                chunk_id = int(item["chunk_id"])
            if "action_type" in item:
                action_type = item["action_type"]
            else:
                action_type = None
            if "status" in item:
                status = item["status"]
            else:
                status = None
            chat_history.history.append(
                ChatbotResponse(
                    time=item["timestamp"],
                    message=message,
                    reference=reference,
                    message_type=item["role"],
                    chat_id=item["chat_id"],
                    chunk_id=chunk_id,
                    action_type=action_type,
                    status=status,
                )
            )
        return chat_history.model_dump()

    async def get_logs_by_trace_id(
        self,
        request: Request,
        req_data: GetLogByTraceIdRequest = Depends(),
    ) -> dict[str,
              Any]:
        r"""Get trace logs by trace ID.

        Args:
            req_data (GetLogByTraceIdRequest): Request object
                containing trace ID.

        Returns:
            dict[str, Any]: Dictionary containing trace logs
                for the given trace ID.
        """
        _, _, user_sub = get_user_credentials(request)
        log_group_name = hash_user_sub(user_sub)

        # Try to get cached logs
        keys = (req_data.trace_id, req_data.start_time, req_data.end_time, log_group_name)
        cached_logs: TraceLogs | None = await self.cache.get(keys)
        if cached_logs:
            resp = GetLogByTraceIdResponse(trace_id=req_data.trace_id, logs=cached_logs)
            return resp.model_dump()

        try:
            observe_provider = await self.get_observe_provider(request)
            logs: TraceLogs = await observe_provider.log_client.get_logs_by_trace_id(
                trace_id=req_data.trace_id,
                start_time=req_data.start_time,
                end_time=req_data.end_time,
                log_group_name=log_group_name,
            )
            # Cache the logs for 10 minutes
            await self.cache.set(keys, logs)
            resp = GetLogByTraceIdResponse(trace_id=req_data.trace_id, logs=logs)
            return resp.model_dump()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_chat_metadata_history(
        self,
        request: Request,
        req_data: GetChatMetadataHistoryRequest = Depends(),
    ) -> dict[str,
              Any]:
        # Get user credentials (fake in local mode, real in remote mode)
        _, _, _ = get_user_credentials(request)
        chat_metadata_history: ChatMetadataHistory = await (
            self.db_client.get_chat_metadata_history(trace_id=req_data.trace_id)
        )
        return chat_metadata_history.model_dump()

    async def get_chat_metadata(
        self,
        request: Request,
        req_data: GetChatMetadataRequest = Depends(),
    ) -> dict[str,
              Any]:
        # Get user credentials (fake in local mode, real in remote mode)
        _, _, _ = get_user_credentials(request)
        chat_metadata: ChatMetadata | None = await (
            self.db_client.get_chat_metadata(chat_id=req_data.chat_id)
        )
        if chat_metadata is None:
            return {}
        return chat_metadata.model_dump()

    async def get_chat_reasoning(
        self,
        request: Request,
        chat_id: str,
    ) -> dict[str,
              Any]:
        """Get reasoning/thinking data for a specific chat."""
        # Get user credentials (fake in local mode, real in remote mode)
        _, _, _ = get_user_credentials(request)

        try:
            # Query for reasoning data from the database
            # Look for records with is_streaming=True for the given chat_id
            reasoning_records = await self.db_client.get_chat_reasoning(chat_id=chat_id)

            return {"chat_id": chat_id, "reasoning": reasoning_records}

        except Exception as e:
            self.logger.error(f"Error fetching reasoning for chat {chat_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch reasoning data")

    async def get_github_token(self, user_email: str) -> str | None:
        return await self.db_client.get_integration_token(
            user_email=user_email,
            token_type=ResourceType.GITHUB.value,
        )

    async def post_chat(
        self,
        request: Request,
        req_data: ChatRequest,
    ) -> dict[str,
              Any]:
        # Get basic information ###############################################
        user_email, _, user_sub = get_user_credentials(request)
        log_group_name = hash_user_sub(user_sub)
        trace_id = req_data.trace_id
        span_ids = req_data.span_ids
        start_time = req_data.start_time
        end_time = req_data.end_time
        model = req_data.model
        message = req_data.message
        chat_id = req_data.chat_id
        service_name = req_data.service_name
        mode = req_data.mode
        # TODO: For other model testing
        req_data.model
        provider = req_data.provider

        if model == ChatModel.AUTO:
            model = ChatModel.GPT_4O
        # Still use the GPT-4o model for main model for now
        elif provider == Provider.CUSTOM:
            model = ChatModel.GPT_4O

        if req_data.time.tzinfo:
            orig_time = req_data.time.astimezone(timezone.utc)
        else:
            orig_time = req_data.time.replace(tzinfo=timezone.utc)

        # Get OpenAI token ####################################################
        # openai_token = await self.db_client.get_integration_token(
        #     user_email=user_email,
        #     token_type=ResourceType.OPENAI.value,
        # )
        
        openai_token = os.getenv("OPENAI_API")

        if openai_token is None and self.chat.local_mode:
            response = ChatbotResponse(
                time=orig_time,
                message=(
                    "OpenAI token is not found, please "
                    "add it in the settings page."
                ),
                reference=[],
                message_type=MessageType.ASSISTANT,
                chat_id=chat_id,
            )
            return response.model_dump()

        # Get whether it's the first chat #####################################
        first_chat: bool = False
        if await self.db_client.get_chat_metadata(chat_id=chat_id) is None:
            first_chat = True

        # Get the title and GitHub related information ########################
        title, github_related = await asyncio.gather(
            summarize_title(
                user_message=message,
                client=self.chat.chat_client,
                openai_token=openai_token,
                model=ChatModel.GPT_4_1_MINI,  # Use GPT-4.1-mini for title
                first_chat=first_chat,
                user_sub=user_sub,
            ),
            is_github_related(
                user_message=message,
                client=self.chat.chat_client,
                openai_token=openai_token,
                model=ChatModel.GPT_4O,
                user_sub=user_sub,
            ))

        # Get the title of the chat if it's the first chat ####################
        if first_chat and title is not None:
            await self.db_client.insert_chat_metadata(
                metadata={
                    "chat_id": chat_id,
                    "timestamp": orig_time,
                    "chat_title": title,
                    "trace_id": trace_id,
                }
            )

        # Get whether the user message is related to GitHub ###################
        set_github_related(github_related)
        is_github_issue: bool = False
        is_github_pr: bool = False
        source_code_related: bool = False
        source_code_related = github_related.source_code_related
        # For now only allow issue and PR creation for agent and non-local mode
        if mode == ChatMode.AGENT:
            is_github_issue = github_related.is_github_issue
            is_github_pr = github_related.is_github_pr

        # Get the trace #######################################################
        observe_provider = await self.get_observe_provider(request)
        selected_trace: Trace | None = None

        # If we have a trace_id, fetch it directly
        if trace_id:
            selected_trace = await observe_provider.trace_client.get_trace_by_id(
                trace_id=trace_id,
                categories=None,
                values=None,
                operations=None,
            )
        else:
            # Otherwise get recent traces and search
            keys = (start_time, end_time, service_name, log_group_name)
            cached_traces: list[Trace] | None = await self.cache.get(keys)
            if cached_traces:
                traces = cached_traces
            else:
                traces: list[Trace
                             ] = await observe_provider.trace_client.get_recent_traces(
                                 start_time=start_time,
                                 end_time=end_time,
                                 log_group_name=log_group_name,
                                 service_name_values=None,
                                 service_name_operations=None,
                                 service_environment_values=None,
                                 service_environment_operations=None,
                                 categories=None,
                                 values=None,
                                 operations=None,
                             )
            for trace in traces:
                if trace.id == trace_id:
                    selected_trace = trace
                    break
        spans_latency_dict: dict[str, float] = {}

        # Compute the span latencies recursively ##############################
        if selected_trace:
            collect_spans_latency_recursively(
                selected_trace.spans,
                spans_latency_dict,
            )
            # Then select spans latency by span_ids
            # if span_ids is not empty
            if len(span_ids) > 0:
                selected_spans_latency_dict: dict[str, float] = {}
                for span_id, latency in spans_latency_dict.items():
                    if span_id in span_ids:
                        selected_spans_latency_dict[span_id] = latency
                spans_latency_dict = selected_spans_latency_dict

        # Get the logs ########################################################
        keys = (trace_id, start_time, end_time, log_group_name)
        logs: TraceLogs | None = await self.cache.get(keys)
        if logs is None:
            observe_provider = await self.get_observe_provider(request)
            logs = await observe_provider.log_client.get_logs_by_trace_id(
                trace_id=trace_id,
                start_time=start_time,
                end_time=end_time,
                log_group_name=log_group_name,
            )
            # Cache the logs for 10 minutes
            await self.cache.set(keys, logs)

        # Get GitHub token
        github_token = await self.get_github_token(user_email)

        # Only fetch the source code if it's source code related ##############
        github_tasks: list[tuple[str, str, str, str]] = []
        log_entries_to_update: list = []
        github_task_keys: set[tuple[str, str, str, str]] = set()
        if source_code_related:
            for log in logs.logs:
                for span_id, span_logs in log.items():
                    for log_entry in span_logs:
                        if log_entry.git_url:
                            owner, repo_name, ref, file_path, line_number = \
                                parse_github_url(log_entry.git_url)
                            # Create task for this GitHub file fetch
                            # notice that there is no await here
                            if is_github_pr:
                                line_context_len = 200
                            else:
                                line_context_len = 5
                            task = self.handle_github_file(
                                owner,
                                repo_name,
                                file_path,
                                ref,
                                line_number,
                                github_token,
                                line_context_len,
                            )
                            github_task_keys.add((owner, repo_name, file_path, ref))
                            github_tasks.append(task)
                            log_entries_to_update.append(log_entry)

            # Process tasks in batches of 20 to avoid overwhelming API
            batch_size = 20
            for i in range(0, len(github_tasks), batch_size):
                batch_tasks = github_tasks[i:i + batch_size]
                batch_log_entries = log_entries_to_update[i:i + batch_size]

                time = datetime.now().astimezone(timezone.utc)
                await self.db_client.insert_chat_record(
                    message={
                        "chat_id": chat_id,
                        "timestamp": time,
                        "role": MessageType.GITHUB.value,
                        "content": "Fetching GitHub file content... ",
                        "trace_id": trace_id,
                        "chunk_id": i // batch_size,
                        "action_type": ActionType.GITHUB_GET_FILE.value,
                        "status": ActionStatus.PENDING.value,
                    }
                )

                # Execute batch in parallel
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Process results and update log entries
                num_failed = 0
                for log_entry, code_response in zip(batch_log_entries, batch_results):
                    # Handle exceptions gracefully
                    if isinstance(code_response, Exception):
                        num_failed += 1
                        continue

                    # If error message is not None, skip the log entry
                    if code_response["error_message"]:
                        num_failed += 1
                        continue

                    log_entry.line = code_response["line"]
                    # For now disable the context as it may hallucinate
                    # on the case such as count number of error logs
                    if not is_github_pr:
                        log_entry.lines_above = None
                        log_entry.lines_below = None
                    else:
                        log_entry.lines_above = code_response["lines_above"]
                        log_entry.lines_below = code_response["lines_below"]

                time = datetime.now().astimezone(timezone.utc)
                num_success = len(batch_log_entries) - num_failed
                await self.db_client.insert_chat_record(
                    message={
                        "chat_id":
                        chat_id,
                        "timestamp":
                        time,
                        "role":
                        MessageType.GITHUB.value,
                        "content":
                        "Finished fetching GitHub file content for "
                        f"{num_success} times. Failed to "
                        f"fetch {num_failed} times.",
                        "trace_id":
                        trace_id,
                        "chunk_id":
                        i // batch_size,
                        "action_type":
                        ActionType.GITHUB_GET_FILE.value,
                        "status":
                        ActionStatus.SUCCESS.value,
                    }
                )

        chat_history = await self.db_client.get_chat_history(chat_id=chat_id)

        node: SpanNode = build_heterogeneous_tree(selected_trace.spans[0], logs.logs)

        if len(span_ids) > 0:
            # Use BFS to find the first span matching any of target span_ids
            queue = deque([node])
            target_set = set(span_ids)

            while queue:
                current = queue.popleft()
                # Check if current node matches any target span
                if current.span_id in target_set:
                    node = current
                    break
                # Add children to queue for next level
                for child in current.children_spans:
                    queue.append(child)

        if mode == ChatMode.AGENT and (is_github_issue or is_github_pr):
            issue_response: ChatbotResponse | None = None
            pr_response: ChatbotResponse | None = None
            issue_message: str = message
            pr_message: str = message
            if is_github_issue and is_github_pr:
                separate_issue_and_pr_output: SeparateIssueAndPrInput = \
                    await separate_issue_and_pr(
                        user_message=message,
                        client=self.chat.chat_client,
                        openai_token=openai_token,
                        model=model,
                        user_sub=user_sub,
                    )
                issue_message = separate_issue_and_pr_output.issue_message
                pr_message = separate_issue_and_pr_output.pr_message
            if is_github_issue:
                issue_response = await self.agent.chat(
                    trace_id=trace_id,
                    chat_id=chat_id,
                    user_message=issue_message,
                    model=model,
                    db_client=self.db_client,
                    chat_history=chat_history,
                    timestamp=orig_time,
                    tree=node,
                    user_sub=user_sub,
                    openai_token=openai_token,
                    github_token=github_token,
                    github_file_tasks=github_task_keys,
                    is_github_issue=True,
                    is_github_pr=False,
                    provider=provider,
                )
            if is_github_pr:
                pr_response = await self.agent.chat(
                    trace_id=trace_id,
                    chat_id=chat_id,
                    user_message=pr_message,
                    model=model,
                    db_client=self.db_client,
                    chat_history=chat_history,
                    timestamp=orig_time,
                    tree=node,
                    user_sub=user_sub,
                    openai_token=openai_token,
                    github_token=github_token,
                    github_file_tasks=github_task_keys,
                    is_github_issue=False,
                    is_github_pr=True,
                    provider=provider,
                )
            # TODO: sequential tool calls
            if issue_response and pr_response:
                summary_response = await summarize_chatbot_output(
                    issue_response=issue_response,
                    pr_response=pr_response,
                    client=self.chat.chat_client,
                    openai_token=openai_token,
                    model=model,
                    user_sub=user_sub,
                )
                return summary_response.model_dump()
            elif issue_response:
                return issue_response.model_dump()
            elif pr_response:
                return pr_response.model_dump()
            else:
                raise ValueError("Should not reach here")
        else:
            response: ChatbotResponse = await self.chat.chat(
                trace_id=trace_id,
                chat_id=chat_id,
                user_message=message,
                model=model,
                db_client=self.db_client,
                chat_history=chat_history,
                timestamp=orig_time,
                tree=node,
                user_sub=user_sub,
                openai_token=openai_token,
            )
            return response.model_dump()

    async def _filter_traces_by_log_content(
        self,
        request: Request,
        traces: list[Trace],
        start_time: datetime,
        end_time: datetime,
        log_group_name: str,
        log_search_values: list[str],
        log_search_operations: list[Operation]
    ) -> list[Trace]:
        """Filter traces by log content using CloudWatch Insights.

        Args:
            traces: List of traces to filter
            start_time: Start time for log query
            end_time: End time for log query
            log_group_name: Log group name
            log_search_values: List of search terms to look for in logs
            log_search_operations: List of operations (currently only '=' supported)

        Returns:
            Filtered list of traces that contain the searched log content
        """
        if not log_search_values:
            return traces

        search_term = log_search_values[0]

        try:
            # Use CloudWatch Insights to find trace IDs
            # from logs containing search term
            # TODO: change all of this to JSON format
            # Log format: timestamp;level;service;function;
            # org;project;env;trace_id;span_id;details
            # Extract trace_id (field 8, 0-indexed field 7)
            # from semicolon-separated logs

            # Single query to get all matching trace IDs
            observe_provider = await self.get_observe_provider(request)
            matching_trace_ids = \
                await observe_provider.log_client.get_trace_ids_from_logs(
                    start_time=start_time,
                    end_time=end_time,
                    log_group_name=log_group_name,
                    search_term=search_term
                )

            if not matching_trace_ids:
                return []

            # Convert to set for fast O(1) lookup
            trace_id_set = set(matching_trace_ids)

            # Filter traces by matching trace IDs
            filtered_traces = [trace for trace in traces if trace.id in trace_id_set]
            return filtered_traces

        except Exception as e:
            self.logger.error(f"Failed to filter traces by log content: {e}")
            # Fallback: return all traces if log filtering fails
            return traces
