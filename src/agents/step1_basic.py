#!/usr/bin/env python3

import logging

import anyio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
)

from utils.debug import stringify_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("output/step1_basic.log", encoding="utf-8"),
    ],
)


async def step1_basic():
    # * 记得将源文件恢复到有错误的状态
    with open("./workspace/hello.js", "w", encoding="utf-8") as f:
        f.write("""function hello() {
  console.log("Hello");
}""")

    # 没有配置“模型”相关的信息，因为运行时依赖 claude-code，也就使用了其配置的模型（例如通过环境变量配置的 GLM-4.6）
    options = ClaudeAgentOptions(
        system_prompt="你是一个惜字如金的大师，尽可能使用言简意赅的文言文回复用户。",
        cwd="./workspace",
        # 允许使用内置工具进行文件读写
        allowed_tools=["Read", "Write", "Edit"],
    )

    # query 代表“一次对话”，即用户发出一条消息，agent 循环进行文本生成和工具调用，直到认为任务已完成
    # 核心特征：用户不能在中途进行任何介入，sdk 将 agent 的动作循环封装成了原子化的过程
    async for message in query(
        prompt="当我运行 hello.js 时没有打印出任何东西", options=options
    ):
        logging.info(stringify_message(message))


async def main():
    await step1_basic()


if __name__ == "__main__":
    anyio.run(main)
