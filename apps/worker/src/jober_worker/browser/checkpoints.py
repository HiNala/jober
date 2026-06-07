from __future__ import annotations

from typing import Literal, cast

from jober_extraction.gates import GateKind

GateCheckpoint = Literal["login", "captcha", "two_factor"]


def gate_checkpoint(gate: GateKind) -> GateCheckpoint:
    return cast(
        GateCheckpoint,
        {
            GateKind.LOGIN: "login",
            GateKind.CAPTCHA: "captcha",
            GateKind.TWO_FACTOR: "two_factor",
        }[gate],
    )
