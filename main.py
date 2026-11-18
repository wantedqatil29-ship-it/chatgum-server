from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

app = FastAPI(title='ChatGum Control Panel', version='0.1.0')

# Safe starter scaffold: account credentials and ChatGum private endpoints are not
# handled here. Connect only through an official/authorized ChatGum API.
bots = {f'bot-{i:02d}': {'name': f'Bot {i:02d}', 'active': False, 'room': None, 'draft': ''} for i in range(1, 51)}
rooms = {f'room-{i:02d}': {'name': f'Room {i:02d}'} for i in range(1, 11)}

class BotUpdate(BaseModel):
    active: Optional[bool] = None
    room: Optional[str] = None
    draft: Optional[str] = Field(default=None, max_length=1000)

@app.get('/health')
def health():
    return {'ok': True, 'service': 'chatgum-control', 'time': datetime.now(timezone.utc).isoformat()}

@app.get('/api/state')
def state():
    return {'bots': bots, 'rooms': rooms, 'integration': 'not_connected'}

@app.patch('/api/bots/{bot_id}')
def update_bot(bot_id: str, update: BotUpdate):
    if bot_id not in bots:
        raise HTTPException(404, 'Bot not found')
    data = update.model_dump(exclude_unset=True)
    if 'room' in data and data['room'] is not None and data['room'] not in rooms:
        raise HTTPException(400, 'Unknown room')
    bots[bot_id].update(data)
    return bots[bot_id]

@app.post('/api/bots/{bot_id}/send')
def send_message(bot_id: str):
    if bot_id not in bots:
        raise HTTPException(404, 'Bot not found')
    bot = bots[bot_id]
    if not bot['active']:
        raise HTTPException(409, 'Activate this bot first')
    if not bot['draft'].strip():
        raise HTTPException(400, 'Message draft is empty')
    # Deliberately no external send: ChatGum official API/access has not been verified.
    raise HTTPException(501, 'ChatGum sending is not connected. Add an official, authorized API adapter first.')

@app.get('/', response_class=HTMLResponse)
def dashboard():
    return HTML

HTML = r'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChatGum Control</title>
<style>body{font:15px system-ui;background:#0b1220;color:#e8eefc;margin:0;padding:22px}h1{margin:0 0 6px}.muted{color:#9aabc9}.stats{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}.stat,.bot{background:#151f33;border:1px solid #263653;border-radius:14px;padding:14px}.stat{min-width:120px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.bot h3{margin:0 0 10px}input,select,textarea,button{font:inherit;border-radius:8px;padding:9px;border:1px solid #344867;background:#0e1728;color:#eef}textarea{width:calc(100% - 20px);min-height:58px}button{cursor:pointer;background:#315ed8;border:0;margin:6px 4px 0 0}.status{font-size:12px;color:#9db4e5}.on{color:#6ee7a8}</style></head><body>
<h1>ChatGum Control</h1><div class="muted">50 account slots · 10 room slots · manual activation dashboard</div>
<div class="stats"><div class="stat"><b id="total">50</b><div class="muted">Bot slots</div></div><div class="stat"><b>10</b><div class="muted">Room slots</div></div><div class="stat"><b id="active">0</b><div class="muted">Active bots</div></div></div>
<p class="status">Integration status: not connected. Message sending stays disabled until an official/authorized ChatGum API is available.</p><div class="grid" id="bots"></div>
<script>
async function api(path,opts={}){let r=await fetch(path,{headers:{'Content-Type':'application/json'},...opts});let j=await r.json();if(!r.ok)throw Error(j.detail||'Request failed');return j}
async function load(){let s=await api('/api/state');document.getElementById('active').textContent=Object.values(s.bots).filter(b=>b.active).length;let root=document.getElementById('bots');root.innerHTML='';for(let [id,b] of Object.entries(s.bots)){let el=document.createElement('section');el.className='bot';el.innerHTML=`<h3>${b.name} <span class="status ${b.active?'on':''}">${b.active?'ACTIVE':'INACTIVE'}</span></h3><label>Room</label><select id="r-${id}">${Object.entries(s.rooms).map(([rid,r])=>`<option value="${rid}" ${b.room===rid?'selected':''}>${r.name}</option>`).join('')}</select><p><textarea id="d-${id}" placeholder="Message draft">${b.draft||''}</textarea></p><button onclick="save('${id}',true)">Activate</button><button onclick="save('${id}',false)">Deactivate</button><button onclick="send('${id}')">Send (API required)</button></section>`;root.appendChild(el)}}
async function save(id,active){try{await api('/api/bots/'+id,{method:'PATCH',body:JSON.stringify({active,room:document.getElementById('r-'+id).value,draft:document.getElementById('d-'+id).value})});load()}catch(e){alert(e.message)}}
async function send(id){try{await save(id,true);await api('/api/bots/'+id+'/send',{method:'POST'})}catch(e){alert(e.message)}}load();
</script></body></html>'''
