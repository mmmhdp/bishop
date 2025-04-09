from starlette.requests import Request
from dataclasses import dataclass, asdict
import asyncio
from fasthtml.common import *
import httpx

from app.config import BACKEND_URL
from app.logging_service import logger


avatar_app, rt = fast_app()


@rt("/{avatar_id}")
async def avatar_view(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as cli:
        func_url = f"/avatars/{avatar_id}"
        url_to_call = BACKEND_URL + func_url
        res = await cli.get(url_to_call)
        avatar = res.json()

    return Div(
        Card(f"Avatar: {avatar["name"]}"),
        Button("Train",
               hx_get=f"/{avatar["id"]}/train_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("Chat",
               hx_get=f"/{avatar["id"]}/chat_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),
        Button("Change Name",
               hx_get=f"/{avatar["id"]}/change_name_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("Delete",
               hx_post=f"/{avatar["id"]}/delete",
               hx_target="#avatar-view",
               hx_swap="innerHTML",
               confirm="Are you sure you want to delete this avatar?"
               ),
        Button("To avatars list",
               hx_get="/avatar-list",
               hx_target="#avatar-view",
               hx_swap="innerHTML",
               ),
        id="avatar-view"
    )


@rt("/{avatar_id}/change_name_widget")
def change_name_widget(avatar_id: str):
    return Form(
        Input(name="name", placeholder="New Name", required=True),
        Button("Save Name"),
        action=f"/{avatar_id}/change_name", method="post",
        hx_target="#avatar-view", hx_swap="innerHTML"
    )


@rt("/{avatar_id}/change_name", methods=["POST"])
async def change_name(avatar_id: str, name: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.put(
            f"{BACKEND_URL}/avatars/{avatar_id}",
            json={"name": name}
        )
    if response.status_code == 200:
        add_toast(sess, "Avatar renamed successfully!", "success")
    else:
        add_toast(sess, "Failed to rename avatar.", "error")

    return Redirect(f"/index")


@rt("/{avatar_id}/delete", methods=["POST"])
async def delete_avatar(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.delete(f"{BACKEND_URL}/avatars/{avatar_id}")

    if response.status_code == 200:
        add_toast(sess, "Avatar deleted!", "success")
    else:
        add_toast(sess, "Failed to delete avatar.", "error")

    return Redirect("/index")


@rt("/{avatar_id}/train_widget")
async def avatar_train_widget(avatar_id: str, sess):
    # async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
    #    try:
    #        res = await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/status")
    #        model_state = res.json()
    #    except Exception:
    #        model_state = {
    #            "status": "unknown",
    #            "trained_on": "n/a",
    #            "last_update": "n/a"
    #        }
    model_state = {
        "status": "unknown",
        "trained_on": "n/a",
        "last_update": "n/a"
    }

    return Div(
        # Div(
        #    Card(
        #        H3("Training Status"),
        #        P(f"Model status: {model_state['status']}"),
        #        P(f"Trained on: {model_state['trained_on']} file(s)"),
        #        P(f"Last updated: {model_state['last_update']}"),
        #        cls="training-card"
        #    ),
        #    id="train-status",
        #    hx_post=f"/avatar/{avatar_id}/train_widget",
        #    hx_swap="outerHTML"
        # ),

        Form(
            Input(type="text", name="type", value="default"),
            Input(type="file", name="files", multiple=True),
            Button("Upload File"),
            hx_post=f"/{avatar_id}/train",
            enctype="multipart/form-data",
            hx_target="#avatar-train",
            hx_swap="innerHTML",
            hx_indicator="#upload-indicator"
        ),
        Div(id="upload-feedback"),
        Div("Uploading...", id="upload-indicator", style="display: none;"),
        Div(
            Button("Start Training",
                   hx_post=f"/{avatar_id}/train/start",
                   hx_target="#avatar-train",
                   hx_swap="outerHTML"
                   ),
            Button("Stop Training",
                   hx_post=f"/{avatar_id}/train/stop",
                   hx_target="#avatar-train",
                   hx_swap="outerHTML"
                   ),
            Button("Back",
                   hx_get=f"/{avatar_id}",
                   hx_target="#avatar-view",
                   hx_swap="innerHTML"
                   ),
            cls="train-actions"
        ),

        id="avatar-train"
    )


@rt("/avatar_id}/train", methods=["POST"])
async def proxy_upload(avatar_id: str, request: Request, sess):
    form = await request.form()
    uploaded_files = form.getlist("files")
    type_value = form.get("type")

    file_data = []
    for file in uploaded_files:
        content = await file.read()
        file_data.append(("file", (file.filename, content, file.content_type)))

    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        res = await client.post(
            f"{BACKEND_URL}/avatars/{avatar_id}/train/",
            data={"type": type_value},
            files=file_data
        )

    if res.status_code == 200:
        add_toast(sess, "File uploaded successfully!", "info")
    else:
        add_toast(sess, "File uploadind failed!", "info")

    return await avatar_train_widget(avatar_id, sess)


@rt("/{avatar_id}/train/start", methods=["POST"])
async def avatar_train_start(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/start")

    return await avatar_train_widget(avatar_id, sess)


@rt("/{avatar_id}/train/stop", methods=["POST"])
async def avatar_train_stop(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/stop")

    return await avatar_train_widget(avatar_id, sess)


@rt("/{avatar_id}/train/status", methods=["POST"])
async def avatar_train_status(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        res = await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/status")
        model_state = res.json()

    return Div(
        P(f"Status: {model_state['status']}"),
        P(f"Files trained: {model_state['trained_on']}"),
        P(f"Last updated: {model_state['last_update']}")
    )


@dataclass
class ChatCreateInfo:
    title: str


async def chat_list_view(sess, avatar_id: str):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.get(f"{BACKEND_URL}/avatars/{avatar_id}/chat/")
        chats = response.json() if response.status_code == 200 else []

    chat_list_view = Div(
        *[Button(
            f"Chat {chat['title']}",
            hx_get=f"/{avatar_id}/chat/{chat['id']}/messages/",
            hx_target="#chat-view",
            hx_swap="innerHTML",
        ) for chat in chats],
        cls="chat-list",
        id="chat-list"
    )
    return chat_list_view


@rt("/{avatar_id}/chat_widget")
async def avatar_chat_widget(sess, avatar_id: str):

    chats_list = await chat_list_view(sess, avatar_id)

    return Div(
        Div(
            Form(
                Input(name="title", placeholder="Chat Title", required=True),
                Button("Create Chat"),
                hx_post=f"/{avatar_id}/chat/create",
                hx_target="#chat-list",
                hx_swap="innerHTML"
            ),
            cls="crud-section",
            id="chat-create-section"
        ),
        H2("Chats"),
        chats_list,
        Button(
            "Back",
            hx_get=f"/avatar/{avatar_id}",
            hx_target="#avatar-view",
            hx_swap="innerHTML"
        ),
        id="chat-view"
    )


@rt("/{avatar_id}/chat/create", methods=["POST"])
async def chat_create(avatar_id: str, chat_create_info: ChatCreateInfo, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as cli:
        func_url = f"/avatars/{avatar_id}/chat/"
        url_to_call = BACKEND_URL + func_url

        res = await cli.post(url_to_call, json=asdict(chat_create_info))

        if res.status_code == 200:
            add_toast(sess, "Chat created successfully!", "info")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "info")

        else:
            err_text = "INVALID RESPONSE CODE"
            add_toast(sess, err_text, "info")

    print(res.json())
    chats_list = await chat_list_view(sess, avatar_id)
    return chats_list


@rt("/avatar/{avatar_id}/chat/{chat_id}/messages/")
async def chat_messages_view(avatar_id: str, chat_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        url = f"{BACKEND_URL}/avatars/{avatar_id}/chat/{chat_id}/msgs/"
        res = await client.get(url)
        print(res.json())
        messages = res.json().get("data", [])[-10:] if res.status_code == 200 else []

    message_box = Div(
        *[
            Div(
                P(f"Avatar : {msg['text']}"),
            )
            for msg in messages
        ],
        id="chat-history",
        cls="chat-history"
    )

    return Div(
        message_box,
        Form(
            Input(name="text", placeholder="Type your message...", required=True),
            Button("Send"),
            hx_post=f"/avatar/{avatar_id}/chat/{chat_id}/send_message",
            hx_target="#chat-history",
            hx_swap="beforeend"
        ),
        Button(
            "Back to Chats",
            hx_get=f"/avatar/{avatar_id}/chat_widget",
            hx_target="#avatar-view",
            hx_swap="innerHTML"
        ),
    )


@rt("/avatar/{avatar_id}/chat/{chat_id}/send_message", methods=["POST"])
async def send_message(avatar_id: str, chat_id: str, text: str, sess):
    payload = {
        "text": text,
        "is_generated": False,
        "dub_url": ""
    }

    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        url = f"{BACKEND_URL}/avatars/{avatar_id}/chat/{chat_id}/msgs/"
        res = await client.post(url, json=payload)

        if res.status_code == 200:
            message = res.json()

            user_block = Div(
                P(f"You: {text}"),
                cls="chat-message-user"
            )

            waiting_block = Div(
                P("Avatar is typing..."),
                id=f"poll-rsp-{message['id']}",
                hx_get=f"/avatar/{avatar_id}/chat/{
                    chat_id}/poll_response/{message['id']}/",
                hx_trigger="load delay:500ms",
                hx_swap="outerHTML"
            )

            return (user_block, waiting_block)

    return Div(P("Failed to send message."), cls="chat-message-error")


@rt("/avatar/{avatar_id}/chat/{chat_id}/poll_response/{rsp_msg_id}/")
async def poll_response(avatar_id: str, chat_id: str, rsp_msg_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        for _ in range(5):
            await asyncio.sleep(0.5)
            url = f"{
                BACKEND_URL}/avatars/{avatar_id}/chat/{chat_id}/msgs/{rsp_msg_id}/response/"
            res = await client.get(url)

            if res.status_code == 200:
                msg = res.json()
                dub_url = msg.get['dub_url']

                return Div(
                    P(f"Avatar: {msg['text']}"),
                    Audio(controls=True, src=msg['dub_url']),
                    cls="chat-message-bot"
                )

    return Div(
        P("Avatar is still thinking..."),
        id=f"poll-rsp-{rsp_msg_id}",
        hx_get=f"/avatar/{avatar_id}/chat/{chat_id}/poll_response/{rsp_msg_id}/",
        hx_trigger="load delay:1000ms",
        hx_swap="outerHTML"
    )
