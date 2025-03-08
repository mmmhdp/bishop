from fasthtml.common import (
    Div, H1, P, Button
)


def WelcomePage():
    return Div(
        H1("Welcome to Bishop"),
        P("Inspired by the iconic character from the movie Alien, Bishop is your gateway to history."),
        P("Communicate with digital avatars of great minds, past and present."),
        P("Train and personalize avatars with your own data for a truly unique experience."),
        P("Powered by advanced LLMs for intelligent conversation and voice generation."),
        Button("Login", onclick="window.location.href='/login'"),
        Button("Sign Up", onclick="window.location.href='/sign-up'"),
    )


def include_routes(app):
    @app.get("/")
    def welcome():
        return WelcomePage()
