import json
from typing import Annotated, Any, Generator, Optional, Sequence, TypedDict, Union
from uuid import uuid4

import mlflow
from databricks_langchain import (
    ChatDatabricks,
    UCFunctionToolkit,
    VectorSearchRetrieverTool,
)
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import BaseTool

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode

from mlflow.entities import SpanType
from mlflow.pyfunc import ResponsesAgent
from mlflow.models import ModelConfig
from mlflow.models.resources import DatabricksFunction, DatabricksServingEndpoint
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

# Enable MLflow LangChain auto-trace
mlflow.langchain.autolog()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    custom_inputs: Optional[dict[str, Any]]
    custom_outputs: Optional[dict[str, Any]]


def create_tool_calling_agent(
    model: LanguageModelLike,
    tools: Union[ToolNode, Sequence[BaseTool]],
    system_prompt: Optional[str] = None,
):
    """Create a tool-calling agent using LangGraph."""
    model = model.bind_tools(tools)

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        return "continue" if isinstance(last, AIMessage) and last.tool_calls else "end"

    pre = (
        RunnableLambda(lambda s: [{"role": "system", "content": system_prompt}] + s["messages"])
        if system_prompt
        else RunnableLambda(lambda s: s["messages"])
    )
    model_runnable = pre | model

    def call_model(state: AgentState, config: RunnableConfig):
        return {"messages": [model_runnable.invoke(state, config)]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", RunnableLambda(call_model))
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
    graph.add_edge("tools", "agent")

    return graph.compile()


class LangGraphResponsesAgent(ResponsesAgent):
    """
    Agent that uses LangGraph for tool calling and Responses API for I/O.
    Matches the ai-agent demo pattern.
    """

    def __init__(
        self,
        uc_catalog: str,
        schema: str,
        llm_endpoint_name: str,
        system_prompt: str,
        vector_search_config: dict,
        llm_temperature: float = 0.01,
        llm_max_tokens: int = 500,
        max_history_messages: int = 20,
    ):
        """
        Initialize the agent with configuration.

        Args:
            uc_catalog: Unity Catalog name
            schema: Schema name
            llm_endpoint_name: Foundation model endpoint name
            system_prompt: System prompt for the agent
            vector_search_config: Dict with vector_search_index, embedding_model, num_results, columns, query_type
            llm_temperature: LLM temperature setting
            llm_max_tokens: Maximum tokens for LLM response
            max_history_messages: Maximum conversation history to maintain
        """
        self.uc_catalog = uc_catalog
        self.schema = schema
        self.llm_endpoint_name = llm_endpoint_name
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages

        # Create LLM
        self.llm = ChatDatabricks(
            endpoint=llm_endpoint_name,
            temperature=llm_temperature,
            max_tokens=llm_max_tokens,
        )

        # Create UC function tools
        uc_function_names = [
            f"{uc_catalog}.{schema}.ask_ai",
            f"{uc_catalog}.{schema}.summarize",
            f"{uc_catalog}.{schema}.translate",
        ]
        self.tools: list[BaseTool] = UCFunctionToolkit(function_names=uc_function_names).tools

        # Add vector search retriever tool
        if vector_search_config:
            vs_index_name = f"{uc_catalog}.{schema}.{vector_search_config['vector_search_index']}"
            self.tools.append(
                VectorSearchRetrieverTool(
                    index_name=vs_index_name,
                    tool_name="vector_search_retriever",
                    tool_description="Retrieves information from Databricks documentation Vector Search.",
                    embedding_model_name=vector_search_config.get("embedding_model"),
                    num_results=vector_search_config.get("num_results", 1),
                    columns=vector_search_config.get("columns", ["url", "content"]),
                    query_type=vector_search_config.get("query_type", "ANN"),
                    filters={},  # Explicitly set empty filters to avoid default category/component filters
                )
            )

        # Create the agent graph
        self.agent = create_tool_calling_agent(self.llm, self.tools, system_prompt)

    def _responses_to_cc(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert Responses API message to ChatCompletion format."""
        msg_type = message.get("type")
        if msg_type == "function_call":
            return [{
                "role": "assistant",
                "content": "tool_call",
                "tool_calls": [{
                    "id": message["call_id"],
                    "type": "function",
                    "function": {
                        "arguments": message["arguments"],
                        "name": message["name"],
                    },
                }],
            }]
        elif msg_type == "message" and isinstance(message["content"], list):
            return [{"role": message["role"], "content": content["text"]} for content in message["content"]]
        elif msg_type == "reasoning":
            return [{"role": "assistant", "content": json.dumps(message["summary"])}]
        elif msg_type == "function_call_output":
            return [{
                "role": "tool",
                "content": message["output"],
                "tool_call_id": message["call_id"],
            }]
        filtered = {k: v for k, v in message.items() if k in {"role", "content", "name", "tool_calls", "tool_call_id"}}
        return [filtered] if filtered else []

    def _langchain_to_responses(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert LangChain messages to Responses API format."""
        for message in messages:
            message = message.model_dump()
            if message["type"] == "ai":
                if tool_calls := message.get("tool_calls"):
                    return [
                        self.create_function_call_item(
                            id=message.get("id") or str(uuid4()),
                            call_id=tc["id"],
                            name=tc["name"],
                            arguments=json.dumps(tc["args"]),
                        )
                        for tc in tool_calls
                    ]
                mlflow.update_current_trace(response_preview=message["content"])
                return [self.create_text_output_item(
                    text=message["content"],
                    id=message.get("id") or str(uuid4())
                )]
            elif message["type"] == "tool":
                # Tool content must be a string for ResponsesAgent
                content = message["content"]
                if not isinstance(content, str):
                    content = str(content) if content else ""
                return [self.create_function_call_output_item(
                    call_id=message["tool_call_id"],
                    output=content
                )]
        return []

    @mlflow.trace(span_type=SpanType.AGENT)
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """Predict method for batch inference."""
        outputs = [
            event.item for event in self.predict_stream(request)
            if event.type == "response.output_item.done"
        ]
        return ResponsesAgentResponse(output=outputs, custom_outputs=request.custom_inputs)

    @mlflow.trace(span_type=SpanType.AGENT)
    def predict_stream(
        self, request: ResponsesAgentRequest,
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        """Streaming predict method."""
        cc_msgs = []
        mlflow.update_current_trace(request_preview=request.input[0].content)
        for msg in request.input:
            cc_msgs.extend(self._responses_to_cc(msg.model_dump()))

        # Limit history to the most recent max_history_messages
        if len(cc_msgs) > self.max_history_messages:
            cc_msgs = cc_msgs[-self.max_history_messages:]

        # Stream agent execution
        for event in self.agent.stream({"messages": cc_msgs}, stream_mode=["updates", "messages"]):
            if event[0] == "updates":
                for node_data in event[1].values():
                    for item in self._langchain_to_responses(node_data["messages"]):
                        yield ResponsesAgentStreamEvent(type="response.output_item.done", item=item)
            elif event[0] == "messages":
                try:
                    chunk = event[1][0]
                    if isinstance(chunk, AIMessageChunk) and (content := chunk.content):
                        yield ResponsesAgentStreamEvent(
                            **self.create_text_delta(delta=content, item_id=chunk.id),
                        )
                except Exception:
                    pass

    def get_resources(self):
        """Get Databricks resources for MLflow registration."""
        res = [DatabricksServingEndpoint(endpoint_name=self.llm.endpoint)]
        for t in self.tools:
            if isinstance(t, VectorSearchRetrieverTool):
                res.extend(t.resources)
            elif hasattr(t, "uc_function_name"):
                res.append(DatabricksFunction(function_name=t.uc_function_name))
        return res


# Load configuration from YAML
model_config = ModelConfig(development_config="ModelConfig.yml")

# Instantiate agent with configuration
AGENT = LangGraphResponsesAgent(
    uc_catalog=model_config.get("catalog"),
    schema=model_config.get("schema"),
    llm_endpoint_name=model_config.get("llm_config")["endpoint"],
    system_prompt=model_config.get("system_prompt"),
    vector_search_config=model_config.get("vector_search_config"),
    llm_temperature=model_config.get("llm_config").get("temperature", 0.01),
    llm_max_tokens=model_config.get("llm_config").get("max_tokens", 500),
    max_history_messages=20,
)

# Register agent with MLflow for inference
mlflow.models.set_model(AGENT)