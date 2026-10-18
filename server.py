#!/usr/bin/env python3
"""Live2 Revenue OS: stdlib-only local-first GTM operating system.
Research: Tavily optional; LLM synthesis: OpenAI optional; outbound disabled.
"""
import os,json,sqlite3,datetime,urllib.request,urllib.error,threading,uuid,re
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
BASE=Path(__file__).resolve().parent; WEB=BASE/'web'; DATA=BASE/'data'; DB=DATA/'revenue.db'; LOCK=threading.Lock()
COUNTRIES={'UK':{'rank':1,'motion':'Commerce activation + Shopify agencies','why':'Large ecommerce and creator agency ecosystem; English-first selling','competitors':'Bambuser, Bazaarvoice, Emplifi, Modash','buyer':'VP Ecommerce / Head of Digital'},'Netherlands':{'rank':2,'motion':'Cross-market creator campaign intelligence','why':'High reported influencer budget concentration; cross-border brands','competitors':'Kolsquare, Modash, Skeepers','buyer':'Head of Influencer / CMO'},'Germany':{'rank':3,'motion':'Enterprise campaign audits + governance','why':'Large multi-brand retail groups and DACH campaigns','competitors':'Kolsquare/Storyclash, Traackr, Brandwatch','buyer':'Global Marketing / Ecommerce Director'},'France':{'rank':4,'motion':'Beauty and luxury creator operations','why':'Global beauty HQs; sophisticated creator ecosystem','competitors':'Skeepers, Kolsquare, Launchmetrics','buyer':'Influencer Director'},'Spain':{'rank':5,'motion':'Fashion creator commerce','why':'Fashion retailers and growing creator investment','competitors':'Kolsquare, Modash, Skeepers','buyer':'Head of Ecommerce'},'Italy':{'rank':6,'motion':'Fashion and beauty commerce via partners','why':'Fashion and beauty heritage with omnichannel retailers','competitors':'Skeepers, Kolsquare','buyer':'Digital Commerce Director'},'Sweden':{'rank':7,'motion':'Selective commerce/agency partners','why':'Digitally mature Nordic retailers','competitors':'Bambuser, Kolsquare/Woomio','buyer':'Ecommerce Director'},'Denmark':{'rank':8,'motion':'Nordic agency and commerce pilots','why':'Cross-border retail and specialized agencies','competitors':'Bambuser, Kolsquare/Woomio','buyer':'Digital Director'}}
AGENTS=[('Market Scout','Selects country and ICP, checks fit and market play'),('Signal Hunter','Retrieves public expansion, hiring, executive and campaign evidence'),('Account Analyst','Synthesizes sourced account hypothesis and risks'),('Buyer Mapper','Identifies buyer roles; never invents personal contacts'),('Offer Architect','Selects product use case, pilot and discovery question'),('Outreach Guardian','Drafts personalized outreach; blocks sending pending approval'),('Revenue Strategist','Creates next actions, expansion path and pipeline hypothesis')]
SCHEMA='''CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, name TEXT, country TEXT, segment TEXT, score INTEGER, evidence TEXT, source TEXT, product TEXT, buyer TEXT, pilot TEXT, discovery TEXT, risk TEXT, next_action TEXT, status TEXT DEFAULT 'Research', owner TEXT DEFAULT 'Unassigned', notes TEXT DEFAULT '', acv INTEGER DEFAULT 40000, agency INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, type TEXT, headline TEXT, detail TEXT, source TEXT, observed TEXT, verified INTEGER DEFAULT 0, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, name TEXT, title TEXT, email TEXT, source TEXT, verified INTEGER DEFAULT 0, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, mode TEXT, state TEXT, output TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, title TEXT, owner TEXT DEFAULT 'AE', status TEXT DEFAULT 'Open', due TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS drafts(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, subject TEXT, body TEXT, status TEXT DEFAULT 'Pending', created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS deals(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, name TEXT, stage TEXT DEFAULT 'Discovery', acv INTEGER DEFAULT 40000, close_date TEXT, notes TEXT DEFAULT '', created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, channel TEXT, hypothesis TEXT, target INTEGER DEFAULT 0, meetings INTEGER DEFAULT 0, opportunities INTEGER DEFAULT 0, wins INTEGER DEFAULT 0, status TEXT DEFAULT 'Planned');
CREATE TABLE IF NOT EXISTS knowledge(id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, title TEXT, content TEXT, source TEXT, approved INTEGER DEFAULT 0, updated TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, kind TEXT, detail TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS integrations(name TEXT PRIMARY KEY, configured INTEGER DEFAULT 0, notes TEXT);'''
def connect():
 c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c
