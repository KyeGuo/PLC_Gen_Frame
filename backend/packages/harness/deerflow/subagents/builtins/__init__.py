"""Built-in subagent configurations."""

from .bash_agent import BASH_AGENT_CONFIG
from .general_purpose import GENERAL_PURPOSE_CONFIG
from .plc_agents import (
    PLC_CODER_CONFIG,
    PLC_DESIGNER_CONFIG,
    PLC_OPTIMIZER_CONFIG,
    PLC_VALIDATOR_CONFIG,
)

__all__ = [
    "GENERAL_PURPOSE_CONFIG",
    "BASH_AGENT_CONFIG",
    "PLC_DESIGNER_CONFIG",
    "PLC_CODER_CONFIG",
    "PLC_VALIDATOR_CONFIG",
    "PLC_OPTIMIZER_CONFIG",
]

# Registry of built-in subagents
BUILTIN_SUBAGENTS = {
    "general-purpose": GENERAL_PURPOSE_CONFIG,
    "bash": BASH_AGENT_CONFIG,
    "plc-designer": PLC_DESIGNER_CONFIG,
    "plc-coder": PLC_CODER_CONFIG,
    "plc-validator": PLC_VALIDATOR_CONFIG,
    "plc-optimizer": PLC_OPTIMIZER_CONFIG,
}