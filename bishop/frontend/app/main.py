from app.logging import logger
from fasthtml.common import *
from dataclasses import dataclass, asdict
from app.config import BACKEND_URL
from pathlib import Path

import httpx


main_css = Link(rel="stylesheet",
                href="app/static/styles.css", type="text/css")
hdrs = [
    main_css,
]


async def jwt_before(req, sess):
    jwt_keys = ["token_type", "access_token"]
    for key in jwt_keys:
        if key not in sess:
            return Redirect("/login")

    token_type = sess["token_type"]
    token = sess["access_token"]

    auth_hdrs = {"Authorization": f"{token_type} {token}"}

    async with httpx.AsyncClient(headers=auth_hdrs) as cli:
        func_url = "/login/test-token"
        url_to_call = BACKEND_URL + func_url
        res = await cli.post(url_to_call)

    if res.status_code != 200:
        return Redirect("/login")

app, rt = fast_app(
    debug=True,
    hdrs=hdrs,
    live=False,
    before=Beforeware(
        jwt_before,
        skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', r'.*\.js',
              '/login', '/signup', '/signup-redirect']
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
    return Redirect("/login")


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


upload_dir = Path("filez")
upload_dir.mkdir(exist_ok=True)


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


@rt("/adsasd")
async def get(sess):
    return Main(
        H1("MAIN PAGE NAH")
    )


@rt("/index")
async def get(sess):

    user_info = await fetch_user_info(sess)
    avatars = await fetch_avatars(sess)

    if not user_info:
        return Redirect("/login")

    signout_btn = Button(
        "Sign Out",
        hx_post="/signout",
    )

    avatar_list_view = Div(
        *[Button(
            avatar["name"],
            hx_get=f"/avatar/{avatar['id']}",
            hx_target="#avatar-actions",
            hx_swap="innerHTML",
            cls="avatar-button",
            style="display: block; padding: 10px; background-color: #444; color: white; width: 100%;"
        ) for avatar in avatars],
        cls="avatar-list",
        style="display: flex; flex-direction: column; gap: 10px; width: 50%;"
    )

    avatar_actions_view = Div(
        H2("Select an avatar to interact with"),
        id="avatar-actions",
        style="width: 50%; padding: 10px; border-left: 1px solid white;"
    )

    return Titled(
        "User Page",
        Container(
            Card(
                H2("User Information"),
                P(f"Name: {user_info.get('full_name', 'N/A')}"),
                P(f"Email: {user_info['email']}"),
                signout_btn
            ),
            H2("Avatars"),
            Div(
                avatar_list_view,
                avatar_actions_view,
                style="display: flex; gap: 20px; width: 100%;"
            )
        )
    )


@rt("/avatar/{avatar_id}")
def avatar_view(avatar_id: str):
    return Div(
        H2(f"Avatar: {avatar_id}"),
        Button("Train",
               hx_get=f"/avatar/{avatar_id}/train_widget",
               hx_target="#avatar-actions",
               hx_swap="innerHTML"),
        Button("Chat",
               hx_get=f"/avatar/{avatar_id}/chat_widget",
               hx_target="#avatar-actions",
               hx_swap="innerHTML"),
    )


@rt("/avatar/{avatar_id}/train_widget")
def train_widget(avatar_id: str):
    return Div(
        H2(f"Training Avatar: {avatar_id}"),
        Form(
            Input(type="file", name="file"),
            Button("Upload Training Data", type="submit", cls="secondary"),
            action=f"/avatar/{avatar_id}/upload",
            method="post",
            enctype="multipart/form-data",
        ),
        Button("Start Training",
               hx_post=f"{BACKEND_URL}/avatar/{avatar_id}/start_train",
               hx_target="#train-status",
               hx_swap="innerHTML"),
        Button("Stop Training",
               hx_post=f"{BACKEND_URL}/avatar/{avatar_id}/stop_train",
               hx_target="#train-status",
               hx_swap="innerHTML"),
        Button("Back",
               hx_get=f"/avatar/{avatar_id}",
               hx_target="#avatar-actions",
               hx_swap="innerHTML"),
        Div(id="train-status")
    )


@rt("/avatar/{avatar_id}/send_message")
def send_mock_message(avatar_id: str, user_message: str):
    mock_responses = {
        "hello": "Hello! How can I assist you today?",
        "how are you": "I'm just a bot, but I'm here to help!",
        "bye": "Goodbye! Have a great day!",
        "default": "I'm not sure how to respond to that, but I'm learning!"
    }
    bot_reply = mock_responses.get(
        user_message.lower(), mock_responses["default"])
    return Div(
        P(f"You: {user_message}", cls="chat chat-end chat-bubble-primary"),
        P(f"Avatar: {bot_reply}", cls="chat chat-start chat-bubble-secondary"),
        id="chat-box",
        style="height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;"
    )


@rt("/avatar/{avatar_id}/chat_widget")
def chat_widget(avatar_id: str):
    return Div(
        H2(f"Chat with Avatar: {avatar_id}"),
        Div(id="chat-box", cls="chat-box h-[73vh] overflow-y-auto border p-2"),
        Form(
            Input(name="user_message", placeholder="Type a message",
                  cls="input input-bordered w-full"),
            Button("Send", cls="btn btn-primary", type="submit"),
            action=f"/avatar/{avatar_id}/send_message",
            method="post",
            hx_target="#chat-box",
            hx_swap="beforeend"
        ),
        Button("Back",
               hx_get=f"/avatar/{avatar_id}",
               hx_target="#avatar-actions",
               hx_swap="innerHTML")
    )
