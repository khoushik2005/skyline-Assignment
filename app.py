import json,uuid
from datetime import datetime,timezone
import pandas as pd
import streamlit as st
from service_agent.policies import POLICIES,REQUESTS,TICKETS
from service_agent.engine import ticket
from service_agent.ai import suggest_intent
st.set_page_config(page_title="Veridian IT Service Agent",page_icon="🛟",layout="wide")
st.markdown("""<style>
.stApp{background:#f6f8fc;color:#16233f}.hero{padding:1.4rem 1.6rem;border-radius:18px;background:linear-gradient(120deg,#15264b,#2458a6);color:white;margin-bottom:1rem}.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.35rem 0 0;color:#dbe8ff}.pill{display:inline-block;padding:.2rem .65rem;border-radius:999px;background:#e8f0ff;color:#174a93;font-size:.8rem;font-weight:700}.source{padding:.8rem;border-left:4px solid #2c63b7;background:white;border-radius:8px;margin:.35rem 0}.stButton>button{border-radius:10px;font-weight:700}</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><span class="pill">VERIDIAN CORP · IT SUPPORT</span><h1>Internal Service Agent</h1><p>Policy-grounded triage, safe routing, structured tickets and a visible audit trail.</p></div>',unsafe_allow_html=True)
if "audit" not in st.session_state: st.session_state.audit=[]
if "last" not in st.session_state: st.session_state.last=None
open_t=[x for x in TICKETS if "closed" not in x[3].lower()]
c1,c2,c3,c4=st.columns(4); c1.metric("Employee requests",len(REQUESTS)); c2.metric("Active queue",len(open_t)); c3.metric("Policy sources",len(POLICIES)); c4.metric("Security escalations",1)
tabs=st.tabs(["Resolve a request","Request inbox","Ticket queue","Knowledge & audit"])
with tabs[0]:
 left,right=st.columns([1,1.15],gap="large")
 with left:
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
 with right:
  st.subheader("Grounded decision")
  d=st.session_state.last
  if not d: st.info("Choose a supplied scenario or enter a new request, then assess it.")
  else:
   a,b,c=st.columns(3); a.metric("Priority",d['priority']); b.metric("Status",d['status']); c.metric("Route",d['route'])
   st.markdown(f"### {d['intent'].title()}")
   if d['priority']=="Critical": st.error(d['answer'])
   elif d['status'] in ["Escalated","Needs inspection","Needs triage"]: st.warning(d['answer'])
   else: st.success(d['answer'])
   if d['follow_up']: st.markdown(f"**Necessary follow-up**  \n{d['follow_up']}")
   st.markdown(f"**Why**  \n{d['rationale']}")
   st.caption(d['ai_mode'])
   st.markdown("**Sources used**")
   if d['sources']:
    for sid in d['sources']: st.markdown(f'<div class="source"><b>{sid} · {POLICIES[sid]["title"]}</b><br>{POLICIES[sid]["text"]}</div>',unsafe_allow_html=True)
   else: st.caption("No supplied policy authorizes a direct resolution; routed safely to a human.")
   st.download_button("Download structured ticket",json.dumps({k:v for k,v in d.items() if k not in ['event_id','timestamp_utc','action','ai_mode','ai_suggestion']},indent=2),file_name=f"{d['request_id']}-ticket.json",mime="application/json",width="stretch")
with tabs[1]:
 st.subheader("15 supplied employee requests")
 frame=pd.DataFrame(REQUESTS,columns=["Request ID","Employee","Email","Opened","Request","Initial action"])
 st.dataframe(frame,width="stretch",hide_index=True,height=520)
with tabs[2]:
 st.subheader("Existing ticket system record")
 q=pd.DataFrame(TICKETS,columns=["Ticket ID","Employee","Issue summary","Status"]); st.dataframe(q,width="stretch",hide_index=True)
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
   st.download_button("Download audit JSON",json.dumps(st.session_state.audit,indent=2),file_name="veridian-audit.json",mime="application/json")
  else: st.info("Each assessment will appear here with time, decision, source and AI mode.")
