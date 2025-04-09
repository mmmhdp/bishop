import base64
from starlette.requests import Request
import starlette.responses as responses
from dataclasses import dataclass, asdict
import asyncio
from fasthtml.common import *
import httpx

from app.config import BACKEND_URL
from app.logging_service import logger

main_css = Link(rel="stylesheet",
                href="app/static/styles.css", type="text/css")
fav = Link(rel="icon", type="image/svg+xml", href="app/static/favicon.ico")
og = Link(rel="icon", type="image/svg+xml", href="app/static/og-image.ico")
hdrs = [main_css, fav, og]


def get_auth_headers(sess):
    jwt_keys = ["token_type", "access_token"]
    for key in jwt_keys:
        if key not in sess:
            return None

    token_type = sess["token_type"]
    token = sess["access_token"]
    headers = {"Authorization": f"{token_type} {token}"}

    return headers


async def jwt_before(req, sess):
    jwt_keys = ["token_type", "access_token"]
    for key in jwt_keys:
        if key not in sess:
            return Redirect("/")

    token_type = sess["token_type"]
    token = sess["access_token"]

    auth_hdrs = {"Authorization": f"{token_type} {token}"}

    async with httpx.AsyncClient(headers=auth_hdrs) as cli:
        func_url = "/login/test-token"
        url_to_call = BACKEND_URL + func_url
        res = await cli.post(url_to_call)

    if res.status_code != 200:
        return Redirect("/")

app, rt = fast_app(
    debug=True,
    hdrs=hdrs,
    live=False,
    before=Beforeware(
        jwt_before,
        skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', r'.*\.js',
              '/login', '/', '/login-redirect', '/signup', '/signup-redirect']
    ),
)

setup_toasts(app, duration=2000)


def main_header():
    return Header(
        Div(
            Span("BishopApp", cls="brand"),
            Nav(
                A("Login", href="/login"),
                A("Signup", href="/signup"),
                cls="nav-links"
            ),
            cls="header-inner"
        ),
        cls="main-header"
    )


def main_footer():
    return Footer(
        Span("© 2025 Bishop Project — All rights reserved."),
        cls="main-footer"
    )


def project_intro():
    return Section(
        H2("What is Bishop?"),
        P("Bishop is a service for interacting with digital avatars of real people."),
        P("An avatar is an intelligent computer model capable of mimicking a specific person’s style of speech, tone, and emotional response."),
        Br(),
        P("Unlike traditional chatbots, Bishop creates the illusion of live conversation by generating both text and audio replies."),
        P("This opens up a wide range of applications: preserving cultural and scientific legacies of public figures, creating educational tools with virtual instructors, and more."),
        Br(),
        P("A key feature of Bishop is its trainable architecture. Avatars can be improved continuously by uploading new materials — such as lectures or interviews — directly through the interface."),
        P("This results in an evolving virtual persona that can converse naturally and reflect the identity of the real person it is modeled after."),
        cls="project-intro"
    )


@rt("/")
def home():
    return Main(
        main_header(),
        Div(
            Titled("Home",
                   P("Welcome to BishopApp."),
                   project_intro()
                   ),
            cls="main-content"
        ),
        main_footer(),
        cls="page-shell"
    )


@dataclass
class LoginInfo:
    username: str
    password: str
    grant_type: str = "password"
    scope: str | None = None
    client_id: str | None = None
    client_secret: str | None = None


@rt("/login-redirect")
def get():
    return Redirect("/login")


@rt("/login")
def get():
    frm = Form(
        Input(id="username", placeholder="Email"),
        Input(id="password", type="password", placeholder="Password"),
        Button("login"),
        action="/login", method="post"
    )

    signup_btn = Button(
        "signup",
        hx_get="/signup-redirect",
        cls="signup-btn"
    )

    content_box = Div(
        Titled("Login", frm),
        signup_btn,
        cls="login-box"
    )

    return Div(
        content_box,
        cls="login-page"
    )


@rt("/login")
async def post(log_info: LoginInfo, sess):
    async with httpx.AsyncClient() as cli:
        func_url = "/login/access-token"
        url_to_call = BACKEND_URL + func_url

        print(asdict(log_info))
        res = await cli.post(url_to_call, data=asdict(log_info))
        print(res.json())

        if res.status_code == 200:
            sess["access_token"] = res.json()["access_token"]
            sess["token_type"] = res.json()["token_type"]

            # Fetch user info
            func_url = "/users/me"
            url_to_call = BACKEND_URL + func_url
            res = await cli.get(url_to_call)
            print(res.json())

            add_toast(sess, "login is successful!", "info")
            return Redirect("/index")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "info")
            return Redirect("/login")

        else:
            err_text = "INVALID RESPONSE CODE"
            add_toast(sess, err_text, "info")
            return Redirect("/login")


@rt("/signout")
def post(sess):
    logger.info("signout triggered")
    jwt_keys = ["token_type", "access_token"]
    for key in jwt_keys:
        if key in sess:
            del sess[key]
    return Redirect("/")


@rt("/signup-redirect")
def get():
    return Redirect("/signup")


@dataclass
class SignUpInfo:
    email: str
    password: str
    full_name: str


