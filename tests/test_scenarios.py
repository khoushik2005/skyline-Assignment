import pytest
from service_agent.policies import REQUESTS,TICKETS
from service_agent.engine import resolve,ticket
EXPECTED={"REQ-01":("laptop hardware issue",["KB-03","ASSET"]),"REQ-02":("guest Wi-Fi",["KB-07"]),"REQ-03":("password access",["KB-01"]),"REQ-04":("non-catalog software",["KB-04"]),"REQ-05":("expired VPN credentials",["KB-02"]),"REQ-06":("printer issue",["KB-05"]),"REQ-07":("home office equipment",["KB-10","ASSET"]),"REQ-08":("security incident",["KB-09"]),"REQ-09":("mailbox quota",["KB-06"]),"REQ-10":("privileged access",[]),"REQ-11":("contractor VPN access",["KB-02"]),"REQ-12":("expense tool login",["KB-08"]),"REQ-13":("laptop hardware issue",["KB-03","ASSET"]),"REQ-14":("non-catalog software",["KB-04"]),"REQ-15":("unclear issue",[])}
@pytest.mark.parametrize("row",REQUESTS,ids=[x[0] for x in REQUESTS])
def test_all_employee_scenarios(row):
 d=resolve(row[4],row[5]); assert (d.intent,d.sources)==EXPECTED[row[0]]; assert d.answer and d.route and d.status and d.rationale
@pytest.mark.parametrize("row",REQUESTS)
def test_structured_ticket_complete(row):
 t=ticket(row[0],row[1],row[2],row[4],row[5]); assert set(["request_id","employee","email","summary","intent","priority","route","status","answer","follow_up","sources","rationale"])<=set(t)
def test_active_queue_rule():
 active=[x for x in TICKETS if "closed" not in x[3].lower()]; assert {x[0] for x in active}=={"TK-1043","TK-1044","TK-1047","TK-1048"}
def test_security_is_critical_and_no_forwarding():
 d=resolve("I received a phishing email and will forward it"); assert d.priority=="Critical" and "Do not forward" in d.answer and d.route=="Security"
def test_policy_conflict_uses_current_asset_control():
 d=resolve("Laptop is dead, had it 3.5 years"); assert "Finance" in d.answer and d.sources==["KB-03","ASSET"]
def test_no_key_ai_fallback(monkeypatch):
 monkeypatch.delenv("GROQ_API_KEY",raising=False)
 from service_agent.ai import suggest_intent
 out,mode=suggest_intent("VPN expired"); assert out is None and "no API key" in mode