def seed():
 DATA.mkdir(exist_ok=True)
 with LOCK,connect() as c:
  c.executescript(SCHEMA)
  if c.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]==0:
   for a in json.loads((DATA/'accounts.json').read_text(encoding='utf-8')):
    c.execute('INSERT INTO accounts(name,country,segment,score,evidence,source,product,buyer,pilot,discovery,risk,next_action,status,agency) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(a.get('Account'),a.get('Country'),a.get('Segment'),int(a.get('Score') or 0),a.get('Public evidence'),a.get('Evidence URL'),a.get('Product hypothesis'),a.get('Economic buyer'),a.get('Pilot'),a.get('Discovery'),a.get('Deal risk'),a.get('Next action'),'Research',int('agency' in str(a.get('Segment','')).lower())))
  if c.execute('SELECT COUNT(*) FROM experiments').fetchone()[0]==0:
   for row in [('UK shoppable-video sprint','Direct ABM','Video-rich UK ecommerce brands will accept a scoped commerce pilot',40),('Benelux campaign audit','Direct ABM','Public campaign evidence supports executive audit conversations',30),('Shopify agency co-sell','Agency channel','Implementation partners can introduce several merchant customers',20),('Growth-trigger ABM','Signal outbound','Recent expansion and hiring signals outperform static messaging',50),('Competitor complement','Competitive ABM','A narrow workflow can complement installed tools',30),('Commerce readiness grader','Inbound','Interactive diagnostic attracts high-intent ecommerce teams',100),('Executive roundtables','Events','Peer discussion generates qualified enterprise discovery',20),('Subsidiary expansion','Customer expansion','Existing client relationships shorten access to new European markets',15)]:c.execute('INSERT INTO experiments(name,channel,hypothesis,target) VALUES(?,?,?,?)',row)
  if c.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0]==0:
   for row in [('Product truth','Social Commerce','Shoppable videos, stories and social walls; confirm enterprise packaging and supported integrations with product team.','https://live2.ai',0),('Product truth','Social Intelligence','Campaign intelligence and social content analysis; validate production coverage, data sources and restrictions.','https://live2.ai',0),('Compliance','Outreach rules','Human approval required before sending; honor opt-outs and local B2B marketing requirements; no fabricated contacts.', '',1),('Commercial','ARR model','Target: 75 annual contracts at blended $40k ACV = $3M exit ARR. Planning assumption, not forecast.','',1)]:c.execute('INSERT INTO knowledge(category,title,content,source,approved) VALUES(?,?,?,?,?)',row)
  for name,desc in [('Tavily','Public web research'),('OpenAI','Optional structured reasoning'),('HubSpot','Not connected; CRM export available'),('Apollo','Not connected; no contact enrichment'),('Hunter','Not connected; verification manual'),('Smartlead','Not connected; sending disabled')]:c.execute('INSERT OR IGNORE INTO integrations(name,configured,notes) VALUES(?,?,?)',(name,0,desc))
  c.execute('UPDATE integrations SET configured=? WHERE name=?',(int(bool(os.getenv('TAVILY_API_KEY'))),'Tavily'))
  c.execute('UPDATE integrations SET configured=? WHERE name=?',(int(bool(os.getenv('OPENAI_API_KEY'))),'OpenAI'))
def allrows(q,args=()):
 with connect() as c:return [dict(r) for r in c.execute(q,args).fetchall()]
def one(q,args=()):
 with connect() as c:
  r=c.execute(q,args).fetchone();return dict(r) if r else None
def execute(q,args=()):
 with LOCK,connect() as c:
  cur=c.execute(q,args);return cur.lastrowid
