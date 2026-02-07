from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Any
import time
import math

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
    situation: Situation          # post-action situation
    action: str
    outcome: str
    strength: float
    importance: float
    usage_count: int
    last_used: float
    fatigue: float = 0.0
    completed: bool = False


# =========================================================
# 2. Learning + Forgetting
# =========================================================

FORGET_THRESHOLD = 0.05
CONFIDENCE_THRESHOLD = 0.65
MIN_EXPERIENCE_FOR_CONFIDENCE = 3


def forgetting_score(mem: MemoryEdge, now: float) -> float:
    return (
        mem.importance
        * math.log(1 + mem.usage_count)
        * math.exp(-(now - mem.last_used) / 3600)
    )


def prune_memory(memory: List[MemoryEdge]) -> List[MemoryEdge]:
    now = time.time()
    return [m for m in memory if forgetting_score(m, now) > FORGET_THRESHOLD]


def hebbian_update(mem: MemoryEdge, reward: float, surprise: float):
    mem.strength += (0.1 + surprise) * reward
    mem.importance = max(mem.importance, abs(reward) + surprise)
    mem.usage_count += 1
    mem.fatigue += 0.2
    mem.last_used = time.time()


def estimate_confidence(memories: List[MemoryEdge]) -> float:
    if not memories:
        return 0.1
    x = sum(m.strength * m.importance for m in memories)
    return 1 / (1 + math.exp(-x))


# =========================================================
# 3. World Simulation + Execution
# =========================================================

def simulate_world(situation: Situation, action: str):
    return [{
        "next_context": situation.context,
        "risk": situation.signals.get("risk", 0.3),
        "benefit": 0.6 if action != "observe" else 0.2,
        "uncertainty": situation.signals.get("uncertainty", 0.3)
    }]


def execute_action(action: str) -> str:
    return f"outcome_of_{action}"


# =========================================================
# 4. Situation Encoding & Update
# =========================================================

def encode_situation(input_signal: Dict[str, Any]) -> Situation:
    return Situation(
        context=input_signal["context"],
        entities=tuple(input_signal.get("entities", [])),
        signals=dict(input_signal.get("signals", {}))
    )


def update_situation(situation: Situation, action: str) -> Situation:
    signals = dict(situation.signals)

    if action == "ask_clarification":
        signals["uncertainty"] = max(0.0, signals.get("uncertainty", 1.0) - 0.3)
        signals["novelty"] = max(0.0, signals.get("novelty", 1.0) - 0.2)

    return Situation(
        context=situation.context,
        entities=situation.entities,
        signals=signals
    )


# =========================================================
# 5. Cognition Helpers
# =========================================================

def propose_actions(situation: Situation, memories: List[MemoryEdge]) -> List[str]:
    actions = {m.action for m in memories if not m.completed}
    return list(actions) if actions else ["observe", "ask_clarification"]


def evaluate_simulations(sims: List[Dict[str, float]]) -> float:
    return sum(
        s["benefit"] - s["risk"] - s["uncertainty"]
        for s in sims
    ) / max(len(sims), 1)


def compute_surprise(real_outcome: str, simulated_contexts: List[str]) -> float:
    return 1.0 if real_outcome not in simulated_contexts else 0.2


def detect_completion(edge: MemoryEdge, situation: Situation):
    low_uncertainty = situation.signals.get("uncertainty", 1.0) <= 0.3
    high_fatigue = edge.fatigue > 0.6
    repeated = edge.usage_count >= 3

    if low_uncertainty and high_fatigue and repeated:
        edge.completed = True


def find_memory_edge(memory: List[MemoryEdge], context: str, action: str):
    for m in memory:
        if m.situation.context == context and m.action == action:
            return m
    return None


# =========================================================
# 6. COGNITIVE STEP (FINAL)
# =========================================================

def cognitive_step(situation: Situation, memory: List[MemoryEdge]):

    relevant = [m for m in memory if m.situation.context == situation.context]
    actions = propose_actions(situation, relevant)

    scored = []
    simulations = {}

    for action in actions:
        sims = simulate_world(situation, action)
        simulations[action] = sims

        conf = estimate_confidence([m for m in relevant if m.action == action])
        score = evaluate_simulations(sims) - sum(
            m.fatigue for m in relevant if m.action == action
        )
        scored.append((action, score, conf))

    scored.sort(key=lambda x: x[1], reverse=True)
    best_action, _, confidence = scored[0]

    total_exp = sum(m.usage_count for m in relevant)

    if confidence < CONFIDENCE_THRESHOLD:
        if total_exp < MIN_EXPERIENCE_FOR_CONFIDENCE:
            print("🧪 EXPLORATION MODE (low confidence)")
        else:
            print("⛔ NO_ACTION (confidence too low)")
            return "NO_ACTION", situation

    outcome = execute_action(best_action)
    new_situation = update_situation(situation, best_action)

    edge = find_memory_edge(memory, situation.context, best_action)
    if edge is None:
        edge = MemoryEdge(
            situation=new_situation,
            action=best_action,
            outcome=outcome,
            strength=0.1,
            importance=0.1,
            usage_count=0,
            last_used=time.time()
        )
        memory.append(edge)
    else:
        edge.situation = new_situation

    surprise = compute_surprise(
        outcome,
        [s["next_context"] for s in simulations[best_action]]
    )

    hebbian_update(edge, reward=1.0, surprise=surprise)
    detect_completion(edge, new_situation)

    memory[:] = prune_memory(memory)

    print(f"✅ ACTION: {best_action} | CONF: {confidence:.2f}")
    print(
        f"   ↳ uncertainty={new_situation.signals.get('uncertainty'):.2f}, "
        f"fatigue={edge.fatigue:.2f}, completed={edge.completed}"
    )

    return outcome, new_situation


# =========================================================
# 7. DEMO
# =========================================================

if __name__ == "__main__":
    memory: List[MemoryEdge] = []

    input_signal = {
        "context": "user_security_question",
        "entities": ["api_key", "local_machine"],
        "signals": {
            "risk": 0.9,
            "uncertainty": 0.6,
            "novelty": 0.4
        }
    }

    situation = encode_situation(input_signal)

    for i in range(6):
        print(f"\n--- STEP {i + 1} ---")
        _, situation = cognitive_step(situation, memory)
