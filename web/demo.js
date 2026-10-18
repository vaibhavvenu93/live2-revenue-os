'use strict';
/* Live2 Revenue OS browser-only demonstration. No network research, no outbound, no shared database. */
(()=>{
const KEY='live2-demo-v1',nativeFetch=window.fetch.bind(window);
const countries={
UK:{rank:1,motion:'Commerce activation + Shopify agencies',why:'Ecommerce and creator agency ecosystem',competitors:'Bambuser, Bazaarvoice, Emplifi, Modash',buyer:'VP Ecommerce / Head of Digital'},
Netherlands:{rank:2,motion:'Cross-market creator campaign intelligence',why:'Cross-border brands and creator activity',competitors:'Kolsquare, Modash, Skeepers',buyer:'Head of Influencer / CMO'},
Germany:{rank:3,motion:'Enterprise campaign audits + governance',why:'Multi-brand retail and DACH campaigns',competitors:'Storyclash, Traackr, Brandwatch',buyer:'Marketing / Ecommerce Director'},
France:{rank:4,motion:'Beauty and luxury creator operations',why:'Beauty and luxury brand ecosystem',competitors:'Skeepers, Kolsquare, Launchmetrics',buyer:'Influencer Director'},
Spain:{rank:5,motion:'Fashion creator commerce',why:'Fashion and ecommerce brands',competitors:'Kolsquare, Modash',buyer:'Head of Ecommerce'},
Italy:{rank:6,motion:'Fashion and beauty commerce',why:'Omnichannel retail brands',competitors:'Skeepers, Kolsquare',buyer:'Digital Commerce Director'},
Sweden:{rank:7,motion:'Nordic agency and commerce',why:'Digitally mature Nordic retail',competitors:'Bambuser, Woomio',buyer:'Ecommerce Director'},
Denmark:{rank:8,motion:'Nordic commerce pilots',why:'Cross-border retail and agencies',competitors:'Bambuser, Woomio',buyer:'Digital Director'}};
const agents=[['Market Scout','Selects market and ICP'],['Signal Hunter','Checks evidence requirements'],['Account Analyst','Develops a hypothesis'],['Buyer Mapper','Suggests buyer roles only'],['Offer Architect','Proposes a pilot'],['Outreach Guardian','Drafts for approval'],['Revenue Strategist','Suggests next action']];
const experiments=[
['UK shoppable-video sprint','Direct ABM','Test a scoped commerce pilot',40],
['Benelux campaign audit','Direct ABM','Test executive campaign audit interest',30],
['Shopify agency co-sell','Agency channel','Test partner introductions',20],
['Growth-trigger ABM','Signal outbound','Compare signal-led outreach',50],
['Competitor complement','Competitive ABM','Test a complementary workflow',30],
['Commerce readiness grader','Inbound','Test diagnostic interest',100],
['Executive roundtables','Events','Test executive engagement',20],
['Subsidiary expansion','Customer expansion','Test multi-market introductions',15]];
const knowledge=[
['Product truth','Social Commerce','Shoppable videos, stories and social walls; confirm product scope with Live2.ai.','https://live2.ai',0],
['Product truth','Social Intelligence','Campaign intelligence; verify production data coverage and restrictions.','https://live2.ai',0],
['Compliance','Outreach rules','Human approval required; demo never sends email.','',1],
['Commercial','ARR model','75 annual contracts at $40k blended ACV = $3M exit ARR; illustrative target only.','',1]];
const integrations=['Tavily','OpenAI','HubSpot','Apollo','Hunter','Smartlead'].map(name=>({name,configured:0,notes:'Not connected in browser-only demo'}));
const now=()=>new Date().toISOString(),clone=x=>JSON.parse(JSON.stringify(x));
let state=null;
function persist(){try{localStorage.setItem(KEY,JSON.stringify(state));}catch(e){throw Error('Browser storage unavailable or full: '+e.message)}}
function idFor(table){return 1+Math.max(0,...state[table].map(x=>Number(x.id)||0))}
function activity(account_id,kind,detail){state.activities.unshift({id:idFor('activities'),account_id,kind,detail,created:now()});state.activities=state.activities.slice(0,100)}
function account(id){const a=state.accounts.find(x=>x.id===Number(id));if(!a)throw Error('Account not found');return a}
function byId(table,id){const x=state[table].find(y=>y.id===Number(id));if(!x)throw Error('Record not found');return x}
function draftFor(a){return {subject:'A question about '+a.name+'’s creator and commerce workflow',body:'Hi {first_name},\\n\\nI was looking at '+a.name+' and its '+a.country+' market presence. A possible area to explore is '+a.product+'. This is a hypothesis, not an assertion about your current workflow.\\n\\nWould it be useful to compare your current process and whether a scoped pilot could help?\\n\\nBest,\\n{sender_name}\\nLive2.ai'};}
async function initialize(){
 try{const saved=JSON.parse(localStorage.getItem(KEY)||'null');if(saved&&Array.isArray(saved.accounts)&&saved.version===1){state=saved;return}}catch{}
 const r=await nativeFetch('/data/accounts.json');if(!r.ok)throw Error('Seed data unavailable ('+r.status+')');
 const rows=await r.json();
 state={version:1,accounts:rows.map((a,i)=>({id:i+1,name:a.Account,country:a.Country,segment:a.Segment,score:Number(a.Score)||0,evidence:a['Public evidence']||'',source:a['Evidence URL']||'',product:a['Product hypothesis']||'',buyer:a['Economic buyer']||'',pilot:a.Pilot||'',discovery:a.Discovery||'',risk:a['Deal risk']||'',next_action:a['Next action']||'',status:'Research',owner:'Unassigned',notes:'',acv:40000,agency:/agency/i.test(a.Segment||'')?1:0})),signals:[],contacts:[],runs:[],tasks:[],drafts:[],deals:[],experiments:experiments.map((x,i)=>({id:i+1,name:x[0],channel:x[1],hypothesis:x[2],target:x[3],meetings:0,opportunities:0,wins:0,status:'Planned'})),knowledge:knowledge.map((x,i)=>({id:i+1,category:x[0],title:x[1],content:x[2],source:x[3],approved:x[4],updated:now()})),activities:[],integrations};persist();
}
function agentRun(d){
 const a=account(d.account_id),market=countries[a.country]||{},steps=[
 {agent:'Market Scout',status:'demo complete',finding:a.country+' · '+a.segment+' · ICP score '+a.score+'/100',evidence:market.why||''},
 {agent:'Signal Hunter',status:'not connected',finding:'SIMULATED: No live search was performed. Existing evidence is a seeded research hypothesis.',evidence:a.source},
 {agent:'Account Analyst',status:'review required',finding:'Hypothesis: '+a.product+'. Not verified customer pain.',evidence:a.evidence},
 {agent:'Buyer Mapper',status:'review required',finding:'Likely role: '+a.buyer+'. No named contact has been verified.',evidence:'Role hypothesis only'},
 {agent:'Offer Architect',status:'review required',finding:a.pilot,evidence:'Pilot suggestion, not an agreed proposal'},
 {agent:'Outreach Guardian',status:'blocked',finding:'No external message sent. Human approval required.',evidence:'Browser-only demo'},
 {agent:'Revenue Strategist',status:'review required',finding:'Next: '+a.next_action+' · Illustrative ACV $'+a.acv,evidence:'Planning assumptions'}];
 const output={account:a.name,country:a.country,mode:'SIMULATED — browser-only; no web research or LLM',steps,sources:[],analysis:null,errors:[],outreach_sent:false,created:now()};
 const id=idFor('runs');state.runs.unshift({id,account_id:a.id,mode:output.mode,state:'Needs review',output:clone(output),created:now()});activity(a.id,'Simulated agent run','Run #'+id+' (no live research)');return {id,...output};
}
function handle(path,d={}){
 const aid=Number(d.account_id)||0;let x,a;
 if(path==='bootstrap')return {...clone(state),countries,agents,live_research:false,llm:false};
 if(path.startsWith('run?')){const id=new URLSearchParams(path.split('?')[1]).get('id');return clone(byId('runs',id))}
 if(path==='agent/run')return agentRun(d);
 if(path==='accounts/update'){if(!['status','owner','notes','acv','score','next_action'].includes(d.field))throw Error('Field not editable');a=account(aid);a[d.field]=d.value;activity(aid,'Account updated',d.field+': '+d.value);return {ok:true}}
 if(path==='contacts/add'){if(!String(d.name||'').trim()||!String(d.title||'').trim())throw Error('Name and title required');account(aid);x={id:idFor('contacts'),account_id:aid,name:d.name,title:d.title,email:d.email||'',source:d.source||'',verified:Number(!!d.verified),created:now()};state.contacts.unshift(x);activity(aid,'Buyer added',x.name);return {id:x.id}}
 if(path==='signals/add'){if(!d.headline)throw Error('Headline required');account(aid);x={id:idFor('signals'),account_id:aid,type:d.type||'other',headline:d.headline,detail:d.detail||'',source:d.source||'',observed:d.observed||now().slice(0,10),verified:Number(!!d.verified),created:now()};state.signals.unshift(x);activity(aid,'Signal added',x.headline);return {id:x.id}}
 if(path==='signals/verify'){byId('signals',d.id).verified=Number(!!d.verified);return {ok:true}}
 if(path==='tasks/add'){if(!d.title)throw Error('Title required');account(aid);x={id:idFor('tasks'),account_id:aid,title:d.title,owner:d.owner||'AE',status:'Open',due:d.due||'',created:now()};state.tasks.unshift(x);activity(aid,'Task created',x.title);return {id:x.id}}
 if(path==='tasks/update'){if(!['Open','In progress','Done'].includes(d.status))throw Error('Invalid status');byId('tasks',d.id).status=d.status;return {ok:true}}
 if(path==='drafts/create'){a=account(aid);x={id:idFor('drafts'),account_id:aid,...draftFor(a),status:'Pending',created:now()};state.drafts.unshift(x);activity(aid,'Draft created','Simulated draft; not sent');return {id:x.id}}
 if(path==='drafts/update'){if(!['Pending','Approved','Rejected'].includes(d.status))throw Error('Invalid approval');x=byId('drafts',d.id);Object.assign(x,{subject:d.subject,body:d.body,status:d.status});return {ok:true,sent:false}}
 if(path==='deals/add'){if(!d.name)throw Error('Deal name required');account(aid);x={id:idFor('deals'),account_id:aid,name:d.name,stage:'Discovery',acv:Number(d.acv)||40000,close_date:d.close_date||'',notes:d.notes||'',created:now()};state.deals.unshift(x);activity(aid,'Simulated opportunity created',x.name);return {id:x.id}}
 if(path==='deals/update'){if(!['Discovery','Qualified','Pilot','Proposal','Negotiation','Won','Lost'].includes(d.stage))throw Error('Invalid stage');byId('deals',d.id).stage=d.stage;return {ok:true}}
 if(path==='experiments/update'){if(!['Planned','Running','Paused','Completed'].includes(d.status))throw Error('Invalid status');x=byId('experiments',d.id);Object.assign(x,{meetings:Math.max(0,Number(d.meetings)||0),opportunities:Math.max(0,Number(d.opportunities)||0),wins:Math.max(0,Number(d.wins)||0),status:d.status});return {ok:true}}
 if(path==='knowledge/add'){if(!d.title||!d.content)throw Error('Title and content required');x={id:idFor('knowledge'),category:d.category||'General',title:d.title,content:d.content,source:d.source||'',approved:Number(!!d.approved),updated:now()};state.knowledge.unshift(x);return {id:x.id}}
 if(path==='knowledge/approve'){byId('knowledge',d.id).approved=Number(!!d.approved);return {ok:true}}
 throw Error('Unsupported demo action: '+path);
}
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
window.fetch=async(input,init={})=>{
 const url=typeof input==='string'?input:input.url;
 if(!url.startsWith('/api/'))return nativeFetch(input,init);
 try{await ready;const path=url.slice(5);if(path.startsWith('export'))throw Error('CSV export unavailable in browser demo');
 const d=init.body?JSON.parse(init.body):{};const result=handle(path,d);
 if(init.body)persist();return json(result);
 }catch(e){return json({error:String(e.message||e)},400)}
};
const ready=initialize();
window.LIVE2_DEMO={ready,reset(){if(confirm('Reset all browser-only demo changes?')){localStorage.removeItem(KEY);location.reload()}},download(){const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='live2-demo-backup.json';a.click();URL.revokeObjectURL(u)}};
ready.then(()=>{
 const banner=document.createElement('div');banner.id='demo-banner';banner.innerHTML='<strong>DEMO MODE — SIMULATED</strong> · Seeded research, illustrative pipeline and browser-only changes. No live agents, shared database, CRM sync or emails sent. <button id="demo-backup">Export demo data</button> <button id="demo-reset">Reset demo</button>';
 document.body.prepend(banner);document.getElementById('demo-backup').onclick=()=>window.LIVE2_DEMO.download();document.getElementById('demo-reset').onclick=()=>window.LIVE2_DEMO.reset();
}).catch(e=>{const el=document.createElement('div');el.textContent='Demo initialization failed: '+e.message;document.body.prepend(el)});
})();