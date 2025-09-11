import os
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


class ArticlePolisher:
    def __init__(self):
        self.llm = self._initialize_llm()
        self.chain = self._create_polishing_chain()

    def _initialize_llm(self):
        """初始化大模型连接"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/openai",
                model="openai/gpt-oss-20b",

            )
        except ImportError:
            raise ImportError("请安装 langchain-openai 包")

    def _create_polishing_chain(self):
        """创建文章润色处理链"""
        prompt = ChatPromptTemplate.from_template("""
你是一名专业英语，请将以下对话润色成一篇200字左右的英文文章。

### 原始对话：
{conversation}

### 用户情绪背景：
{mood}

### 要求：
1. 保持第一人称视角
2. 使用生动、自然的英语表达
3. 适当添加过渡句使文章连贯
4. 保留所有关键信息
5. 结尾添加简短的反思段落

请直接输出润色后的文章，不要包含额外说明。
""")
        return prompt | self.llm | StrOutputParser()

    def format_conversation(self, messages: List[Dict]) -> str:
        """
        格式化对话记录
        返回: 格式化后的对话文本
        """
        return "\n".join(
            f"{msg['type'].capitalize()}: {msg['text']}"
            for msg in messages
        )

    async def polish(
            self,
            messages: List[Dict],
            mood: str = "neutral"
    ) -> Dict[str, str]:
        """
        主润色方法（API 调用入口）

        参数:
            messages: 对话记录列表 [{"type": "user/ai", "text": "..."}]
            mood: 用户情绪状态

        返回:
            {
                "status": "success/error",
                "article": "润色后的文章",
                "word_count": int,
                "error": "错误信息（如有）"
            }
        """
        try:
            # 输入验证
            if not messages:
                return {
                    "status": "error",
                    "error": "对话记录不能为空"
                }

            # 格式化对话
            formatted_conv = self.format_conversation(messages)

            # 调用大模型
            article = await self.chain.ainvoke({
                "conversation": formatted_conv,
                "mood": mood
            })

            return {
                "status": "success",
                "article": article.strip(),
                "word_count": len(article.split()),
                "error": None
            }

        except Exception as e:
            return {
                "status": "error",
                "article": None,
                "word_count": 0,
                "error": f"润色失败: {str(e)}"
            }



