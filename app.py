import json,uuid
from datetime import datetime,timezone
import pandas as pd
import streamlit as st
from service_agent.policies import POLICIES,REQUESTS,TICKETS
from service_agent.engine import ticket
from service_agent.ai import suggest_intent

st.set_page_config(page_title="Veridian IT Service Agent",page_icon="🛟",layout="wide")

st.markdown("""<style>
:root{
 --ink:#16233f; --muted:#5b6b8c; --bg:#f4f7fc; --card:#ffffff; --line:#e6ebf5;
 --brand1:#15264b; --brand2:#2458a6; --accent:#2c63b7;
 --crit:#c0392b; --high:#c8720a; --norm:#1f8a5f;
}
.stApp{background:var(--bg) !important;color:var(--ink) !important}
[data-testid="stHeader"]{background:transparent}
.hero{padding:1.6rem 2rem;border-radius:20px;background:linear-gradient(120deg,var(--brand1),var(--brand2));
 color:#ffffff !important;margin-bottom:1.25rem;box-shadow:0 10px 30px -12px rgba(21,38,75,.55);}
.hero h1{margin:.3rem 0 0;font-size:2.05rem;font-weight:800;letter-spacing:-.01em;color:#ffffff !important}
.hero p{margin:.4rem 0 0;color:#dbe8ff !important;font-size:.98rem}
.pill{display:inline-block;padding:.25rem .7rem;border-radius:999px;background:rgba(255,255,255,.16);
 color:#eaf2ff !important;font-size:.74rem;font-weight:700;letter-spacing:.06em;border:1px solid rgba(255,255,255,.28)}

.kpi{background:var(--card) !important;border:1px solid var(--line);border-radius:14px;padding:.9rem 1.1rem;
 box-shadow:0 1px 2px rgba(20,30,60,.04)}
.kpi .n{font-size:1.6rem;font-weight:800;color:var(--brand1) !important;line-height:1.1}
.kpi .l{font-size:.78rem;color:var(--muted) !important;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin-top:.15rem}

.card{background:var(--card) !important;color:var(--ink) !important;border:1px solid var(--line);border-radius:16px;padding:1.1rem 1.25rem;
 box-shadow:0 1px 2px rgba(20,30,60,.04)}

.badge{display:inline-block;padding:.28rem .75rem;border-radius:999px;font-size:.76rem;font-weight:700;
 letter-spacing:.02em;margin-right:.4rem}
.b-crit{background:#fdeceb !important;color:var(--crit) !important;border:1px solid #f6c9c4}
.b-high{background:#fdf1df !important;color:var(--high) !important;border:1px solid #f4dba9}
.b-norm{background:#e8f6ef !important;color:var(--norm) !important;border:1px solid #bfe8d3}
.b-resolved{background:#e8f6ef !important;color:var(--norm) !important;border:1px solid #bfe8d3}
.b-pending{background:#eef1fb !important;color:#3a4b9c !important;border:1px solid #cfd6f2}
.b-waiting{background:#fdf1df !important;color:var(--high) !important;border:1px solid #f4dba9}
.b-escalated{background:#fdeceb !important;color:var(--crit) !important;border:1px solid #f6c9c4}
.b-progress{background:#e6f2fb !important;color:#1c5f9c !important;border:1px solid #bfdff5}
.b-triage{background:#f1eefb !important;color:#5b3fa8 !important;border:1px solid #d9cdf5}
.b-active{background:#fdf1df !important;color:var(--high) !important;border:1px solid #f4dba9}
.b-closed{background:#eef1f4 !important;color:#5b6b8c !important;border:1px solid #dbe1ea}

.decision-title{font-size:1.35rem;font-weight:800;color:var(--brand1) !important;margin:.2rem 0 .8rem}
.section-label{font-size:.76rem;font-weight:800;color:var(--muted) !important;text-transform:uppercase;
 letter-spacing:.06em;margin:.9rem 0 .3rem}
.answer-box{border-radius:12px;padding:.85rem 1rem;font-size:.98rem;line-height:1.5;margin:.2rem 0 .3rem;font-weight:500}
.answer-crit{background:#fdeceb !important;border:1px solid #f6c9c4;color:#7a241b !important}
.answer-warn{background:#fdf1df !important;border:1px solid #f4dba9;color:#7a4a06 !important}
.answer-ok{background:#e8f6ef !important;border:1px solid #bfe8d3;color:#12543a !important}

.source{padding:.85rem 1rem;border-left:4px solid var(--accent);background:#f8fafd !important;border-radius:0 10px 10px 0;
 margin:.45rem 0;color:#22304f !important}
.source b{color:var(--brand1) !important}

.stButton>button{border-radius:10px;font-weight:700}
.stDownloadButton>button{border-radius:10px;font-weight:700;background:#ffffff !important;color:var(--brand1) !important;
 border:1px solid var(--accent) !important}
.stDownloadButton>button:hover{background:#eaf1fb !important;color:var(--brand1) !important}
.stTabs [data-baseweb="tab-list"]{gap:4px}
.stTabs [data-baseweb="tab"]{border-radius:10px 10px 0 0;font-weight:600}
div[data-testid="stExpander"]{border-radius:12px;border:1px solid var(--line);background:var(--card) !important}
</style>""",unsafe_allow_html=True)

