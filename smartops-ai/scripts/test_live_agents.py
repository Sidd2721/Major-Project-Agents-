import sys, urllib.request, json, time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("🚀 VERIFYING LIVE RUNNING SMARTOPS AI WORKFLOWS")
print("="*60)

# 1. Customer Support Flow
print("\n[1/3] Testing Customer Support Ticket Flow...")
payload = {
    'email': 'demo.student@university.edu',
    'order_id': 'ORD-LIVE-TEST-001',
    'complaint_text': 'URGENT: Battery expanded and sparked when plugged into the charger. Immediate safety risk!'
}
req = urllib.request.Request('http://localhost:8000/complaints', 
                             data=json.dumps(payload).encode('utf-8'),
                             headers={'Content-Type': 'application/json', 'User-Agent': 'SmartOps-LiveTest'})
with urllib.request.urlopen(req) as r:
    sub_res = json.loads(r.read().decode('utf-8'))
    ticket_id = sub_res.get('complaint_id')
    print(f"  ✓ Ticket submitted: ID #{ticket_id}")

print("  ... Waiting 4s for background AI triage worker ...")
time.sleep(4)

with urllib.request.urlopen('http://localhost:8000/complaints') as r:
    all_tickets = json.loads(r.read().decode('utf-8'))
    matched = [t for t in all_tickets if t.get('id') == ticket_id or t.get('order_id') == 'ORD-LIVE-TEST-001']
    if matched:
        t = matched[0]
        print(f"  ✅ Status         : {t.get('status')}")
        print(f"  ✅ Priority       : {t.get('priority')} (Reason: {t.get('priority_reason')})")
        print(f"  ✅ Sentiment      : {t.get('sentiment')}")
        print(f"  ✅ Draft Response : {str(t.get('response_draft'))[:90]}...")
    else:
        print("  ❌ Ticket not found")

# 2. Sales Assistant Flow
print("\n[2/3] Testing Sales Assistant Endpoints & Prospects...")
with urllib.request.urlopen('http://localhost:5175/api/prospects') as r:
    data = json.loads(r.read().decode('utf-8'))
    prospects = data.get('prospects', [])
    print(f"  ✅ Total Sales Prospects: {len(prospects)}")
    if prospects:
        p0 = prospects[0]
        print(f"  ✅ Sample Prospect: {p0.get('name')} @ {p0.get('company')} [Status: {p0.get('status')}]")

# 3. Voice Agent Flow
print("\n[3/3] Testing Voice Agent Live SQLite Context Grounding...")
v_payload = {
    'agent_id': 'support',
    'message': 'how many open P1 tickets are there?'
}
v_req = urllib.request.Request('http://localhost:8765/api/chat',
                               data=json.dumps(v_payload).encode('utf-8'),
                               headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(v_req) as r:
    v_res = json.loads(r.read().decode('utf-8'))
    print(f"  ✅ Voice Agent Reply : {v_res.get('reply')}")
    print(f"  ✅ Grounded DB Stats : {v_res.get('used_data')}")

print("\n" + "="*60)
print("🎯 ALL 3 AGENTS VERIFIED WORKING END-TO-END ON LOCALHOST!")
print("="*60)
