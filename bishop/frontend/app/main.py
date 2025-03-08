from app.routes import (
    welcome, login, sign_up, chat
)

from fasthtml.common import (
    Script, Link, fast_app, picolink
)

tlink = Script(src="https://cdn.tailwindcss.com")
dlink = Link(rel="stylesheet",
             href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

hdrs = [tlink, dlink, picolink]

app, rt = fast_app(
    debug=True,
    hdrs=hdrs,
    live=True
)

welcome.include_routes(app)
login.include_routes(app)
sign_up.include_routes(app)
chat.include_routes(app)
