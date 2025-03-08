from fasthtml.common import *


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


@threaded
def get_response(r, idx, messages):
    for chunk in r:
        messages[idx]["content"] += chunk
    messages[idx]["generating"] = False


MESSAGES = []


def include_routes(app):
    @app.get("/chat/chat_message/{msg_idx}")
    def get_chat_message(msg_idx: int):
        if msg_idx >= len(MESSAGES):
            return ""
        return ChatMessage(msg_idx)

    @app.route("/chat")
    def get():
        page = Body(H1('Chatbot Demo'),
                    Div(*[ChatMessage(i) for i in range(len(MESSAGES))],
                        id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                    Form(Group(ChatInput(MESSAGES), Button("Send", cls="btn btn-primary")),
                         hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                         cls="flex space-x-2 mt-2",
                         ), cls="p-4 max-w-lg mx-auto")
        return Title('Chatbot Demo'), page

    @app.post("/chat")
    def post(msg: str):
        idx = len(MESSAGES)
        MESSAGES.append({"role": "user", "content": msg.rstrip()})
        # Send message to chat model (with streaming)
        # r = cli(messages, sp=sp, stream=True)
        r = "response from model"
        MESSAGES.append({"role": "assistant", "generating": True,
                        "content": ""})  # Response initially blank
        # Start a new thread to fill in content
        get_response(r, idx+1, MESSAGES)
        return (ChatMessage(idx, MESSAGES),  # The user's message
                ChatMessage(idx+1, MESSAGES),  # The chatbot's response
                # And clear the input field via an OOB swap
                ChatInput(MESSAGES))
