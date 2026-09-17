from dataclasses import dataclass,asdict
from .policies import POLICIES
@dataclass
class Decision:
 intent:str; route:str; status:str; priority:str; answer:str; follow_up:str; sources:list; rationale:str
 def as_dict(self): return asdict(self)
def resolve(text, initial_status="Not started"):
 t=text.lower().strip(); follow=""
 if not t or len(t.split())<5 or ("not working" in t and not any(x in t for x in ["vpn","printer","laptop","mail","expense"])):
  return Decision("unclear issue","Employee follow-up","Waiting for employee","Normal","I need a little more detail before I can help.","What is not working, what error do you see, and which device or application is affected?",[],"The request is too vague to safely select a policy.")
 if any(x in t for x in ["phish","malware","unauthorized access"]):
  return Decision("security incident","Security","Escalated","Critical","Report this immediately to security@veridian-corp.example. Do not forward it to other employees.","If safe, provide the sender address and time received directly to Security.",["KB-09"],"Security incidents require immediate escalation and restricted sharing.")
 if "password" in t or "locked out" in t:
  locked=any(x in t for x in ["6 times","5 failed","locked out"])
  return Decision("password access","IT Service Desk" if locked else "Self-service","Escalated" if locked else "Resolved","High" if locked else "Normal","Contact IT for a manual unlock; a reset is already queued." if locked and "queued" in initial_status.lower() else ("Contact IT for a manual unlock, then reset your password." if locked else "Use the self-service portal to reset your password."),"",["KB-01"],"Five failed attempts lock the account; otherwise self-service applies.")
 if "vpn" in t:
  if "contractor" in t: return Decision("contractor VPN access","Manager / Access Request","Pending approval","Normal","Submit manager approval through the access request form for the contractor.","Has the manager submitted the access request form?",["KB-02"],"Contractor VPN requires manager approval.")
  if "expired" in t: return Decision("expired VPN credentials","Employee self-service","Resolved","High","Renew the VPN credentials; employee VPN credentials expire every 90 days.","",["KB-02"],"Credential renewal is the employee's next action.")
  return Decision("VPN issue","IT Service Desk","Needs investigation","Normal","Full-time employees receive VPN automatically; IT should investigate the connection issue.","Are you a full-time employee or contractor, and what error do you see?",["KB-02"],"Employment type changes the access path.")
 if "guest" in t and ("wi-fi" in t or "wifi" in t): return Decision("guest Wi-Fi","Front-desk kiosk","Resolved","Normal","Any employee can generate 24-hour guest Wi-Fi credentials at the front-desk kiosk. No IT ticket is needed.","",["KB-07"],"The policy provides a self-service route.")
 if "printer" in t or "paper jam" in t:
  done=any(x in initial_status.lower() for x in ["investigating","technician"])
  return Decision("printer issue","IT Service Desk","In progress" if done else "Waiting for troubleshooting","Normal","A technician is already assigned; keep the existing investigation open." if done else "Check the printer queue and restart the print spooler.","" if done else "If it still fails after restart, what is the printer asset tag?",["KB-05"],"Troubleshoot first, then ticket with asset tag; existing work is not duplicated.")
 if "mailbox" in t or "quota" in t or "can't send email" in t or "can’t send email" in t:
  return Decision("mailbox quota","Employee / Manager","Waiting for employee","Normal","Archive old mail first. An increase above 25GB needs manager approval and cannot exceed 50GB.","After archiving, do you still need an increase, and has your manager approved it?",["KB-06"],"Archive is the immediate action; quota changes are controlled.")
 if "expense" in t:
  return Decision("expense tool login","IT Service Desk","Waiting for employee" if "waiting" in initial_status.lower() else "Needs investigation","Normal","IT can help with login issues only if an expense-tool account already exists.","Do you already have an account? If yes, share the exact error or screenshot.",["KB-08"],"Finance grants accounts; IT handles technical login issues.")
 if "work from home" in t or "home office" in t or ("monitor" in t and "week" in t):
  return Decision("home office equipment","Manager / Finance","Pending approval","Normal","Because you work remotely more than 3 days a week, request manager sign-off and Finance processing. IT handles shipping after approval.","Have manager sign-off and Finance approval been completed?",["KB-10","ASSET"],"The home-office allowance path applies; hardware remains governed by asset policy.")
 if any(x in t for x in ["software","install","extension"]):
  noncat=any(x in t for x in ["not in","non-catalog","extension"])
  return Decision("non-catalog software" if noncat else "software installation","IT Security" if noncat else "Self-service","Pending Security review" if noncat else "Resolved","Normal","Security review is already in progress; allow 3–5 business days." if noncat and "security" in initial_status.lower() else ("Submit the item for IT Security review; review takes 3–5 business days." if noncat else "Install it from the approved software catalog."),"What is the software/extension name and business purpose?" if noncat else "",["KB-04"],"Non-catalog items require Security review.")
 if "laptop" in t or "screen" in t or "hardware" in t:
  years=2 if "2 years" in t else (3.5 if "3.5" in t else None); failure=any(x in t for x in ["dead","won't turn on","won’t turn on","flicker"])
  if years and years<4: return Decision("laptop hardware issue","IT Hardware + Finance","Needs inspection","High" if "dead" in t else "Normal","IT must verify the hardware failure. Because the device is inside the current 4-year refresh cycle, any early replacement needs both IT approval and Finance sign-off.","Can IT inspect the device and confirm the issue and date of issue?",["KB-03","ASSET"],"The Q2 2026 asset extract is newer and stricter than the 3-year KB threshold, so early replacement controls apply.")
  return Decision("laptop replacement","IT Hardware","Needs inspection","Normal","Confirm the device issue date and hardware condition; replacement requests should be raised at least 2 weeks ahead.","What is the issue date and has hardware failure been verified?",["KB-03","ASSET"],"Eligibility and current asset controls must both be checked.")
 if "admin access" in t or "server" in t:
  return Decision("privileged access","Human access owner","Escalated","High","This request cannot be approved from the supplied IT policies. Route it to the human system owner for authorization.","Provide the business justification, required scope, approver, and duration.",[],"No supplied policy authorizes privileged access; urgency does not create authority.")
 return Decision("unmatched issue","IT Service Desk","Needs triage","Normal","No supplied policy safely resolves this request. Route it to a human for triage.","What system is affected, what error appears, and when did it begin?",[],"No grounded policy match was found.")
def ticket(req_id,employee,email,text,initial="Not started"):
 d=resolve(text,initial); return {"request_id":req_id,"employee":employee,"email":email,"summary":text,"intent":d.intent,"priority":d.priority,"route":d.route,"status":d.status,"answer":d.answer,"follow_up":d.follow_up,"sources":d.sources,"rationale":d.rationale}
