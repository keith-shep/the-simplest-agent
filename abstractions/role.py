from typing import Final, Literal

RoleName = Literal["user", "assistant"]


class Role:
    USER: Final[RoleName] = "user"
    ASSISTANT: Final[RoleName] = "assistant"