st.markdown(
 '<div class="hero"><span class="pill">VERIDIAN CORP · IT SUPPORT</span>'
 '<h1>🛟 Internal Service Agent</h1>'
 '<p>Policy-grounded triage, safe routing, structured tickets and a visible audit trail.</p></div>',
 unsafe_allow_html=True
)

if "audit" not in st.session_state: st.session_state.audit=[]
if "last" not in st.session_state: st.session_state.last=None
open_t=[x for x in TICKETS if "closed" not in x[3].lower()]

def kpi(col,label,value):
 col.markdown(f'<div class="kpi"><div class="n">{value}</div><div class="l">{label}</div></div>',unsafe_allow_html=True)

k1,k2,k3,k4=st.columns(4)
kpi(k1,"Employee requests",len(REQUESTS))
kpi(k2,"Active queue",len(open_t))
kpi(k3,"Policy sources",len(POLICIES))
kpi(k4,"Security escalations",1)
st.write("")

BADGE_MAP={
 "Critical":"b-crit","High":"b-high","Normal":"b-norm",
 "Resolved":"b-resolved","Escalated":"b-escalated","Pending approval":"b-pending",
 "Waiting for employee":"b-waiting","Waiting for troubleshooting":"b-waiting",
 "Needs inspection":"b-escalated","Needs investigation":"b-waiting","Needs triage":"b-triage",
 "In progress":"b-progress","Pending Security review":"b-waiting",
}
def badge(value):
 cls=BADGE_MAP.get(value,"b-pending")
 return f'<span class="badge {cls}">{value}</span>'

tabs=st.tabs(["🧭 Resolve a request","📥 Request inbox","🎫 Ticket queue","📚 Knowledge & audit"])

