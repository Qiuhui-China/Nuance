#!/usr/bin/env python3
"""
Nuance AI 对话测试脚本（集成文章润色功能）
直接在控制台体验完整的对话流程并生成润色文章
"""

from conversation import ConversationAgent
from polish import ArticlePolisher
import asyncio


def print_separator():
    print("\n" + "=" * 50 + "\n")


async def test_conversation():
    # 初始化组件
    agent = ConversationAgent()
    polisher = ArticlePolisher()
    session_id = "test_session_1"

    print("=== Nuance AI 对话测试 ===")
    print("输入 'quit' 随时退出测试")
    print("输入 'generate' 可提前结束对话并生成文章")
    print_separator()

    # 1. 开始新会话
    mood = input("请选择用户情绪（例如：happy/sad/angry）：").strip()
    if mood.lower() == 'quit':
        return

    start_result = agent.start_session(session_id, mood)
    print(f"\nAI: {start_result['response']}")
    print(f"[剩余对话轮次: {start_result['turns_left']}]")

    # 2. 对话循环
    while True:
        print_separator()
        user_input = input("用户输入: ").strip()

        if user_input.lower() == 'quit':
            print("测试终止")
            break

        # 处理用户回复
        try:
            reply_result = agent.user_reply(session_id, user_input)
            print(f"\nAI: {reply_result['response']}")

            # 检查会话状态
            if not reply_result['session_active']:
                print(f"\n[对话已结束 - 原因: {reply_result['ended_by']}]")

                # 获取完整对话历史
                history = agent.get_history(session_id)
                print("\n=== 完整对话历史 ===")
                for msg in history:
                    print(f"{msg['role'].upper()}: {msg['content']}")

                # 3. 润色生成文章
                print_separator()
                print("正在生成润色文章...")

                # 提取用户消息（修正过滤条件）
                user_messages = [
                    {"type": msg['role'], "text": msg['content']}
                    for msg in history
                    if msg['role'].lower() == 'user'  # 改为小写比较
                ]

                print(f"\n[DEBUG] 提取到的用户消息数: {len(user_messages)}")
                if not user_messages:
                    print("警告: 未提取到用户消息，使用完整历史记录")
                    user_messages = [
                        {"type": msg['role'], "text": msg['content']}
                        for msg in history
                    ]

                if not user_messages:
                    raise ValueError("无法生成文章：对话历史完全为空")

                polish_result = await polisher.polish(
                    messages=user_messages,
                    mood=mood
                )

                if polish_result["status"] == "success":
                    print_separator()
                    print("=== 润色后的文章 ===")
                    print(polish_result["article"])
                    print(f"\n[字数: {polish_result['word_count']}]")
                else:
                    print(f"文章生成失败: {polish_result['error']}")

                break

            print(f"[剩余对话轮次: {reply_result['turns_left']}]")

        except ValueError as e:
            print(f"错误: {str(e)}")
            break

    # 4. 清理会话
    agent.cleanup_session(session_id)
    print_separator()
    print("测试完成，会话数据已清理")


if __name__ == "__main__":
    asyncio.run(test_conversation())