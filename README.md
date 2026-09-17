# Veridian IT Internal Service Agent — Assignment 2

A Streamlit prototype that turns the supplied Veridian Corp employee requests into grounded service decisions. It selects a policy, asks only necessary questions, resolves safe cases, escalates risky or unclear cases, creates a downloadable structured ticket, and records an audit trail.

## Run

Requires Python 3.11.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app works without an API key using the deterministic policy engine. Optional Groq intent suggestions never override the grounded decision:

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "..."
GROQ_MODEL = "llama-3.1-8b-instant"
```

## Architecture and process

`app.py` (four-part UI) → `service_agent.engine` (deterministic intent and policy rules) → supplied `policies.py` → structured decision/ticket → session audit and JSON downloads. `service_agent.ai` optionally asks Groq for a constrained intent suggestion; missing key, network failure or invalid output falls back safely.

1. Capture issue and existing action status.
2. Detect ambiguity or high-risk intent first.
3. Match only supplied knowledge sources.
4. Apply current/stricter controls where sources overlap. The Q2 2026 Asset extract controls the refresh cycle; KB-03 still contributes the hardware-failure and lead-time rules.
5. Preserve in-progress actions rather than duplicating work.
6. Return answer, required follow-up, route, status, rationale and source IDs.
7. Append a timestamped audit event.

## Inputs, sources and assumptions

- Only the supplied Assignment 2 data pack is encoded: KB-01 to KB-10, the Q2 2026 Asset Management extract, 15 employee requests, and TK-1042 to TK-1051.
- The scenario week is 21–25 September 2026.
- No portal URLs, asset tags, employee types, approvals, software catalog contents, or access policy were invented.
- Vague requests remain in employee follow-up. Privileged access is routed to a human because no supplied source grants authority.
- Ticket and audit downloads are session-local prototype artifacts, not writes to a real corporate system.

## AI tools disclosure

- **Groq API (optional):** constrained intent suggestion only, configured by `GROQ_API_KEY` and optional `GROQ_MODEL`. It cannot add policies or change the deterministic service action.
- **AI coding assistance:** used to help structure the prototype, test cases and presentation. All operational answers remain traceable to supplied sources.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Tests cover every supplied employee scenario, structured ticket completeness, the four active queue records, phishing safety, the laptop-policy overlap, and no-key fallback.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository with `app.py` at repository root.
2. In Streamlit Community Cloud choose **Create app**.
3. Select the repository, branch and entrypoint `app.py`.
4. Open **Advanced settings** and add `GROQ_API_KEY` and `GROQ_MODEL` in Secrets if Groq is wanted. The app works without them.
5. Deploy. `runtime.txt` requests Python 3.11 and `requirements.txt` contains bounded versions.

## Demo and defence

Use `DEMO_SCRIPT.md` for a 15-minute walkthrough. `Veridian_IT_Service_Agent_10_Slides.pptx` is the exactly 10-slide presentation. The assignment also asks the candidate to record a demo video, upload it to Drive with open access, and submit a GitHub link; those personal publishing steps are intentionally not fabricated by the project.
