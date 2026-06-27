from typing import Any, Dict, List

RGBColor = tuple[int, int, int]
PortraitImage = list[str]
PortraitPalette = dict[str, RGBColor]


class NPCDefinition:
    """Defines a pluggable NPC with customizable relationship stats and hidden state variables."""

    def __init__(
        self,
        npc_id: str,
        name: str,
        image: PortraitImage,
        pallete: PortraitPalette,
        public_role: str,
        personality: str,
        speech_style: str,
        hidden_motives: str,
        relationship_stats: List[str] = None,
        hidden_state_vars: Dict[str, Any] = None,
        relationship_defaults: Dict[str, int] = None
    ):
        if not isinstance(image, list):
            raise TypeError(
                f"{name} image must be a list[str], but got {type(image).__name__}."
            )

        if not isinstance(pallete, dict):
            raise TypeError(
                f"{name} pallete must be a dict[str, tuple[int, int, int]], "
                f"but got {type(pallete).__name__}. "
                f"You probably used pallete=[SOME_PALETTE] or pallete=SOME_PORTRAIT by mistake."
            )

        self.id = npc_id
        self.name = name
        self.image = image
        self.pallete = pallete
        self.public_role = public_role
        self.personality = personality
        self.speech_style = speech_style
        self.hidden_motives = hidden_motives
        self.relationship_stats = relationship_stats or ["trust", "suspicion", "respect"]
        self.hidden_state_vars = hidden_state_vars or {}
        self.relationship_defaults = relationship_defaults or {
        stat: 50 for stat in self.relationship_stats
        }