def log(a,kind,detail):execute('INSERT INTO activities(account_id,kind,detail) VALUES(?,?,?)',(a,kind,detail[:500]))
def search_web(query):
 key=os.getenv('TAVILY_API_KEY','').strip()
 if not key:return [],'offline — TAVILY_API_KEY not configured'
 payload=json.dumps({'api_key':key,'query':query,'search_depth':'basic','max_results':6,'include_answer':False}).encode()
 req=urllib.request.Request('https://api.tavily.com/search',payload,{'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=22) as res: data=json.load(res)
 return [{'title':str(x.get('title',''))[:180],'url':str(x.get('url',''))[:600],'snippet':str(x.get('content',''))[:900]} for x in data.get('results',[])],'live search (unverified snippets)'
def llm_analysis(account,sources):
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key or not sources:return None
 system='You are a cautious European enterprise GTM research analyst. Return JSON only: {"triggers":[{"type":"growth|hiring|executive|campaign|commerce|partnership","headline":"...","detail":"...","source":"exact URL from input"}],"pain_hypothesis":"...","buyer_roles":["..."],"pilot":"...","risks":["..."]}. Never invent names, emails, claims or buyer intent. Triggers are unverified until reviewed. Only use provided sources.'
 body=json.dumps({'model':os.getenv('OPENAI_MODEL','gpt-4o-mini'),'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps({'account':account,'sources':sources})[:14000]}]})
 req=urllib.request.Request('https://api.openai.com/v1/chat/completions',body.encode(),{'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=35) as res:raw=json.load(res)
 return json.loads(raw['choices'][0]['message']['content'])
def agent_run(account_id,live=False):
 a=one('SELECT * FROM accounts WHERE id=?',(account_id,))
 if not a:raise ValueError('Account not found')
 market=COUNTRIES.get(a['country'],{}); sources=[];mode='demo / seeded evidence';analysis=None;errors=[]
 if live:
  try:sources,mode=search_web(f'"{a["name"]}" {a["country"]} 2026 growth expansion hiring executive ecommerce influencer marketing')
  except Exception as e:errors.append('Research provider unavailable: '+str(e)[:180]);mode='research unavailable'
  if sources and os.getenv('OPENAI_API_KEY'):
   try:analysis=llm_analysis(a,sources);mode+=' + LLM analysis'
   except Exception as e:errors.append('LLM analysis unavailable: '+str(e)[:180])
 triggers=analysis.get('triggers',[]) if analysis else []
 # Only persist evidence if it has an exact URL among returned search sources.
 urls={s['url'] for s in sources}
 for t in triggers[:8]:
  if t.get('source') in urls:
   execute('INSERT INTO signals(account_id,type,headline,detail,source,observed,verified) VALUES(?,?,?,?,?,?,0)',(account_id,str(t.get('type','research'))[:40],str(t.get('headline',''))[:200],str(t.get('detail',''))[:1200],t['source'],datetime.date.today().isoformat()))
 steps=[{'agent':'Market Scout','status':'completed','finding':f'{a["country"]} · {a["segment"]} · ICP score {a["score"]}/100','evidence':market.get('why','')},
 {'agent':'Signal Hunter','status':'completed' if sources else 'needs connection','finding':f'{len(sources)} public search results retrieved; {len(triggers)} LLM-extracted candidate signals.' if sources else 'No new live evidence retrieved; existing account evidence is seeded.','evidence':a['source']},
 {'agent':'Account Analyst','status':'review required','finding':(analysis or {}).get('pain_hypothesis') or f'Hypothesis: {a["product"]}. This is not a verified customer pain point.','evidence':a['evidence']},
 {'agent':'Buyer Mapper','status':'review required','finding':'Likely economic buyer: '+str(a['buyer'])+'. '+(', '.join(analysis.get('buyer_roles',[])) if analysis else 'Named buyer and email require verification.'),'evidence':'No individual identity asserted'},
 {'agent':'Offer Architect','status':'review required','finding':(analysis or {}).get('pilot') or a['pilot'],'evidence':'Proposed pilot; validate product scope and ROI'},
 {'agent':'Outreach Guardian','status':'blocked','finding':'Create an editable draft; human approval and lawful basis review required. No email is sent.','evidence':'Sending integration intentionally disabled'},
 {'agent':'Revenue Strategist','status':'review required','finding':'Next: '+str(a['next_action'])+' · Indicative ACV $'+str(a['acv']),'evidence':'Planning assumptions only'}]
 result={'account':a['name'],'country':a['country'],'mode':mode,'steps':steps,'sources':sources,'analysis':analysis,'errors':errors,'outreach_sent':False,'created':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 rid=execute('INSERT INTO runs(account_id,mode,state,output) VALUES(?,?,?,?)',(account_id,mode,'Needs review',json.dumps(result)))
 log(account_id,'Agent run',f'Run #{rid}: {mode}')
 return {'id':rid,**result}
def draft_for(a):
 title='A question about '+a['name']+'’s '+('creator campaigns' if 'intelligence' in str(a['product']).lower() else 'social commerce')
 body=f'''Hi {{first_name}},\n\nI was looking at {a['name']} and its {a['country']} market presence. One area I’m exploring is whether brands can get more measurable value from creator content without replacing the systems they already use.\n\nA possible fit is {a['product']}. I would want to validate your current workflow first rather than assume there is a problem.\n\nWould it be useful to compare how you currently handle this and whether a scoped pilot could help?\n\nBest,\n{{sender_name}}\nLive2.ai'''
 return title,body
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(WEB),**kwargs)
 def log_message(self,*args):pass
 def respond(self,code,obj):
  b=json.dumps(obj,ensure_ascii=False,default=str).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  p=urlparse(self.path);path=p.path;qs=parse_qs(p.query)
  if path=='/':self.path='/index.html';return super().do_GET()
  if not path.startswith('/api/'):return super().do_GET()
  try:
   if path=='/api/bootstrap':
    return self.respond(200,{'accounts':allrows('SELECT * FROM accounts ORDER BY score DESC'), 'signals':allrows('SELECT * FROM signals ORDER BY id DESC LIMIT 200'),'contacts':allrows('SELECT * FROM contacts ORDER BY id DESC'),'runs':allrows('SELECT id,account_id,mode,state,created FROM runs ORDER BY id DESC LIMIT 100'),'tasks':allrows('SELECT * FROM tasks ORDER BY id DESC'),'drafts':allrows('SELECT * FROM drafts ORDER BY id DESC'),'deals':allrows('SELECT * FROM deals ORDER BY id DESC'),'experiments':allrows('SELECT * FROM experiments'),'knowledge':allrows('SELECT * FROM knowledge ORDER BY id DESC'),'activities':allrows('SELECT * FROM activities ORDER BY id DESC LIMIT 100'),'integrations':allrows('SELECT * FROM integrations'),'countries':COUNTRIES,'agents':AGENTS,'live_research':bool(os.getenv('TAVILY_API_KEY')),'llm':bool(os.getenv('OPENAI_API_KEY'))})
   if path=='/api/run':
    r=one('SELECT * FROM runs WHERE id=?',(int(qs.get('id',['0'])[0]),));return self.respond(200,{**r,'output':json.loads(r['output'])} if r else {'error':'Not found'})
   if path=='/api/export':
    table=qs.get('table',['accounts'])[0]
    if table not in ('accounts','signals','contacts','tasks','deals','experiments','activities'):return self.respond(400,{'error':'Invalid table'})
    import csv,io
    rows=allrows('SELECT * FROM '+table);buf=io.StringIO()
    if rows:w=csv.DictWriter(buf,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    b=buf.getvalue().encode('utf-8-sig');self.send_response(200);self.send_header('Content-Type','text/csv; charset=utf-8');self.send_header('Content-Disposition',f'attachment; filename="live2_{table}.csv"');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
   return self.respond(404,{'error':'Unknown endpoint'})
  except Exception as e:return self.respond(500,{'error':str(e)[:300]})
 def do_POST(self):
  path=urlparse(self.path).path
  try:
   length=int(self.headers.get('Content-Length','0'))
   if length<1 or length>50000:return self.respond(400,{'error':'Invalid payload size'})
   d=json.loads(self.rfile.read(length));account=int(d.get('account_id') or 0)
   if path=='/api/agent/run':return self.respond(200,agent_run(account,bool(d.get('live'))))
   if path=='/api/accounts/update':
    field=d.get('field');allowed={'status','owner','notes','acv','score','next_action'}
    if field not in allowed:return self.respond(400,{'error':'Field not editable'})
    val=d.get('value');execute('UPDATE accounts SET '+field+'=? WHERE id=?',(val,account));log(account,'Account updated',f'{field}: {str(val)[:120]}');return self.respond(200,{'ok':True})
   if path=='/api/contacts/add':
    name=str(d.get('name','')).strip();title=str(d.get('title','')).strip()
    if not name or not title:return self.respond(400,{'error':'Name and title required'})
    cid=execute('INSERT INTO contacts(account_id,name,title,email,source,verified) VALUES(?,?,?,?,?,?)',(account,name[:150],title[:150],str(d.get('email',''))[:200],str(d.get('source',''))[:600],int(bool(d.get('verified')))));log(account,'Buyer added',name);return self.respond(200,{'id':cid})
   if path=='/api/signals/add':
    title=str(d.get('headline','')).strip();source=str(d.get('source','')).strip()
    if not title:return self.respond(400,{'error':'Headline required'})
    sid=execute('INSERT INTO signals(account_id,type,headline,detail,source,observed,verified) VALUES(?,?,?,?,?,?,?)',(account,str(d.get('type','other'))[:40],title[:200],str(d.get('detail',''))[:1000],source[:600],str(d.get('observed',datetime.date.today().isoformat()))[:30],int(bool(d.get('verified')))));log(account,'Signal added',title);return self.respond(200,{'id':sid})
   if path=='/api/signals/verify':execute('UPDATE signals SET verified=? WHERE id=?',(int(bool(d.get('verified'))),int(d.get('id'))));return self.respond(200,{'ok':True})
   if path=='/api/tasks/add':
    title=str(d.get('title','')).strip()
    if not title:return self.respond(400,{'error':'Title required'})
    tid=execute('INSERT INTO tasks(account_id,title,owner,due) VALUES(?,?,?,?)',(account,title[:300],str(d.get('owner','AE'))[:100],str(d.get('due',''))[:20]));log(account,'Task created',title);return self.respond(200,{'id':tid})
   if path=='/api/tasks/update':
    if d.get('status') not in ('Open','In progress','Done'):return self.respond(400,{'error':'Invalid status'})
    execute('UPDATE tasks SET status=? WHERE id=?',(d['status'],int(d['id'])));return self.respond(200,{'ok':True})
   if path=='/api/drafts/create':
    a=one('SELECT * FROM accounts WHERE id=?',(account,))
    if not a:return self.respond(404,{'error':'Account not found'})
    sub,body=draft_for(a);did=execute('INSERT INTO drafts(account_id,subject,body) VALUES(?,?,?)',(account,sub,body));log(account,'Draft created','Pending approval');return self.respond(200,{'id':did})
   if path=='/api/drafts/update':
    status=str(d.get('status','Pending'))
    if status not in ('Pending','Approved','Rejected'):return self.respond(400,{'error':'Invalid approval status'})
    execute('UPDATE drafts SET subject=?,body=?,status=? WHERE id=?',(str(d.get('subject',''))[:250],str(d.get('body',''))[:10000],status,int(d['id'])));return self.respond(200,{'ok':True,'sent':False})
   if path=='/api/deals/add':
    name=str(d.get('name','')).strip()
    if not name:return self.respond(400,{'error':'Deal name required'})
    did=execute('INSERT INTO deals(account_id,name,stage,acv,close_date,notes) VALUES(?,?,?,?,?,?)',(account,name[:200],'Discovery',int(d.get('acv') or 40000),str(d.get('close_date',''))[:20],str(d.get('notes',''))[:1000]));log(account,'Opportunity created',name);return self.respond(200,{'id':did})
   if path=='/api/deals/update':
    stage=d.get('stage')
    if stage not in ('Discovery','Qualified','Pilot','Proposal','Negotiation','Won','Lost'):return self.respond(400,{'error':'Invalid stage'})
    execute('UPDATE deals SET stage=? WHERE id=?',(stage,int(d['id'])));return self.respond(200,{'ok':True})
   if path=='/api/experiments/update':
    vals=[max(0,int(d.get(x) or 0)) for x in ('meetings','opportunities','wins')];status=d.get('status','Planned')
    if status not in ('Planned','Running','Paused','Completed'):return self.respond(400,{'error':'Invalid status'})
    execute('UPDATE experiments SET meetings=?,opportunities=?,wins=?,status=? WHERE id=?',(*vals,status,int(d['id'])));return self.respond(200,{'ok':True})
   if path=='/api/knowledge/add':
    if not d.get('title') or not d.get('content'):return self.respond(400,{'error':'Title and content required'})
    kid=execute('INSERT INTO knowledge(category,title,content,source,approved) VALUES(?,?,?,?,?)',(str(d.get('category','General'))[:80],str(d['title'])[:200],str(d['content'])[:8000],str(d.get('source',''))[:600],int(bool(d.get('approved')))));return self.respond(200,{'id':kid})
   if path=='/api/knowledge/approve':execute('UPDATE knowledge SET approved=? WHERE id=?',(int(bool(d.get('approved'))),int(d['id'])));return self.respond(200,{'ok':True})
   return self.respond(404,{'error':'Unknown endpoint'})
  except (ValueError,TypeError,json.JSONDecodeError) as e:return self.respond(400,{'error':str(e)[:300]})
  except Exception as e:return self.respond(500,{'error':str(e)[:300]})
if __name__=='__main__':
 seed();port=int(os.getenv('PORT','8765'));print(f'Live2 Revenue OS FULL → http://localhost:{port}',flush=True);print('Tavily:',bool(os.getenv('TAVILY_API_KEY')),'OpenAI:',bool(os.getenv('OPENAI_API_KEY')),'Outbound: disabled',flush=True);ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
