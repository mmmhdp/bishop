from fasthtml.common import (
    Form, Input, Button, Titled, RedirectResponse, H1, Redirect
)
from dataclasses import dataclass, asdict
from app.config import BACKEND_URL

from fasthtml.common import (
    Script, Link, fast_app, picolink, Main, cookie, setup_toasts, add_toast
)
import requests
import httpx


tlink = Script(src="https://cdn.tailwindcss.com")
dlink = Link(rel="stylesheet",
             href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

hdrs = [tlink, dlink, picolink]

app, rt = fast_app(
    debug=True,
    hdrs=hdrs,
    live=False
)

setup_toasts(app, duration=1500)


async def before(req, sess):
    async with httpx.AsyncClient() as cli:
        func_url = "/login/test-token"
        url_to_call = BACKEND_URL + func_url
        res = await cli.post(url_to_call)

    if res.status_code != 200:
        return Redirect("/login")


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
    return Titled("Login", frm)


@rt("/login")
async def post(log_info: LoginInfo, sess):
    async with httpx.AsyncClient() as cli:
        func_url = "/login/access-token"
        url_to_call = BACKEND_URL + func_url

        print(asdict(log_info))
        res = await cli.post(url_to_call, data=asdict(log_info))
        print(res.json())

        if res.status_code == 200:
            cookie(key="access_token", value=res.json()["access_token"])
            cookie(key="token_type", value=res.json()["token_type"])
            add_toast(sess, "login is successful!", "success")
            return Redirect("/")

        elif res.status_code == 422:
            for detail in res.json()["detail"]:
                err_text = detail["msg"] + " " + detail["loc"][1]
                add_toast(sess, err_text, "error")
            return Redirect("/login")
        else:
            print(res.json())
            for detail in res.json()["detail"]:
                err_text = detail["msg"]
                add_toast(sess, err_text, "error")


@rt("/")
async def get():
    return H1("MAIN PAGE")
