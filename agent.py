# agent.py — AI Compliance RAG Agent (Free, Local LLM)
import ollama
import json
from tools import list_files, grab, read_file

# ── Configuration ─────────────────────────────────────────────────
MODEL = "phi3"          # Change to "llama3" or "mistral" if pulled
MAX_STEPS = 10
DEBUG = True            # Set False to hide intermediate results

# ── Tool Registry ─────────────────────────────────────────────────
TOOLS = {
    "list_files": list_files,
    "grab": grab,
    "read_file": read_file,
}

# ── Tool Definitions ──────────────────────────────────────────────
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all compliance documents in the knowledge base. Call this first.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grab",
            "description": (
                "Searches compliance documents for keywords, article references, "
                "system names, risk levels, or status indicators like OPEN or MISSING."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search term e.g. 'Article 14', 'OPEN', 'human-in-the-loop', 'MISSING'"
                    }
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads full content of a compliance document by exact filename.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Exact filename e.g. 'ai_risk_register.md'"
                    }
                },
                "required": ["filename"],
            },
        },
    },
]

# ── System Prompt ─────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an AI Compliance Assistant supporting a Chief AI Compliance Officer (CAICO).

Your knowledge base contains internal compliance documents including:
- AI Risk Registers (EU AI Act Articles 9-15)
- Audit Findings and Remediation Trackers
- Human-in-the-loop and Human-on-the-loop Control Registers
- Vendor Conformity Documentation Logs
- Open Remediation Items

When answering compliance questions:
1. Start by listing available files to understand the knowledge base
2. Search for specific terms before reading full documents
3. Always cite the exact document name and line number
4. Explicitly flag: OPEN findings, MISSING documentation, NOT IMPLEMENTED controls
5. Structure answers clearly for compliance reporting and board-level communication
6. Reference the relevant EU AI Act article when applicable
"""

# ── Agentic Loop ──────────────────────────────────────────────────
def run_compliance_agent(question: str):

    print(f"\n{'='*65}")
    print(f"COMPLIANCE QUERY: {question}")
    print(f"{'='*65}\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(MAX_STEPS):
        print(f"[Step {step + 1}] Reasoning...")

        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )

        message = response["message"]
        messages.append(message)

        # No tool calls means final answer is ready
        if not message.get("tool_calls"):
            print(f"\n{'='*65}")
            print("COMPLIANCE ANSWER:")
            print(f"{'='*65}\n")
            print(message["content"])
            print(f"\n[Total reasoning steps: {step + 1}]")
            return message["content"]

        # Execute each tool call
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"].get("arguments") or {}

            print(f"  → {tool_name}({tool_args})")

            if tool_name in TOOLS:
                result = TOOLS[tool_name](**tool_args) if tool_args else TOOLS[tool_name]()
            else:
                result = f"Unknown tool: {tool_name}"

            if DEBUG:
                preview = result[:200].replace('\n', ' ')
                print(f"  ← {preview}...")

            messages.append({
                "role": "tool",
                "content": result,
            })

    return "Maximum steps reached. Please refine your query."


# ── Compliance Demo Queries ───────────────────────────────────────
if __name__ == "__main__":

    demo_queries = [
        "Which high-risk AI systems are missing human-in-the-loop controls?",
        "List all OPEN audit findings with their owners and due dates.",
        "Which vendors have missing conformity documentation?",
        "What remediation actions are critical priority and not yet started?",
    ]

    for query in demo_queries:
        run_compliance_agent(query)
        print("\n" + "─"*65 + "\n")
