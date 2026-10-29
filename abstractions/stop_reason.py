from typing import Final, Literal

StopReasonName = Literal["end_turn", "tool_use"]


class StopReason:
    END_TURN: Final[StopReasonName] = "end_turn"
    TOOL_USE: Final[StopReasonName] = "tool_use"
