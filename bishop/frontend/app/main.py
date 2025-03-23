import asyncio
from app.logging import logger
from fasthtml.common import *
from dataclasses import dataclass, asdict
from app.config import BACKEND_URL
from pathlib import Path

import httpx


main_css = Link(rel="stylesheet",
                href="app/static/styles.css", type="text/css")
fav = Link(rel="icon", type="image/svg+xml", href="app/static/favicon.ico")
og = Link(rel="icon", type="image/svg+xml", href="app/static/og-image.ico")
hdrs = [main_css, fav, og]


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
    token_type = sess.get("token_type")
    token = sess.get("access_token")
    if not token_type or not token:
        return None

    headers = {"Authorization": f"{token_type} {token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"{BACKEND_URL}/users/me")
        return response.json() if response.status_code == 200 else None


async def fetch_avatars(sess):
    token_type = sess.get("token_type")
    token = sess.get("access_token")
    if not token_type or not token:
        return []

    headers = {"Authorization": f"{token_type} {token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"{BACKEND_URL}/avatar/")
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

    user_box = await user_info_box(sess),
    avatar_list_view = await avatars_list_box(sess)
    return Titled(
        "User Page",
        user_box,
        avatar_list_view,

    )


@rt("/avatar/{avatar_id}")
def avatar_view(avatar_id: str):
    return Div(
        Card(f"Avatar: {avatar_id}"),
        Button("Train",
               hx_get=f"/avatar/{avatar_id}/train_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("Chat",
               hx_get=f"/avatar/{avatar_id}/chat_widget",
               hx_target="#avatar-view",
               hx_swap="innerHTML"
               ),

        Button("To avatars list",
               hx_get="/avatar-list",
               hx_target="#avatar-view",
               hx_swap="innerHTML",
               ),
        id="avatar-view"
    )


@rt("/avatar/{avatar_id}/train_widget")
def avatar_train_widget(avatar_id: str):
    model_state = {
        "status": "idle",
        "trained_on": 5,
        "last_update": "2025-03-23 14:02"
    }

    return Div(
        Card(
            H3("Training Status"),
            P(f"Model status: {model_state['status']}"),
            P(f"Trained on: {model_state['trained_on']} file(s)"),
            P(f"Last updated: {model_state['last_update']}"),
            cls="training-card"
        ),

        Form(
            Input(type="text", name="item_in", value=avatar_id, readonly=True),
            Input(type="file", name="file", multiple=True),
            Button("Add Files"),
            action="/api/v1/upload/",  # still uses your existing backend
            method="post",
            enctype="multipart/form-data"
        ),

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


# Memory-based chat storage: avatar_id → list of messages
chat_sessions: dict[str, list[dict]] = {}

# Reusable chat message component


def ChatMessage(msg: dict) -> FT:
    role = msg["role"]
    cls = "chat-message-user" if role == "user" else "chat-message-bot"
    return Div(
        P(f"{role.title()}: {msg['content']}"),
        cls=cls
    )

# Route: Render chat widget for a given avatar


@rt("/avatar/{avatar_id}/chat_widget")
def avatar_chat_widget(avatar_id: str):
    print("Chat widget triggered")
    chat_sessions.setdefault(avatar_id, [])  # Ensure chat list exists

    return Div(
        H3(f"Chat with Avatar {avatar_id}"),
        Div(
            *[ChatMessage(m) for m in chat_sessions[avatar_id]],
            id="chat-history",
            cls="chat-history"
        ),
        Form(
            Input(name="message", placeholder="Type your message...", required=True),
            Button("Send", type="submit"),
            hx_post=f"/avatar/{avatar_id}/send_message",
            hx_target="#chat-history",
            hx_swap="beforeend"
        ),
        Button(
            "Back",
            hx_get=f"/avatar/{avatar_id}",
            hx_target="#avatar-view",
            hx_swap="innerHTML"
        ),
        id="avatar-chat"
    )

# Route: Handle sending message and return user + bot responses


@rt("/avatar/{avatar_id}/send_message", methods=["POST"])
async def avatar_chat_send(avatar_id: str, message: str):
    chat_sessions.setdefault(avatar_id, [])
    chat_sessions[avatar_id].append({"role": "user", "content": message})

    # Simulate mock bot response
    await asyncio.sleep(0.5)
    reply = f"MockBot: I received “{message}” and will respond soon!"
    chat_sessions[avatar_id].append({"role": "bot", "content": reply})

    return (
        ChatMessage({"role": "user", "content": message}),
        ChatMessage({"role": "bot", "content": reply})
    )
