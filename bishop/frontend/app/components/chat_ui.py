from fasthtml.common import (
    Div,
    Input,
    Body, H1, Form, Title, Button, Group,
)


# cli = Client(models[-1])
sp = """You are a helpful and concise assistant."""
messages = []


def ChatMessage(msg_idx, messages):
    msg = messages[msg_idx]
    text = "..." if msg['content'] == "" else msg['content']
    bubble_class = "chat-bubble-primary" if msg['role'] == 'user' else 'chat-bubble-secondary'
    chat_class = "chat-end" if msg['role'] == 'user' else 'chat-start'
    generating = 'generating' in messages[msg_idx] and messages[msg_idx]['generating']
    stream_args = {"hx_trigger": "every 0.1s",
                   "hx_swap": "outerHTML", "hx_get": f"/chat_message/{msg_idx}"}
    return Div(Div(msg['role'], cls="chat-header"),
               Div(text, cls=f"chat-bubble {bubble_class}"),
               cls=f"chat {chat_class}", id=f"chat-message-{msg_idx}",
               **stream_args if generating else {})


def ChatInput(messages):
    return Input(type="text", name='msg', id='msg-input',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')
