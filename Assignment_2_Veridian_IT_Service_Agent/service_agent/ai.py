import os,json
ALLOWED={"password access","contractor VPN access","expired VPN credentials","VPN issue","guest Wi-Fi","printer issue","mailbox quota","expense tool login","home office equipment","non-catalog software","software installation","laptop hardware issue","laptop replacement","privileged access","security incident","unclear issue","unmatched issue"}
def suggest_intent(text):
 key=os.getenv("GROQ_API_KEY")
 try:
  import streamlit as st
  key=st.secrets.get("GROQ_API_KEY",key); model=st.secrets.get("GROQ_MODEL",os.getenv("GROQ_MODEL","llama-3.1-8b-instant"))
 except Exception: model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant")
 if not key: return None,"Deterministic mode (no API key)"
 try:
  from groq import Groq
  prompt="Classify this IT request into exactly one label: "+", ".join(sorted(ALLOWED))+". Return only the label. Request: "+text
  out=Groq(api_key=key).chat.completions.create(model=model,messages=[{"role":"user","content":prompt}],temperature=0,max_tokens=20).choices[0].message.content.strip()
  return (out if out in ALLOWED else None),"Groq intent suggestion"
 except Exception: return None,"Deterministic fallback (AI unavailable)"
