import os
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


class ConversationAgent:
    def __init__(self):
        self.llm = self._initialize_deepseek()
        self.max_turns = 5
        self.sessions: Dict[str, List] = {}
        self.active_sessions: Dict[str, bool] = {}

        self.prompt_template = ChatPromptTemplate.from_template("""
##User Background:
-Current Mood: {mood}
-Conversation History: {conversation_history}
## Your Task:
-Based on the conversation history and the user’s last response, ask the most relevant next question.
Ask in English, one question at a time, and dig deeper into details using the 5W1H principle (Who, What, When, Where, Why, How).
## Conversation Rules:
-Maintain a warm and encouraging tone
-If the user responds in Chinese, continue asking in English
-Do not correct or evaluate the user’s expression
-Proactively end the conversation when sufficient information is gathered
Output only the question (or closing line), with no additional content
-don't give the process of analysis
## Example:
What happened that made you feel {mood}?
## Closing Condition:
If TURNS ARE MORE THAN 3 AND sufficient information is collected, say: "Thank you for sharing! Ready to generate your English article now?"
""")
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def _initialize_deepseek(self):
        """初始化DeepSeek连接"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/openai",
                model="openai/gpt-oss-20b",  # 修正：去除多余空格
                temperature=0.7,
                max_tokens=150,
            )
        except ImportError:
            # 修正：增加异常捕获的详细打印，同时确保导入失败时抛出明确错误
            try:
                from langchain.llms import DeepSeek
                return DeepSeek(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    model="deepseek-chat",
                    temperature=0.7
                )
            except ImportError as e:
                raise ImportError(f"Failed to import LLM libraries: {str(e)}") from e

    def start_session(self, session_id: str, mood: str) -> dict:
        """初始化新对话"""
        if session_id in self.active_sessions:
            return {"error": "Session already exists", "response": "", "turns_left": 0, "session_active": False}

        self.sessions[session_id] = [SystemMessage(content=f"用户情绪：{mood.strip()}")]  # 去除情绪中的空格
        self.active_sessions[session_id] = True

        try:
            mood = self._extract_mood(session_id)
            # 修正：首次对话历史用英文，避免LLM理解偏差
            response = self.chain.invoke({
                "mood": mood,
                "conversation_history": "This is the first conversation, no history yet."
            }).strip()  # 去除首尾空格，避免空内容

            # 兜底：若首次响应为空，用默认问题
            if not response:
                response = f"What happened that made you feel {mood}?"

            self.sessions[session_id].append(AIMessage(content=response))
            return {
                "response": response,
                "turns_left": int(self.max_turns),
                "session_active": True,
                "error": None
            }
        except Exception as e:
            error_msg = str(e)
            return {
                "response": f"Oops, something went wrong. Let's start: What happened that made you feel {mood}?",
                "turns_left": int(self.max_turns),
                "session_active": True,
                "error": error_msg
            }

    def _generate_response(self, session_id: str, user_input: str) -> str:
        """生成基于上下文的AI响应（核心修正：初始化response+修复缩进）"""
        # 1. 修正：先初始化response，避免"未定义"错误
        response = ""
        # 2. 添加用户消息（确保只添加一次）
        self.sessions[session_id].append(HumanMessage(content=user_input.strip()))

        # 3. 准备对话历史和情绪
        conversation_history = self._format_conversation_history(session_id)
        mood = self._extract_mood(session_id)
        max_retries = 1
        retry_count = 0

        # 4. 修复：while循环逻辑（先初始化response，再判断）
        while retry_count <= max_retries and not response:
            try:
                # 调用模型生成响应
                response = self.chain.invoke({
                    "mood": mood,
                    "conversation_history": conversation_history
                }).strip()
                retry_count += 1

                # 日志：重试后仍为空
                if not response and retry_count >= max_retries:
                    print(f"[WARNING] Session {session_id}: LLM returned empty response after {max_retries} retries")

            except Exception as e:
                print(f"[ERROR] Session {session_id}: LLM call failed (retry {retry_count}/{max_retries}): {str(e)}")
                response = ""  # 异常时重置为 empty，触发重试
                retry_count += 1

        # 5. 兜底：若最终仍为空，用情绪匹配的默认问题（确保非空）
        if not response:
            default_questions = {
                "happy": "What made you feel happy recently?",
                "sad": "Would you like to share what made you feel sad?",
                "angry": "What happened that made you feel angry?",
                "excited": "What exciting thing happened to you?",
                "calm": "What made you feel calm lately?"
            }
            response = default_questions.get(mood.lower(), f"Could you share more about your {mood} experience?")

        # 6. 修复：添加AI响应到会话（缩进正确，确保只执行一次）
        self.sessions[session_id].append(AIMessage(content=response))
        return response

    def _format_conversation_history(self, session_id: str) -> str:
        """格式化对话历史（修正：处理用户/AI空输入）"""
        history_text = []
        for msg in self.sessions[session_id]:
            if isinstance(msg, SystemMessage):
                continue
            elif isinstance(msg, HumanMessage):
                content = msg.content.strip() or "The user did not provide content."
                history_text.append(f"User: {content}")
            elif isinstance(msg, AIMessage):
                content = msg.content.strip() or "The AI did not provide a response."
                history_text.append(f"AI Assistant: {content}")

        return "\n".join(history_text) if history_text else "No conversation history available yet."

    def _extract_mood(self, session_id: str) -> str:
        """从会话中提取情绪（修正：增加异常处理，避免格式错误）"""
        try:
            system_msg = self.sessions[session_id][0]
            if not isinstance(system_msg, SystemMessage):
                raise ValueError("First session message is not SystemMessage")

            system_content = system_msg.content.strip()
            # 兼容"用户情绪：XXX"和"User Mood: XXX"格式
            if "：" in system_content:
                return system_content.split("：")[-1].strip()
            elif ":" in system_content:
                return system_content.split(":")[-1].strip()
            else:
                raise ValueError(f"Invalid system message format: {system_content}")
        except (IndexError, ValueError) as e:
            print(f"[WARNING] Session {session_id}: Failed to extract mood ({str(e)}), using 'happy' as default")
            return "happy"  # 兜底：情绪提取失败时用默认值

    def user_reply(self, session_id: str, user_input: str) -> dict:
        """处理用户回复（修正：确保返回非空response）"""
        if not self._validate_session(session_id):
            return {
                "error": "Invalid or inactive session",
                "response": "Invalid session. Please start a new conversation.",
                "session_active": False,
                "turns_left": 0
            }

        # 检查结束条件
        end_check = self._check_end_conditions(session_id, user_input)
        if end_check:
            return end_check

        try:
            response = self._generate_response(session_id, user_input)
            turns_left = self.max_turns - self._count_user_turns(session_id)

            # 检查是否结束对话
            if self._is_ending_response(response):
                self._end_session(session_id)
                return {
                    "response": response,
                    "session_active": False,
                    "ended_by": "ai",
                    "turns_left": 0
                }

            return {
                "response": response,
                "session_active": True,
                "turns_left": turns_left,
                "error": None
            }
        except Exception as e:
            error_msg = str(e)
            mood = self._extract_mood(session_id)
            return {
                "error": error_msg,
                "response": f"Sorry, I had a trouble. Could you tell me more about your {mood} experience?",
                "session_active": True,
                "turns_left": self.max_turns - self._count_user_turns(session_id)
            }

    def _validate_session(self, session_id: str) -> bool:
        return session_id in self.active_sessions and self.active_sessions[session_id]

    def _check_end_conditions(self, session_id: str, user_input: str) -> Optional[dict]:
        """检查结束条件（修正：返回非空response）"""
        if self._is_ending_phrase(user_input):
            self._end_session(session_id)
            return {
                "response": "Thank you for sharing! Ready to generate your English article now?",
                "turns_left": 0,
                "session_active": False,
                "ended_by": "user",
                "error": None
            }

        if self._count_user_turns(session_id) >= self.max_turns:
            self._end_session(session_id)
            return {
                "response": "We've reached the maximum conversation turns. Ready to generate your English article now?",
                "turns_left": 0,
                "session_active": False,
                "ended_by": "max_turns",
                "error": None
            }
        return None

    def _is_ending_phrase(self, text):
        """检查结束短语（修正：处理非字符串输入）"""
        if not isinstance(text, str):
            try:
                text = str(text).lower()
            except Exception:
                return False
        else:
            text = text.lower()
        end_phrases = ["结束", "够了", "generate", "可以了", "stop", "finish", "生成文章"]
        return any(phrase in text for phrase in end_phrases)

    def _is_ending_response(self, response: str) -> bool:
        """检查AI是否触发结束（修正：处理空response）"""
        if not response:
            return False
        lower_response = response.lower()
        return any(phrase in lower_response for phrase in ["generate", "ready to create", "thank you for sharing"])

    def _count_user_turns(self, session_id: str) -> int:
        """计数用户轮次（修正：避免会话为空时报错）"""
        return len([msg for msg in self.sessions.get(session_id, []) if isinstance(msg, HumanMessage)])

    def _end_session(self, session_id: str):
        """结束会话（修正：处理不存在的会话）"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id] = False

    def get_history(self, session_id: str) -> List[Dict]:
        """获取对话历史（修正：返回空列表而非报错）"""
        return [
            {"role": msg.type, "content": msg.content}
            for msg in self.sessions.get(session_id, [])
        ]

    def cleanup_session(self, session_id: str):
        """清理会话（修正：安全删除，避免KeyError）"""
        self.sessions.pop(session_id, None)
        self.active_sessions.pop(session_id, None)