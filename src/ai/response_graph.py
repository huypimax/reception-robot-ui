"""
LangGraph workflow cho Q&A system - All-in-one file
"""
import os
import json
import datetime
from typing import Literal, TypedDict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from language_manager import get_language_manager, get_string
import utilities.constants as constants
import utilities.string_ids as stringIds


# ==================== State Schema ====================
class GraphState(TypedDict):
    """State của LangGraph workflow"""
    query: str
    messages: List[BaseMessage]
    reply: Optional[str]
    next_step: Optional[Literal["offline", "faq", "llm", "tools", "end", "navigation", "delivery"]]
    tool_results: Optional[List[dict]]
    error: Optional[str]
    context: Optional[dict]


# ==================== Helper Functions ====================
def check_offline_responses(query: str, last_reply: str = "") -> Optional[str]:
    """Kiểm tra và trả về câu trả lời offline nếu có"""
    query_lower = query.lower()
    lang_manager = get_language_manager()
    
    if any(kw in query_lower for kw in constants.KEYWORDS_GOODBYE):
        return get_string(stringIds.AI_OFFLINE_GOODBYE)
    elif any(kw in query_lower for kw in constants.KEYWORDS_TIME):
        current_time = datetime.datetime.now().strftime(constants.TIME_FORMAT)
        return get_string(stringIds.AI_OFFLINE_TIME, time=current_time)
    elif any(kw in query_lower for kw in constants.KEYWORDS_DATE):
        days = [
            get_string(stringIds.AI_DAYS_MONDAY), get_string(stringIds.AI_DAYS_TUESDAY), get_string(stringIds.AI_DAYS_WEDNESDAY),
            get_string(stringIds.AI_DAYS_THURSDAY), get_string(stringIds.AI_DAYS_FRIDAY), get_string(stringIds.AI_DAYS_SATURDAY), get_string(stringIds.AI_DAYS_SUNDAY)
        ]
        months = [
            "", get_string(stringIds.AI_MONTHS_JANUARY), get_string(stringIds.AI_MONTHS_FEBRUARY), get_string(stringIds.AI_MONTHS_MARCH),
            get_string(stringIds.AI_MONTHS_APRIL), get_string(stringIds.AI_MONTHS_MAY), get_string(stringIds.AI_MONTHS_JUNE),
            get_string(stringIds.AI_MONTHS_JULY), get_string(stringIds.AI_MONTHS_AUGUST), get_string(stringIds.AI_MONTHS_SEPTEMBER),
            get_string(stringIds.AI_MONTHS_OCTOBER), get_string(stringIds.AI_MONTHS_NOVEMBER), get_string(stringIds.AI_MONTHS_DECEMBER)
        ]
        now = datetime.datetime.now()
        date_str = f"{days[now.weekday()]}, {now.day} {months[now.month]} {now.year}"
        return get_string(stringIds.AI_OFFLINE_DATE, date=date_str)
    elif any(kw in query_lower for kw in constants.KEYWORDS_REPEAT):
        return last_reply or get_string(stringIds.AI_OFFLINE_REPEAT)
    return None


def check_faq(query: str) -> Optional[str]:
    """Kiểm tra câu hỏi có trong FAQ không"""
    query_lower = query.lower()

    if any(kw in query_lower for kw in constants.KEYWORDS_HCMUT):
        return get_string(stringIds.AI_FAQ_HCMUT)
    
    elif any(kw in query_lower for kw in constants.KEYWORDS_IVS):
        return get_string(stringIds.AI_FAQ_IVS)

    elif any(kw in query_lower for kw in constants.KEYWORDS_FABLAB):
        return get_string(stringIds.AI_FAQ_FABLAB)

    elif any(kw in query_lower for kw in constants.KEYWORDS_MEMBERS):
        return get_string(stringIds.AI_FAQ_MEMBERS)

    elif any(kw in query_lower for kw in constants.KEYWORDS_CREATOR):
        return get_string(stringIds.AI_FAQ_CREATOR)

    elif any(kw in query_lower for kw in constants.KEYWORDS_NAME):
        return get_string(stringIds.AI_FAQ_NAME)
        
    elif any(kw in query_lower for kw in constants.KEYWORDS_HELP):
        return get_string(stringIds.AI_FAQ_HELP)
    
    return None


# ==================== Tools ====================
@tool
def search_web(query: str) -> str:
    """Use this web search tool ONLY to retrieve REAL-TIME, UP-TO-DATE data, 
    the LATEST NEWS, or information about events that have occurred since 2023. 
    DO NOT use this tool for questions regarding history, famous people (such as Albert Einstein), 
    or widely known general knowledge."""
    import requests
    endpoint = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": 1}
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        abstract = data.get("AbstractText", "")
        return abstract or get_string(stringIds.AI_WEB_SEARCH_NO_INFO)
    except Exception as e:
        return get_string(stringIds.AI_WEB_SEARCH_ERROR, error=str(e))


