from typing import Any, Dict, List


class NPCDefinition:
    """Defines a pluggable NPC with customizable relationship stats and hidden state variables."""
    
    def __init__(
        self,
        npc_id: str,
        name: str,
        public_role: str,
        personality: str,
        speech_style: str,
        hidden_motives: str,
        relationship_stats: List[str] = None,
        hidden_state_vars: Dict[str, Any] = None,
        relationship_defaults: Dict[str, int] = None
    ):
        self.id = npc_id
        self.name = name
        self.public_role = public_role
        self.personality = personality
        self.speech_style = speech_style
        self.hidden_motives = hidden_motives
        self.relationship_stats = relationship_stats or ["trust", "suspicion", "respect"]
        self.hidden_state_vars = hidden_state_vars or {}
        self.relationship_defaults = relationship_defaults or {stat: 50 for stat in self.relationship_stats}
