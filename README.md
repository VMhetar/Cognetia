🧠 Cognetia — A Cognitive AI Agent (Experimental)

Cognetia is an experimental cognitive AI agent that focuses on how an agent decides to act, not just what it outputs.

Unlike typical LLM-based agents, Cognetia explicitly models:

belief formation

uncertainty and confidence

exploratory behavior

internal world simulation

learning from real outcomes

forgetting unused knowledge

habit formation and habit breaking

This project is an exploration of cognition-first AI, not chatbots or workflow automation.

✨ Core Idea

Most modern “AI agents”:

always respond

always act

hallucinate confidence

rely entirely on LLMs

store memory as text embeddings

Cognetia does the opposite.

If the agent is unsure, it can choose to do nothing.
If it lacks experience, it explores cautiously.
If a behavior repeats too much, it becomes fatigued.

This creates behavior that is less flashy, but far more epistemically honest.

🧩 Architecture Overview

Cognetia is built around a strict separation of concerns:

Perception
   ↓
Situation Encoding
   ↓
Memory Retrieval (Hebbian)
   ↓
World Simulation (LLM via MCP)
   ↓
Confidence & Risk Evaluation
   ↓
Action / No-Action
   ↓
Learning + Forgetting

Key principle:

LLMs are used for imagination, not cognition.

🧠 Core Components
1. Situation Representation

A Situation is a structured snapshot of context:

Situation(
  context="user_security_question",
  entities=("api_key", "local_machine"),
  signals={
    "risk": 0.9,
    "uncertainty": 0.6,
    "novelty": 0.4
  }
)


If two situations feel similar to a human, they should look similar here.

2. Hebbian Memory (Associative Learning)

Memory is stored as associations, not facts:

(Situation) ↔ (Action) ↔ (Outcome)


Learning rule:

repeated success strengthens associations

surprising outcomes increase learning rate

unused memories decay over time

No backpropagation.
No offline training.
Only experience.

3. Confidence Engine

Confidence is computed from past outcomes, not model logits.

No experience → low confidence

Repeated success → higher confidence

Confidence gates action execution

If confidence is below a threshold:

the agent may explore

or may choose NO_ACTION

Silence is allowed.

4. Exploration Bootstrapping

When the agent has little or no experience:

confidence is low

exploration mode is enabled

safe, low-risk actions are preferred

This allows learning without reckless behavior.

5. Internal World Simulation (LLM)

Before acting, the agent simulates possible futures using an LLM.

The LLM:

generates possible outcomes

does not decide what to do

does not update memory

This mirrors human “mental simulation”.

6. MCP (Model Context Protocol)

All imagination and execution is accessed only through MCP tools.

This enforces:

permission boundaries

no direct LLM access from cognition

no uncontrolled side effects

Cognetia can run with:

a local MCP abstraction (research mode)

or FastMCP (server-based tools)

7. Forgetting Mechanism

Memory decays based on:

time since last use

usage frequency

importance of the outcome

Unused, low-impact knowledge disappears naturally.

This prevents:

memory bloat

stale beliefs

overfitting to old situations

8. Action Fatigue (Habit Breaking)

Repeated actions accumulate fatigue.

Even if an action is successful:

repeating it too often reduces its score

the agent eventually tries alternatives

infinite loops are avoided

This models:

boredom

diminishing returns

habit breaking

🧪 Example Behavior
STEP 1 → exploration → ask_clarification (low confidence)
STEP 2 → ask_clarification (confidence rises)
STEP 3 → ask_clarification (fatigue increases)
STEP 4 → observe
STEP 5 → NO_ACTION


This is intentional behavior, not randomness.

🚫 What Cognetia Is NOT

❌ Not a chatbot

❌ Not an agent framework

❌ Not an RL benchmark

❌ Not prompt engineering

❌ Not designed for production (yet)

This is a research system.

🛠 How to Run
python cogniagent.py


No external services required (LLM is stubbed).

🧭 Current Status

✅ End-to-end cognitive loop

✅ Confidence-gated action

✅ Exploration vs hesitation

✅ Internal simulation

✅ Forgetting + fatigue

⚠️ Single-step reasoning only

⚠️ No long-term goals yet

🔮 Planned Extensions

Dream / sleep consolidation

Situation similarity graph

Risk-aware exploration bias

Multi-step world simulation

Embodied environments (robotics / simulations)

🧠 Philosophy

Cognetia follows a simple belief:

Intelligence is not about always having an answer.
It’s about knowing when not to act.

⚠️ Disclaimer

This project explores cognitive ideas inspired by:

predictive processing

Hebbian learning

active inference

biological cognition

It is experimental and may behave in unexpected ways.

That’s the point.
