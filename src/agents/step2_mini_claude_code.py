import logging
from typing import Any

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from utils.debug import stringify_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("output/step2_mini_claude_code.log", encoding="utf-8"),
    ],
)


async def step2_mini_claude_code():
    # * 记得将源文件恢复到有错误的状态
    with open("./workspace/hello.js", "w", encoding="utf-8") as f:
        f.write("""function hello() {
  console.log("Hello");
}""")

    # mini_claude_code 内部状态
    end = False
    tool_to_allow: str | None = None
    call_id_tool_map = {}
    allowed_tool_set = set()

    # 使用 Hook 机制动态控制工具使用
    async def preprocess_tool_use(input_data, tool_use_id, context):
        # 已被用户允许的工具直接返回 permissionDecision=allow 允许使用
        if input_data["tool_name"] in allowed_tool_set:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "user allowed",
                }
            }
        else:
            return {}

    options = ClaudeAgentOptions(
        # 直接使用内置的 claude code 系统提示词
        system_prompt={"type": "preset", "preset": "claude_code"},
        cwd="./workspace",
        allowed_tools=["Read", "Write"],
        hooks={"PreToolUse": [HookMatcher(hooks=[preprocess_tool_use])]},  # type: ignore
    )

    async with ClaudeSDKClient(options=options) as client:
        while not end:
            user_input = input("请输入（exit-退出；allow-授权）：")

            if user_input == "exit":
                end = True
                continue
            if user_input == "allow" and tool_to_allow is not None:
                allowed_tool_set.add(tool_to_allow)
                logging.info(f"已授权使用工具 [{tool_to_allow}]")
                tool_to_allow = None
                user_input = "已授权，请继续"

            await client.query(prompt=user_input)
            async for message in client.receive_response():
                logging.info(stringify_message(message))

                # 记录所有 call_id -> tool 的映射
                if isinstance(message, AssistantMessage) and isinstance(
                    message.content[0], ToolUseBlock
                ):
                    call_id_tool_map[message.content[0].id] = message.content[0].name

                # 当发现 agent 试图调用工具但失败时，提示用户允许使用此工具
                if (
                    isinstance(message, UserMessage)
                    and isinstance(message.content[0], ToolResultBlock)
                    and message.content[0].is_error
                ):
                    tool_name = call_id_tool_map.get(message.content[0].tool_use_id)

                    if tool_name is not None:
                        tool_to_allow = tool_name
                        logging.info(
                            f"调用工具 [{tool_to_allow}] 失败，请输入 allow 以授权使用此工具~"
                        )
                        await client.interrupt()


async def main():
    await step2_mini_claude_code()


if __name__ == "__main__":
    anyio.run(main)
