from claude_agent_sdk import AssistantMessage, ResultMessage, SystemMessage, UserMessage
from claude_agent_sdk.types import StreamEvent


def stringify_message(
    message: UserMessage
    | AssistantMessage
    | SystemMessage
    | ResultMessage
    | StreamEvent,
):
    if isinstance(message, UserMessage):
        return f"[User] content={message.content}"
    elif isinstance(message, AssistantMessage):
        return f"[Assistant]({message.model}) content={message.content}"
    elif isinstance(message, SystemMessage):
        return f"[System]({message.subtype}) data={message.data}"
    elif isinstance(message, ResultMessage):
        return f"[Result]({message.subtype}) msg={message}"
    elif isinstance(message, StreamEvent):
        return f"[StreamEvent] msg={message}"
