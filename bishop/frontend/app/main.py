from fasthtml.common import (
    Form, Input, Button, Titled, RedirectResponse, H1, Redirect
)
from dataclasses import dataclass, asdict
from app.config import BACKEND_URL

from fasthtml.common import (
    Script, Link, fast_app, picolink, Main, cookie, setup_toasts, add_toast, Div, Beforeware, P
)
import requests
import httpx


tlink = Script(src="https://cdn.tailwindcss.com")
dlink = Link(rel="stylesheet",
             href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

hdrs = [tlink, dlink, picolink]


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
    )
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


@rt("/")
def get():
    signout_btn = Button(
        "signout",
        hx_post="/signout"
    )

    return Titled(
        "MAIN PAGE",
        signout_btn
    )
    return Redirect("/signup")
