import os
import json
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# 错误类型字典
ERROR_TYPES = {
    "vocabulary": "词汇错误",
    "grammar": "语法错误",
    "pronunciation": "发音错误",
    "expression": "表达不自然",
    "punctuation": "标点错误",
    "spelling": "拼写错误",
    "word_order": "词序错误",
    "preposition": "介词错误",
    "tense": "时态错误",
    "article": "冠词错误",
    "capitalization": "大小写错误",
    "perfect":"没有错误",
}


class WritingCorrectionAgent:
    def __init__(self):
        self.llm = self._initialize_deepseek()

        # 更正和建议的提示词 - 针对写作场景优化
        self.correction_prompt_template = ChatPromptTemplate.from_template("""
你是一名专业的英语写作教练，正在分析用户的英语表达，帮助提高写作质量。

### 对话上下文：
{conversation_context}

### 你的任务：
请分析用户的所有英语表达（只关注user类型的消息），识别可能的错误或不自然之处，并提供专业的更正建议。

### 输出要求（必须严格遵守）：
请以JSON格式输出，包含一个corrections数组，每个元素包含：
- type: 错误类型（从以下选项中选择：{error_types}）
- original: 原始表达
- suggestion: 建议的正确表达
- explanation: 简要解释（用中文）
如果没有错误，则type为perfect

### 分析准则：
1. 只分析用户的消息（type为user的内容）
2. 重点关注：语法、时态、冠词、介词、表达自然度
3. 对于全大写文本，检查是否应该使用正常大小写
4. 每次最多分析5个主要错误
5. 解释要简洁明了，适合英语学习者
6.不可以输出空数组
请直接输出JSON格式，不要有其他内容。
## 示例输出格式：
{{
  "corrections": [
    {{
      "type": "grammar",
      "original": "I goes to school",
      "suggestion": "I go to school",
      "explanation": "主语I是第一人称，应该使用动词原形go"
    }}
  ]
}}
## 2. 无错误时输出：
{{
  "corrections": [
    {{
      "type": "perfect",
      "original": "I went to the park on Sunday with my friends.",
      "suggestion": "I went to the park on Sunday with my friends.",
      "explanation": "无错误：语法、时态、介词使用均正确，表达自然。"
    }}
  ]
}}

""")
        self.correction_chain = self.correction_prompt_template | self.llm | StrOutputParser()

    def _initialize_deepseek(self):
        """初始化DeepSeek连接"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/openai",
                model="openai/gpt-oss-20b",
                temperature=0.7,

            )
        except ImportError:
            from langchain.llms import DeepSeek
            return DeepSeek(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model="deepseek-chat",
                temperature=0.3
            )

    def analyze_writing(self, conversation_data: List[Dict]) -> dict:
        """
        分析对话中的用户写作并提供更正建议

        参数:
            conversation_data: 对话记录，格式为包含type、text、time的字典列表

        返回:
            包含更正建议的字典
        """
        try:
            # 格式化对话上下文
            conversation_context = self._format_conversation_context(conversation_data)

            # 调用模型进行分析
            response = self.correction_chain.invoke({
                "conversation_context": conversation_context,
                "error_types": ", ".join(ERROR_TYPES.keys())
            })

            # 尝试解析JSON响应
            try:
                result = json.loads(response)

                # 验证结构
                if "corrections" not in result:
                    return {
                        "error": "Invalid response format: missing 'corrections' field",
                        "raw_response": response
                    }

                # 验证每个更正项的结构
                valid_corrections = []
                for correction in result["corrections"]:
                    if all(key in correction for key in ["type", "original", "suggestion", "explanation"]):
                        # 验证错误类型是否在预定义字典中
                        if correction["type"] in ERROR_TYPES:
                            valid_corrections.append(correction)

                return {
                    "corrections": valid_corrections,
                    "total_errors": len(valid_corrections),
                    "conversation_length": len(conversation_data)
                }

            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分或返回错误
                return self._handle_json_parse_error(response)

        except Exception as e:
            return {"error": str(e)}

    def _format_conversation_context(self, conversation_data: List[Dict]) -> str:
        """格式化对话上下文"""
        formatted_lines = []
        for item in conversation_data:
            speaker = "AI助手" if item["type"] == "ai" else "用户"
            formatted_lines.append(f"{speaker}: {item['text']}")
        return "\n".join(formatted_lines)

    def _handle_json_parse_error(self, response: str) -> dict:
        """处理JSON解析错误"""
        # 尝试从响应中提取JSON部分
        try:
            # 查找第一个{和最后一个}
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end + 1]
                result = json.loads(json_str)
                if "corrections" in result:
                    return result
        except:
            pass

        return {
            "error": "Failed to parse model response as JSON",
            "raw_response": response
        }