@rt("/signup")
async def get():
    frm = Form(
        Input(id="email", name="email", placeholder="Email"),
        Input(id="password", name="password",
              type="password", placeholder="Password"),
        Input(id="full_name", name="full_name", placeholder="Full Name"),
        Button("signup"),
        action="/signup", method="post"
    )

    login_btn = Button(
        "login",
        hx_get="/login-redirect",
        cls="login-btn"
    )

    content_box = Div(
        Titled("Sign Up", frm),
        login_btn,
        cls="signup-box"
    )

    return Div(
        content_box,
        cls="signup-page"
    )


@rt("/signup")
async def post(signup_info: SignUpInfo, sess):
    async with httpx.AsyncClient() as cli:
        func_url = "/users/signup"
        url_to_call = BACKEND_URL + func_url

        print(asdict(signup_info))
        res = await cli.post(url_to_call, json=asdict(signup_info))
        print(res.json())

        if res.status_code == 200:
            add_toast(sess, "signup is successful!", "info")
            return Redirect("/login")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "info")
            return Redirect("/signup")

        elif res.status_code == 422:
            print(res.json())
            for detail in res.json()["detail"]:
                err_text = detail["msg"]
                add_toast(sess, err_text, "info")
            return Redirect("/signup")

        else:
            err_text = "INVALID RESPONSE CODE"
            add_toast(sess, err_text, "info")


