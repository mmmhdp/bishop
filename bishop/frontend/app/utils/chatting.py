from fasthtml.common import (
    threaded
)


@threaded
def get_response(r, idx, messages):
    for chunk in r:
        messages[idx]["content"] += chunk
    messages[idx]["generating"] = False
