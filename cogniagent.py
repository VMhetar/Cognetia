from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Any, Callable
import time
import math
from mcp.server.fastmcp import FastMCP
# =========================================================
# 1. Core Cognitive Data
# =========================================================

@dataclass(frozen=True)
class Situation:
    context: str
    entities: Tuple[str, ...]
    signals: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


@dataclass
class MemoryEdge:
    situation: Situation
    action: str
    outcome: str
    strength: float
    importance: float
    usage_count: int
    last_used: float


# =========================================================
# 2. MCP – HARD BOUNDARY
# =========================================================

class MCPTool:
    def __init__(self, name: str, handler: Callable[..., Any]):
        self.name = name
        self.handler = handler

    def call(self, payload: Dict[str, Any]) -> Any:
        return self.handler(**payload)


class MCP:
    """
    The ONLY gateway to imagination and execution.
    """
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}

    def register_tool(self, tool: MCPTool):
        self._tools[tool.name] = tool

    def invoke(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        if tool_name not in self._tools:
            raise RuntimeError(f"MCP tool '{tool_name}' not registered")
        return self._tools[tool_name].call(payload)


# =========================================================
# 3. Learning + Forgetting
# =========================================================

def forgetting_score(mem: MemoryEdge, now: float) -> float:
    time_decay = math.exp(-(now - mem.last_used) / 3600)
    usage_factor = math.log(1 + mem.usage_count)
    return mem.importance * usage_factor * time_decay


FORGET_THRESHOLD = 0.05


def prune_memory(memory: List[MemoryEdge]) -> List[MemoryEdge]:
    now = time.time()
    return [m for m in memory if forgetting_score(m, now) > FORGET_THRESHOLD]


def hebbian_update(mem: MemoryEdge, reward: float, surprise: float):
    lr = 0.1 + surprise
    mem.strength += lr * reward
    mem.importance = max(mem.importance, abs(reward) + surprise)
    mem.usage_count += 1
    mem.last_used = time.time()


# =========================================================
# 4. Confidence Engine
# =========================================================

def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def estimate_confidence(memories: List[MemoryEdge]) -> float:
    if not memories:
        return 0.1
    weighted = sum(m.strength * m.importance for m in memories)
    return sigmoid(weighted)


CONFIDENCE_THRESHOLD = 0.65
MIN_EXPERIENCE_FOR_CONFIDENCE = 3


# =========================================================
# 5. MCP TOOLS (Imagination + Action)
# =========================================================

def mcp_simulate_world(situation: Situation, action: str):
    """
    Replace with real LLM later.
    """
    return [
        {
            "next_context": situation.context,
            "risk": situation.signals.get("risk", 0.3),
            "benefit": 0.6 if action != "observe" else 0.2,
            "uncertainty": situation.signals.get("uncertainty", 0.3)
        }
    ]


def mcp_execute_action(action: str) -> str:
    return f"outcome_of_{action}"


# =========================================================
# 6. Cognition Helpers
# =========================================================

def encode_situation(input_signal: Dict[str, Any]) -> Situation:
    return Situation(
        context=input_signal["context"],
        entities=tuple(input_signal.get("entities", [])),
        signals=input_signal.get("signals", {})
    )


def propose_actions(
    situation: Situation,
    memories: List[MemoryEdge]
) -> List[str]:
    actions = {m.action for m in memories}
    return list(actions) if actions else ["observe", "ask_clarification"]


def evaluate_simulations(sims: List[Dict[str, float]]) -> float:
    return sum(
        s["benefit"] - s["risk"] - s["uncertainty"]
        for s in sims
    ) / max(len(sims), 1)


def compute_surprise(real_outcome: str, simulated_contexts: List[str]) -> float:
    return 1.0 if real_outcome not in simulated_contexts else 0.2


def find_memory_edge(
    memory: List[MemoryEdge],
    situation: Situation,
    action: str
):
    for m in memory:
        if m.situation.context == situation.context and m.action == action:
            return m
    return None


# =========================================================
# 7. COGNITIVE STEP (CORRECT LOGIC)
# =========================================================

def cognitive_step(
    input_signal: Dict[str, Any],
    memory: List[MemoryEdge],
    mcp: MCP
):
    situation = encode_situation(input_signal)

    relevant = [
        m for m in memory
        if m.situation.context == situation.context
    ]

    candidate_actions = propose_actions(situation, relevant)

    simulations: Dict[str, List[Dict[str, float]]] = {}
    for action in candidate_actions:
        simulations[action] = mcp.invoke(
            "simulate_world",
            {"situation": situation, "action": action}
        )

    scored = []
    for action, sims in simulations.items():
        confidence = estimate_confidence(
            [m for m in relevant if m.action == action]
        )
        score = evaluate_simulations(sims)
        scored.append((action, score, confidence))

    scored.sort(key=lambda x: x[1], reverse=True)
    best_action, _, confidence = scored[0]

    total_experience = sum(m.usage_count for m in relevant)

    if confidence < CONFIDENCE_THRESHOLD:
        if total_experience < MIN_EXPERIENCE_FOR_CONFIDENCE:
            print("🧪 EXPLORATION MODE (low confidence)")
        else:
            print("⛔ NO_ACTION (confidence too low)")
            return "NO_ACTION"

    outcome = mcp.invoke("execute_action", {"action": best_action})

    surprise = compute_surprise(
        outcome,
        [s["next_context"] for s in simulations[best_action]]
    )

    edge = find_memory_edge(memory, situation, best_action)
    if edge is None:
        edge = MemoryEdge(
            situation=situation,
            action=best_action,
            outcome=outcome,
            strength=0.1,
            importance=0.1,
            usage_count=0,
            last_used=time.time()
        )
        memory.append(edge)

    hebbian_update(edge, reward=1.0, surprise=surprise)
    memory[:] = prune_memory(memory)

    print(f"✅ ACTION: {best_action} | CONF: {confidence:.2f}")
    return outcome


# =========================================================
# 8. DEMO
# =========================================================

if __name__ == "__main__":
    memory: List[MemoryEdge] = []

    mcp = MCP()
    mcp.register_tool(MCPTool("simulate_world", mcp_simulate_world))
    mcp.register_tool(MCPTool("execute_action", mcp_execute_action))

    input_signal = {
        "context": "user_security_question",
        "entities": ["api_key", "local_machine"],
        "signals": {
            "risk": 0.9,
            "uncertainty": 0.6,
            "novelty": 0.4
        }
    }

    for i in range(5):
        print(f"\n--- STEP {i + 1} ---")
        cognitive_step(input_signal, memory, mcp)