@tool
def get_weather(city: str) -> str:
    """Retrieves the current weather forecast. 
    If the user's query does not specify a location, the system will automatically 
    prioritize checking the weather for the robot's default location, 
    which is Diên Hồng Ward, Ho Chi Minh City, Vietnam."""
    import requests
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    lang_manager = get_language_manager()
    current_lang = lang_manager.get_current_language()
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        api_key = config.get("openweathermap_api_key")
        if not api_key:
            return "API key for OpenWeatherMap is missing in config.json."
    except FileNotFoundError:
        return "Configuration file 'config.json' not found."
    except json.JSONDecodeError:
        return "Error decoding 'config.json'. Please check the file format."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(base_url, params={
            "q": city, "appid": api_key, "units": "metric", "lang": current_lang
        })
        if response.status_code == 200:
            data = response.json()
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            return get_string(stringIds.AI_WEATHER_CURRENT, city=city, description=weather_description, 
                    temp=temperature, feels_like=feels_like, humidity=humidity)
        elif response.status_code == 404:
            return get_string(stringIds.AI_WEATHER_NOT_FOUND, city=city)
        else:
            return get_string(stringIds.AI_WEATHER_ERROR, status=response.status_code, reason=response.reason)
    except requests.RequestException as e:
        return get_string(stringIds.AI_WEATHER_EXCEPTION, error=str(e))


ALL_TOOLS = [search_web, get_weather]


