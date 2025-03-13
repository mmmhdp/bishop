from fasthtml.common import (
    Form, Input, Button, Titled, RedirectResponse, H1, Redirect,
    Script, Link, fast_app, picolink, Main, cookie, setup_toasts, add_toast, Div, Beforeware, P
)
from fasthtml.common import *
from dataclasses import dataclass, asdict
from app.config import BACKEND_URL

import requests
import httpx


tlink = Script(src="https://cdn.tailwindcss.com")
dlink = Link(rel="stylesheet",
             href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
custom_link = Link(rel="stylesheet",
                   href="app/assets/styles.css", type="text/css")

hdrs = [tlink, dlink, picolink, custom_link]


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


@dataclass
class LoginInfo:
    username: str
    password: str
    grant_type: str = "password"
    scope: str | None = None
    client_id: str | None = None
    client_secret: str | None = None


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
        hx_get="/signup-redirect"
    )

    return Titled("Login", frm, signup_btn)


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
            add_toast(sess, "login is successful!", "success")
            return Redirect("/")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "error")
            return Redirect("/login")

        else:
            err_text = "INVALID RESPONSE CODE"
            add_toast(sess, err_text, "error")
            return Redirect("/login")


@rt("/signout")
def post(sess):
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
        Input(id="email", placeholder="Email"),
        Input(id="password", type="password", placeholder="Password"),
        Input(id="full_name", placeholder="Full Name"),
        Button("signup"),
        action="/signup", method="post"
    )

    return Titled("Sign Up", frm)


@rt("/signup")
async def post(signup_info: SignUpInfo, sess):
    async with httpx.AsyncClient() as cli:
        func_url = "/users/signup"
        url_to_call = BACKEND_URL + func_url

        print(asdict(signup_info))
        res = await cli.post(url_to_call, json=asdict(signup_info))
        print(res.json())

        if res.status_code == 200:
            add_toast(sess, "signup is successful!", "success")
            return Redirect("/login")

        elif res.status_code == 400:
            print(res.json())
            err_text = res.json()["detail"]
            add_toast(sess, err_text, "error")
            return Redirect("/signup")

        elif res.status_code == 422:
            print(res.json())
            for detail in res.json()["detail"]:
                err_text = detail["msg"]
                add_toast(sess, err_text, "error")
            return Redirect("/signup")

        else:
            err_text = "INVALID RESPONSE CODE"
            add_toast(sess, err_text, "error")

# Mock user data
user_info = {
    "name": "John Doe",
    "email": "john.doe@example.com"
}

# Mock avatars
avatars = [
    {"name": "AI Mentor"},
    {"name": "Chat Companion"},
    {"name": "Virtual Assistant"},
]


@rt("/")
def get():
    signout_btn = Button(
        "signout",
        hx_post="/signout"
    )
    return Titled(
        "User Page",
        Container(
            Card(
                H2("User Information"),
                P(f"Name: {user_info['name']}"),
                P(f"Email: {user_info['email']}"),
            ),
            H2("Avatars"),
            Div(
                *[Div(
                    H3(avatar["name"]),
                    Button(
                        "Train", hx_post=f"/train/{avatar['name']}", cls="secondary"),
                    Button("Chat", hx_get=f"/chat/{avatar['name']}")
                ) for avatar in avatars],
                cls="grid"
            )
        )
    )


@rt("/train/{name}")
def train(name: str):
    return f"Training {name}..."


@rt("/chat/{name}")
def chat(name: str):
    return f"Chatting with {name}..."