async def fetch_user_info(sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.get(f"{BACKEND_URL}/users/me")
        return response.json() if response.status_code == 200 else None


async def fetch_avatars(sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.get(f"{BACKEND_URL}/avatars/")
        return response.json().get("data", []) if "data" in response.json() else []


@rt("/index-redirect")
def get():
    return Redirect("/index")


async def user_info_box(sess):
    signout_btn = Button(
        "Sign Out",
        hx_post="/signout",
    )
    user_info = await fetch_user_info(sess)

    return Grid(
        H2("User Information"),
        P(f"Name: {user_info.get('full_name', 'N/A')}"),
        P(f"Email: {user_info['email']}"),
        signout_btn
    )


@dataclass
class AvatarCreateInfo:
    name: str


@rt("/avatar-create")
async def avatar_create(avatar_info: AvatarCreateInfo, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as cli:
        func_url = "/avatars/"
        url_to_call = BACKEND_URL + func_url

        res = await cli.post(url_to_call, json=asdict(avatar_info))

        if res.status_code == 200:
            add_toast(sess, "Avatar created successfully!", "info")
            return Redirect("/index")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "info")
            return Redirect("/index")

        else:
            err_text = "INVALID RESPONSE CODE"
            print(res.json())
            add_toast(sess, err_text, "info")

    return Redirect("/index")


@rt("/avatar-list")
async def avatars_list_box(sess):
    avatars = await fetch_avatars(sess)

    avatar_list_view = Div(
        *[Button(
            avatar["name"],
            hx_get=f"/avatar/{avatar['id']}",
            hx_target="#avatar-view",
            hx_swap="innerHTML",
        ) for avatar in avatars],
        cls="avatar-list",
    )

    return Div(
        Div(
            Form(
                Input(id="avatar-name", name="name",
                      placeholder="Avatar Name", required=True),
                Button("Create Avatar"),
                action="/avatar-create", method="post",
            ),
        ),
        H2("Avatars"),
        avatar_list_view,
        id="avatar-view"
    )


@rt("/index")
async def get(sess):

    signout_btn = Button(
        "Sign Out",
        hx_post="/signout",
    )

    user_view = await user_info_box(sess)
    avatar_list_view = await avatars_list_box(sess)

    return Titled(
        "User Page",
        user_view,
        avatar_list_view,
    )


@rt("/avatar/{avatar_id}")
async def avatar_view(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as cli:
        func_url = f"/avatars/{avatar_id}"
        url_to_call = BACKEND_URL + func_url
        res = await cli.get(url_to_call)
        avatar = res.json()

    return Div(
        Card(f"Avatar: {avatar["name"]}"),
        Button("Train",
               hx_get=f"/avatar/{avatar["id"]}/train_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("Chat",
               hx_get=f"/avatar/{avatar["id"]}/chat_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),
        Button("Change Name",
               hx_get=f"/avatar/{avatar["id"]}/change_name_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("Delete",
               hx_post=f"/avatar/{avatar["id"]}/delete",
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


@rt("/avatar/{avatar_id}/change_name_widget")
def change_name_widget(avatar_id: str):
    return Form(
        Input(name="name", placeholder="New Name", required=True),
        Button("Save Name"),
        action=f"/avatar/{avatar_id}/change_name", method="post",
        hx_target="#avatar-view", hx_swap="innerHTML"
    )


@rt("/avatar/{avatar_id}/change_name", methods=["POST"])
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


@rt("/avatar/{avatar_id}/delete", methods=["POST"])
async def delete_avatar(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        response = await client.delete(f"{BACKEND_URL}/avatars/{avatar_id}")

    if response.status_code == 200:
        add_toast(sess, "Avatar deleted!", "success")
    else:
        add_toast(sess, "Failed to delete avatar.", "error")

    return Redirect("/index")


@rt("/avatar/{avatar_id}/train_widget")
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
            hx_post=f"/avatar/{avatar_id}/train",
            enctype="multipart/form-data",
            hx_target="#avatar-train",
            hx_swap="innerHTML",
            hx_indicator="#upload-indicator"
        ),
        Div(id="upload-feedback"),
        Div("Uploading...", id="upload-indicator", style="display: none;"),
        Div(
            Button("Start Training",
                   hx_post=f"/avatar/{avatar_id}/train/start",
                   hx_target="#avatar-train",
                   hx_swap="outerHTML"
                   ),
            Button("Stop Training",
                   hx_post=f"/avatar/{avatar_id}/train/stop",
                   hx_target="#avatar-train",
                   hx_swap="outerHTML"
                   ),
            Button("Back",
                   hx_get=f"/avatar/{avatar_id}",
                   hx_target="#avatar-view",
                   hx_swap="innerHTML"
                   ),
            cls="train-actions"
        ),

        id="avatar-train"
    )


@rt("/avatar/{avatar_id}/train", methods=["POST"])
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


@rt("/avatar/{avatar_id}/train/start", methods=["POST"])
async def avatar_train_start(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/start")

    return await avatar_train_widget(avatar_id, sess)


@rt("/avatar/{avatar_id}/train/stop", methods=["POST"])
async def avatar_train_stop(avatar_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        await client.post(f"{BACKEND_URL}/avatars/{avatar_id}/train/stop")

    return await avatar_train_widget(avatar_id, sess)


@rt("/avatar/{avatar_id}/train/status", methods=["POST"])
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
            hx_get=f"/avatar/{avatar_id}/chat/{chat['id']}/messages/",
            hx_target="#chat-view",
            hx_swap="innerHTML",
        ) for chat in chats],
        cls="chat-list",
        id="chat-list"
    )
    return chat_list_view


@rt("/avatar/{avatar_id}/chat_widget")
async def avatar_chat_widget(sess, avatar_id: str):

    chats_list = await chat_list_view(sess, avatar_id)

    return Div(
        Div(
            Form(
                Input(name="title", placeholder="Chat Title", required=True),
                Button("Create Chat"),
                hx_post=f"/avatar/{avatar_id}/chat/create",
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


@rt("/avatar/{avatar_id}/chat/create", methods=["POST"])
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


async def render_message_widget(msg: dict, avatar_id: str, chat_id: str, sess):
    role = "Avatar" if msg["is_generated"] else "User"
    blocks = [P(f"{role}: {msg['text']}")]

    if msg["is_generated"] and msg.get("dub_url"):
        async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
            try:
                audio_res = await client.get(
                    f"{BACKEND_URL}/avatars/{avatar_id}/chat/{
                        chat_id}/msgs/{msg['id']}/response/dub/"
                )
                audio_res.raise_for_status()
                b64 = base64.b64encode(audio_res.content).decode("ascii")
                blocks.append(
                    Audio(
                        controls=True,
                        autoplay=False,
                        preload="auto",
                        src=f"data:audio/mpeg;base64,{b64}"
                    )
                )
            except Exception as e:
                logger.warning(f"Could not load audio for message {
                               msg['id']}: {e}")
                blocks.append(P("Audio unavailable."))

    return Div(*blocks, cls=f"chat-message-{'bot' if msg['is_generated'] else 'user'}")


@rt("/avatar/{avatar_id}/chat/{chat_id}/messages/")
async def chat_messages_view(avatar_id: str, chat_id: str, sess):
    async with httpx.AsyncClient(headers=get_auth_headers(sess)) as client:
        url = f"{BACKEND_URL}/avatars/{avatar_id}/chat/{chat_id}/msgs/"
        res = await client.get(url)
        messages = res.json().get("data", [])[-10:] if res.status_code == 200 else []

    message_box = Div(
        *[
            await render_message_widget(msg, avatar_id, chat_id, sess)
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
                text = msg.get("text", "")

                try:
                    audio_res = await client.get(
                        f"{BACKEND_URL}/avatars/{avatar_id}/chat/{
                            chat_id}/msgs/{rsp_msg_id}/response/dub/"
                    )
                    audio_res.raise_for_status()

                    b64 = base64.b64encode(audio_res.content).decode("ascii")
                    return Div(
                        P(f"Avatar: {text}"),
                        Audio(
                            controls=True,
                            autoplay=False,
                            preload="auto",
                            src=f"data:audio/mpeg;base64,{b64}"
                        ),
                        cls="chat-message-bot"
                    )
                except Exception as e:
                    logger.error(f"Error fetching audio: {e}")
                    return Div(
                        P(f"Avatar: {text}"),
                        P("Audio unavailable."),
                        cls="chat-message-bot"
                    )

    return Div(
        P("Avatar is still thinking..."),
        id=f"poll-rsp-{rsp_msg_id}",
        hx_get=f"/avatar/{avatar_id}/chat/{chat_id}/poll_response/{rsp_msg_id}/",
        hx_trigger="load delay:1000ms",
        hx_swap="outerHTML"
    )