with tabs[0]:
 left,right=st.columns([1,1.15],gap="large")
 with left:
  st.markdown('<div class="card">',unsafe_allow_html=True)
  st.subheader("Request details")
  preset=st.selectbox("Load supplied scenario",["New request"]+[f"{x[0]} · {x[1]}" for x in REQUESTS])
  row=None if preset=="New request" else REQUESTS[[f"{x[0]} · {x[1]}" for x in REQUESTS].index(preset)]
  req_id=st.text_input("Request ID",row[0] if row else "NEW")
  employee=st.text_input("Employee",row[1] if row else "")
  email=st.text_input("Email",row[2] if row else "")
  initial=st.text_input("Current action/status",row[5] if row else "Not started")
  issue=st.text_area("What happened?",row[4] if row else "",height=145,placeholder="Describe the affected system, error and context...")
  if st.button("Assess and create ticket",type="primary",width="stretch"):
   if not issue.strip(): st.error("Enter the employee's issue first.")
   else:
    result=ticket(req_id,employee or "Unknown",email,issue,initial); ai_label,ai_mode=suggest_intent(issue)
    event={"event_id":str(uuid.uuid4()),"timestamp_utc":datetime.now(timezone.utc).isoformat(),"action":"ticket_assessed","ai_mode":ai_mode,**result}
    if ai_label: event["ai_suggestion"]=ai_label
    st.session_state.audit.append(event); st.session_state.last=event
  st.markdown('</div>',unsafe_allow_html=True)
 with right:
  st.markdown('<div class="card">',unsafe_allow_html=True)
  st.subheader("Grounded decision")
  d=st.session_state.last
  if not d: st.info("Choose a supplied scenario or enter a new request, then assess it.")
  else:
   st.markdown(badge(d['priority'])+badge(d['status'])+f'<span class="badge b-pending">{d["route"]}</span>',unsafe_allow_html=True)
   st.markdown(f'<div class="decision-title">{d["intent"].title()}</div>',unsafe_allow_html=True)
   box_cls="answer-crit" if d['priority']=="Critical" else ("answer-warn" if d['status'] in ["Escalated","Needs inspection","Needs triage"] else "answer-ok")
   st.markdown(f'<div class="answer-box {box_cls}">{d["answer"]}</div>',unsafe_allow_html=True)
   if d['follow_up']:
    st.markdown('<div class="section-label">Necessary follow-up</div>',unsafe_allow_html=True)
    st.write(d['follow_up'])
   st.markdown('<div class="section-label">Why</div>',unsafe_allow_html=True)
   st.write(d['rationale'])
   st.caption(f"🤖 {d['ai_mode']}")
   st.markdown('<div class="section-label">Sources used</div>',unsafe_allow_html=True)
   if d['sources']:
    for sid in d['sources']: st.markdown(f'<div class="source"><b>{sid} · {POLICIES[sid]["title"]}</b><br>{POLICIES[sid]["text"]}</div>',unsafe_allow_html=True)
   else: st.caption("No supplied policy authorizes a direct resolution; routed safely to a human.")
   st.download_button("⬇ Download structured ticket",json.dumps({k:v for k,v in d.items() if k not in ['event_id','timestamp_utc','action','ai_mode','ai_suggestion']},indent=2),file_name=f"{d['request_id']}-ticket.json",mime="application/json",width="stretch")
  st.markdown('</div>',unsafe_allow_html=True)

with tabs[1]:
 st.subheader("15 supplied employee requests")
 frame=pd.DataFrame(REQUESTS,columns=["Request ID","Employee","Email","Opened","Request","Initial action"])
 st.dataframe(frame,width="stretch",hide_index=True,height=520)

with tabs[2]:
 st.subheader("Existing ticket system record")
 q=pd.DataFrame(TICKETS,columns=["Ticket ID","Employee","Issue summary","Status"])
 q["State"]=q["Status"].apply(lambda s:"Closed" if "closed" in s.lower() else "Active")
 def style_state(v):
  cls="b-closed" if v=="Closed" else "b-active"
  return f'<span class="badge {cls}">{v}</span>'
 q_display=q.copy()
 q_display["State"]=q_display["State"].apply(style_state)
 st.write(q_display.to_html(escape=False,index=False),unsafe_allow_html=True)
 st.caption("Resolved, Rejected and Approved tickets are closed history. All others remain active cases.")

with tabs[3]:
 l,rgt=st.columns([1.15,1])
 with l:
  st.subheader("Supplied knowledge base")
  for sid,p in POLICIES.items():
   with st.expander(f"{sid} · {p['title']}"): st.write(p['text'])
 with rgt:
  st.subheader("Session audit trail")
  if st.session_state.audit:
   adf=pd.DataFrame(st.session_state.audit)
   st.dataframe(adf[["timestamp_utc","request_id","employee","intent","route","status","ai_mode"]],width="stretch",hide_index=True)
   st.download_button("⬇ Download audit JSON",json.dumps(st.session_state.audit,indent=2),file_name="veridian-audit.json",mime="application/json")
  else: st.info("Each assessment will appear here with time, decision, source and AI mode.")