# ==================== ResponseGraph Class ====================
class ResponseGraph:
    """LangGraph workflow cho xử lý câu hỏi của user"""
    
    def __init__(self, api_key: str, model_name: str = constants.MODEL_NAME, initial_context: list = None):
        self.api_key = api_key
        self.model_name = model_name
        self.initial_context = initial_context or []
        self.last_reply = ""
        self._conversation_messages = []
        self.lang_manager = get_language_manager()
        
        # Khởi tạo LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7
        )
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)
        
        # Tạo graph
        self.graph = self._create_graph()
        self.app = self.graph.compile()
    
    def reset_conversation(self):
        """Reset conversation để sử dụng ngôn ngữ mới"""
        self._conversation_messages = []
        self.last_reply = ""
    
    def _create_graph(self) -> StateGraph:
        """Tạo LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Thêm nodes
        workflow.add_node("offline_check", self._offline_check_node)
        workflow.add_node("faq_check", self._faq_check_node)
        workflow.add_node("llm_call", self._llm_call_node)
        workflow.add_node("tool_execution", self._tool_execution_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Entry point
        workflow.set_entry_point("offline_check")
        
        # Conditional routing
        workflow.add_conditional_edges("offline_check", self._route_after_offline, {
            "offline": "finalize", "continue": "faq_check"
        })
        workflow.add_conditional_edges("faq_check", self._route_after_faq, {
            "faq": "finalize", "continue": "llm_call"
        })
        workflow.add_conditional_edges("llm_call", self._route_after_llm, {
            "tools": "tool_execution", "end": "finalize"
        })
        
        workflow.add_edge("tool_execution", "llm_call")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    def _offline_check_node(self, state: GraphState) -> GraphState:
        """Node kiểm tra offline responses"""
        query = state.get("query", "").lower()
        offline_reply = check_offline_responses(query, self.last_reply)
        
        if offline_reply:
            return {**state, "reply": offline_reply, "next_step": "offline"}
        return {**state, "next_step": "continue"}
    
    def _faq_check_node(self, state: GraphState) -> GraphState:
        """Node kiểm tra FAQ"""
        query = state.get("query", "")
        faq_answer = check_faq(query)
        
        if faq_answer:
            return {**state, "reply": faq_answer, "next_step": "faq"}
        return {**state, "next_step": "continue"}
    
    def _get_system_prompt(self) -> str:
        """Lấy system prompt dựa trên ngôn ngữ hiện tại"""
        lang_manager = get_language_manager()
        current_lang = lang_manager.get_current_language()
        language_name = constants.LANGUAGE_NAME_VI if current_lang == "vi" else constants.LANGUAGE_NAME_EN
        return get_string(stringIds.AI_SYSTEM_PROMPT, language=language_name)
    
    def _llm_call_node(self, state: GraphState) -> GraphState:
        """Node gọi LLM"""
        query = state.get("query", "")
        messages = state.get("messages", [])
        lang_manager = get_language_manager()
        current_lang = lang_manager.get_current_language()
        language_name = "TIẾNG VIỆT" if current_lang == "vi" else "ENGLISH"
        
        # Đảm bảo system prompt luôn có ở đầu
        has_system_prompt = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system_prompt:
            messages.insert(0, SystemMessage(content=self._get_system_prompt()))
        
        # Thêm tool results nếu có
        tool_results = state.get("tool_results")
        if tool_results:
            for result in tool_results:
                tool_name = result.get("tool", "")
                tool_result = result.get("result", "")
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=f"{tool_name}_call"))
        
        # Thêm query mới với prompt ngôn ngữ
        if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != query:
            # Thêm prompt rõ ràng vào query để đảm bảo trả lời đúng ngôn ngữ
            language_query = f"{query}\n\n{get_string(stringIds.AI_QUERY_NOTE, language=language_name)}"
            messages.append(HumanMessage(content=language_query))
        
        try:
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            # Kiểm tra tool calls
            if hasattr(response, "tool_calls") and response.tool_calls and len(response.tool_calls) > 0:
                return {**state, "messages": messages, "next_step": "tools", "tool_results": []}
            
            # Không có tool calls
            reply = response.content if hasattr(response, "content") else str(response)
            return {**state, "messages": messages, "reply": reply, "next_step": "end"}
            
        except Exception as e:
            print(f"Error in LLM call: {e}")
            return {**state, "reply": get_string(stringIds.AI_ERROR_RESPONSE), "error": str(e), "next_step": "end"}
    
    def _tool_execution_node(self, state: GraphState) -> GraphState:
        """Node thực thi tools"""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if not (last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls):
            return {**state, "next_step": "end"}
        
        tool_results = []
        for tool_call in last_message.tool_calls:
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
            else:
                tool_name = getattr(tool_call, "name", "")
                tool_args = getattr(tool_call, "args", {})
                if hasattr(tool_args, "dict"):
                    tool_args = tool_args.dict()
            
            for tool in ALL_TOOLS:
                if tool.name == tool_name:
                    try:
                        result = tool.invoke(tool_args)
                        tool_results.append({"tool": tool_name, "result": result})
                        print(f"DEBUG: Executed tool {tool_name}")
                    except Exception as e:
                        print(f"DEBUG: Error executing tool {tool_name}: {e}")
                        tool_results.append({"tool": tool_name, "result": f"Error: {str(e)}"})
                    break
        
        return {**state, "tool_results": tool_results, "next_step": "continue"}
    
    def _finalize_node(self, state: GraphState) -> GraphState:
        """Node cuối cùng - lưu reply"""
        reply = state.get("reply", "")
        if reply:
            self.last_reply = reply
        return {**state, "next_step": "end"}
    
    def _route_after_offline(self, state: GraphState) -> Literal["offline", "continue"]:
        return "offline" if state.get("next_step") == "offline" else "continue"
    
    def _route_after_faq(self, state: GraphState) -> Literal["faq", "continue"]:
        return "faq" if state.get("next_step") == "faq" else "continue"
    
    def _route_after_llm(self, state: GraphState) -> Literal["tools", "end"]:
        return "tools" if state.get("next_step") == "tools" else "end"
    
    def invoke(self, query: str, initial_messages: list = None) -> str:
        """Chạy workflow với query mới"""
        messages = (self._conversation_messages.copy() 
                   if self._conversation_messages 
                   else (initial_messages or []))
        
        # Đảm bảo system prompt luôn có ở đầu messages
        has_system_prompt = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system_prompt:
            messages.insert(0, SystemMessage(content=self._get_system_prompt()))
        
        # Thêm initial context nếu có
        if not messages or len(messages) == 1:  # Chỉ có system prompt
            if self.initial_context:
                for msg in self.initial_context:
                    if msg.get("role") == "user":
                        messages.append(SystemMessage(content=msg["parts"][0]["text"]))
                    elif msg.get("role") == "model":
                        messages.append(AIMessage(content=msg["parts"][0]["text"]))
        
        initial_state = {
            "query": query,
            "messages": messages,
            "reply": None,
            "next_step": None,
            "tool_results": None,
            "error": None,
            "context": {}
        }
        
        try:
            final_state = self.app.invoke(initial_state)
            reply = final_state.get("reply", get_string(stringIds.AI_ERROR_RESPONSE))
            self._conversation_messages = final_state.get("messages", messages)
            return reply
        except Exception as e:
            print(f"Error in graph execution: {e}")
            return get_string(stringIds.AI_ERROR_PROCESSING)
