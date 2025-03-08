from fasthtml.common import (
    Div, H1, Titled, Form, Input, Label, Button
)


def LoginPage():
    return Titled(
        "Login Form",
        Form(
            Label("Name", Input(name="name")),
            Label("Email", Input(name="email", type="email")),
            Label("Age", Input(name="age", type="number")),
            Button("Submit", type="submit"),
            action="/submit",
            method="post"
        )
    )


def include_routes(app):

    @app.get("/login")
    def login():
        return LoginPage()
