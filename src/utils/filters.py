def should_respond(message: str) -> bool:
    message = message.lower()
    if ("?" in message or "bob" in message):
        return True
    else:
        return False