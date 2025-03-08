from fasthtml.common import (
    Div, H1
)


def SignUpPage():
    return Div(
        H1("Sign Up to Bishop")
    )


def include_routes(app):
    @app.get("/sign-up")
    def signup():
        return SignUpPage()
