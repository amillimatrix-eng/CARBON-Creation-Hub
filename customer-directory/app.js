(() => {
const degreeData=[
 {index:'01 / BUSINESS',title:'Business°',subtitle:'Strategy & Commercial',copy:'Positioning, go-to-market, commercial structure and buyer-facing systems shaped around the decision that matters.',glow:'#777770',tags:['Strategy','Go-to-market','Commercial'],detail:['Route-to-market and proposition design','Commercial planning and sales enablement','Business and marketing plans where genuinely required','Buyer journeys, offers and conversion assets','Special commercial problem-solving']},
 {index:'02 / DESIGN',title:'Design°',subtitle:'Brand & Experience',copy:'Identity, presentation and interaction designed to make value legible before anyone has to explain it.',glow:'#676762',tags:['Brand','UX','Campaigns'],detail:['Brand and identity systems','Campaign and advertising assets','Pitch decks and presentation systems','Interface and customer experience design','Packaging, retail and point-of-sale work']},
 {index:'03 / INTELLIGENCE',title:'Intelligence°',subtitle:'AI & Evidence',copy:'AI, research and structured reasoning turned into useful decisions, assistance and evidence-aware workflows.',glow:'#5e5e59',tags:['AI','Research','Evaluation'],detail:['AI-assisted workflow design','Research and evidence synthesis','Model, prompt and tool-use evaluation','Decision surfaces and intelligent dashboards','Knowledge and support intelligence']},
 {index:'04 / SYSTEMS',title:'Systems°',subtitle:'Software & Automation',copy:'Web, software, APIs, integrations and automation built to remove friction and connect the work.',glow:'#70706a',tags:['Software','APIs','Automation'],detail:['Websites and customer-facing interfaces','APIs and integrations','Workflow and process automation','Internal tools and operational systems','Data validation and decision dashboards']},
 {index:'05 / UTILITY',title:'Utility°',subtitle:'Rapid Problem-Solving',copy:'Focused interventions that prove value quickly: fix, test, automate, prototype, improve.',glow:'#81817a',tags:['Fix','Test','Prototype'],detail:['Micro-audits and targeted fixes','QA and software/API testing','Listing and catalogue refresh','Operational prototypes and proofs of concept','One-problem / one-result delivery sprints']},
 {index:'06 / STUDIOS',title:'Studios°',subtitle:'Film, Media & Worlds',copy:'Narrative, film, vertical series, campaign media and dimensional presentation developed for review or commission.',glow:'#6b443a',tags:['Film','Vertical','Interactive'],detail:['Vertical drama and episodic development','Short-form film and trailer production','Scripts, adaptation and story systems','Visual continuity and production packages','Interactive and dimensional presentation']}
];

const sprints=[
 {index:'FIRST MOVE / 01',title:'Focused Fix',copy:'Resolve one visible defect with a focused correction and a clear acceptance condition.',glow:'#555550',tags:['Fast','Focused'],detail:['Best for a visible website, workflow, document, interface or process defect.','Keep the first move small enough to verify quickly.']},
 {index:'FIRST MOVE / 02',title:'Diagnostic Sprint',copy:'Inspect one surface, rank the highest-value issues, and turn the strongest finding into action.',glow:'#676761',tags:['Audit','Prioritized'],detail:['Website, conversion path, presentation, workflow, data or customer journey.','Evidence first; recommendations second.']},
 {index:'FIRST MOVE / 03',title:'Conversion Asset',copy:'A page, deck, proposal, offer sheet or campaign asset built to move one decision.',glow:'#76766f',tags:['Commercial','Design'],detail:['Useful when presentation or positioning is the bottleneck.','Built around one audience and one next action.']},
 {index:'FIRST MOVE / 04',title:'Workflow Automation',copy:'Remove one repetitive manual step with a working automation that reduces friction immediately.',glow:'#60605b',tags:['Automation','Workflow'],detail:['Start with the repeated action that wastes the most effort.','Extend only after the first automation works.']},
 {index:'FIRST MOVE / 05',title:'Flow Validation',copy:'Test one workflow, API, product path or AI interaction and return concise, actionable evidence.',glow:'#686862',tags:['QA','Evidence'],detail:['Useful for regression, API, UX or AI-evaluation work.','Defects are documented with evidence and acceptance criteria.']},
 {index:'FIRST MOVE / 06',title:'Outcome Prototype',copy:'Build one working proof so the next decision is based on something tangible.',glow:'#74746d',tags:['Prototype','Proof'],detail:['Interactive concept, automation proof, utility surface or production sample.','The next step is earned by the result.']}
];

const studio=[
 {index:'SELECTED PROPERTY',title:'The Dragon Who Could Not Claim Me',subtitle:'Vertical fantasy-romance',copy:'A developed CARBON° Studios vertical property with locked story continuity, canonical cast direction and a controlled buyer-review package.',glow:'#7a3325',visual:'dragon',image:'./assets/studios/dragon-series-poster.png',imageAlt:'The Dragon Who Could Not Claim Me — CARBON° Studios key art',tags:['Vertical','Fantasy romance','Developed property'],detail:['Current public visual uses governed canonical key art.','Buyer-review material and visual-continuity documentation are available in controlled form.','The review package is structured around format, story, visual continuity and commissioning options.'],url:'./work/dragon.html',cta:'View property overview'},
 {index:'EPISODE 01 / RENDERED REVIEW',title:'IT CHOSE HER',subtitle:'The Dragon Who Could Not Claim Me',copy:'A 70-second 9:16 Episode 01 review master is rendered. The moving-picture master remains controlled while final release clearances and the subject-motion upgrade are completed.',glow:'#8b4a31',visual:'dragon',image:'./assets/studios/dragon-ep01-cast.png',imageAlt:'Canonical cast imagery for The Dragon Who Could Not Claim Me',tags:['EP01','70 sec','9:16','Controlled review'],detail:['Episode 01 — IT CHOSE HER.','Rendered review master: 70 seconds, 720×1280, H.264 with burned-in English captions.','CARBON° critic correction passed for safe area, mobile framing, accepted still-pack cast identity, captions, file probe and corrected loudness.','Public video release is not represented as complete; the review master remains controlled.'],url:'./work/dragon.html',cta:'View episode status'},
 {index:'STUDIOS CAPABILITY',title:'Vertical Series Development',subtitle:'Story engine to production package',copy:'Series concepts, episode engines, scripts, visual continuity and production direction built for vertical-native review and commissioning.',glow:'#57423c',visual:'dragon',tags:['Series','9:16','Development'],detail:['Concept and series-engine development','Pilot/sample scripting','Character and visual continuity','Shot, audio and edit direction','Buyer-specific adaptation']},
 {index:'STUDIOS CAPABILITY',title:'Short Film + Trailer',subtitle:'Narrative and campaign production',copy:'Focused story, trailer and short-form packages developed around a clear audience, platform and commercial purpose.',glow:'#4f4f4a',tags:['Film','Trailer','Campaign'],detail:['Creative concept and script','Shot and visual direction','Poster / key-art systems','Audio / edit briefing','Review and delivery packaging']},
 {index:'PRODUCTION QUEUE',title:'Catalogue in production',subtitle:'Materializing from the existing CARBON° backlog',copy:'New properties enter the public slate only as their story, visual, provenance and production state become defensible. The production queue continues behind this surface.',glow:'#484844',tags:['Production active','Governed release'],detail:['Raw ideas do not count as catalogue breadth.','Approved imagery is surfaced as each property or sample becomes defensible.','Internal-only, watermarked or rights-unclear material stays out of the public slate.']}
];

const work=[
 {index:'IRIS / EVIDENCE',title:'IRIS — MiCase',subtitle:'Living case-file interface',copy:'A case-oriented evidence and presentation environment designed around clarity, provenance and review.',glow:'#651f2a',visual:'iris',tags:['Evidence','Case file','Interface'],detail:['Evidence-led presentation','Case structure and provenance','Recruiter and candidate-facing layers','Distinct maroon IRIS identity']},
 {index:'JAM3S / INTELLIGENCE',title:'JAM3S',subtitle:'Spatial intelligence presence',copy:'An intelligence interface language built around layered context, state, topology and responsive presence.',glow:'#7950a8',visual:'jam3s',tags:['Intelligence','Spatial','Interface'],detail:['Layered contextual surfaces','State and signal presentation','Spatial interaction concepts','Distinct JAM3S visual language']},
 {index:'INTERACTIVE + PRODUCT',title:'H0B° unchAIned',subtitle:'Interactive product surface',copy:'An AMX product surface with its own industrial identity, state language and explicit truth labels.',glow:'#b88722',visual:'hobo',tags:['Interactive','Product','Experience'],url:'./work/h0b.html',cta:'View build overview'},
 {index:'SYSTEMS + INTELLIGENCE',title:'AMX Evidence House',subtitle:'Evidence-aware retrieval',copy:'An evidence and workflow system designed to keep claims tied to inspectable sources.',glow:'#595954',tags:['Evidence','Workflow','Systems'],url:'./work/evidence-house.html',cta:'View build overview'},
 {index:'UTILITY + SYSTEMS',title:'ORACL3 Token Preflight',subtitle:'Read-only preflight checks',copy:'A read-only preflight utility designed to check token and network conditions before downstream action.',glow:'#55706c',visual:'oracl3',tags:['API','Preflight','Utility'],url:'./work/oracl3.html',cta:'View build overview'}
];

const $=id=>document.getElementById(id);

function tile(item){
 const el=document.createElement('article');
 el.className='tile'+(item.visual?' visual-'+item.visual:'')+(item.image?' has-art':'');
 el.tabIndex=0; el.setAttribute('role','button');
 const art=item.image?'<img class="tile-art" src="'+item.image+'" alt="'+(item.imageAlt||'')+'" loading="lazy" decoding="async">':'';
 el.innerHTML=art+'<div class="tile-bg" style="--glow:'+item.glow+'"></div><div class="tile-copy"><div class="tile-index">'+item.index+'</div><h3>'+item.title+'</h3>'+(item.subtitle?'<div class="tile-subtitle">'+item.subtitle+'</div>':'')+'<p>'+item.copy+'</p><div class="mini">'+(item.tags||[]).map(x=>'<span>'+x+'</span>').join('')+'</div></div>';
 const open=()=>openDrawer(item);
 el.addEventListener('click',open);
 el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}});
 return el;
}
function fill(id,data){const box=$(id);data.forEach(x=>box.append(tile(x)))}

function openDrawer(item){
 const action=item.url?'<div class="drawer-cta"><a class="button primary" href="'+item.url+'">'+(item.cta||'View overview')+' →</a></div>':'<div class="drawer-cta"><a class="button primary" href="#contact" data-close-drawer>Discuss this capability</a></div>';
 $('drawerBody').innerHTML='<span class="kicker">'+item.index+'</span><h2>'+item.title+'</h2>'+(item.subtitle?'<p class="drawer-subtitle">'+item.subtitle+'</p>':'')+'<p>'+item.copy+'</p>'+(item.detail?'<div class="drawer-list">'+item.detail.map(x=>'<div>'+x+'</div>').join('')+'</div>':'')+action;
 $('drawerBackdrop').hidden=false; $('drawer').classList.add('open'); $('drawer').setAttribute('aria-hidden','false');
 const closeLink=$('drawerBody').querySelector('[data-close-drawer]'); if(closeLink) closeLink.addEventListener('click',closeDrawer);
}
function closeDrawer(){ $('drawer').classList.remove('open'); $('drawer').setAttribute('aria-hidden','true'); setTimeout(()=>{$('drawerBackdrop').hidden=true},220); }

$('drawerClose').addEventListener('click',closeDrawer); $('drawerBackdrop').addEventListener('click',closeDrawer);
document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ closeDrawer(); $('degreeModal').hidden=true; }});
document.querySelector('[data-open="degree"]').addEventListener('click',()=>{$('degreeModal').hidden=false});
document.querySelector('[data-close-modal]').addEventListener('click',()=>{$('degreeModal').hidden=true});
$('degreeModal').addEventListener('click',e=>{if(e.target===$('degreeModal')) $('degreeModal').hidden=true});

fill('degreeRail',degreeData); fill('sprintRail',sprints); fill('studioRail',studio); fill('workRail',work);

/* lightweight 3D interaction */
const stage=$('carbonStage');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if(stage && !reduce){
 const move=(x,y)=>{
   const rx=(.5-y)*8, ry=(x-.5)*10;
   stage.style.transform='rotateX('+rx+'deg) rotateY('+ry+'deg) translateZ(0)';
 };
 stage.closest('.carbon-stage-wrap').addEventListener('pointermove',e=>{
   const r=e.currentTarget.getBoundingClientRect();
   move((e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height);
 });
 stage.closest('.carbon-stage-wrap').addEventListener('pointerleave',()=>{stage.style.transform='rotateX(0deg) rotateY(0deg)'});
}

/* topbar state */
window.addEventListener('scroll',()=>{$('topbar').classList.toggle('compact',window.scrollY>36)},{passive:true});

/* boot */
const boot=$('boot'); const states=['INITIALIZING DEGREE SYSTEM','ALIGNING MATERIAL','CALIBRATING INTERFACE','READY'];
let si=0; const bs=$('bootStatus');
const bootTimer=setInterval(()=>{si=Math.min(si+1,states.length-1);bs.textContent=states[si];},320);
window.addEventListener('load',()=>{setTimeout(()=>{clearInterval(bootTimer);boot.classList.add('out')},1050)});

/* occasional Matrix rain */
const canvas=$('matrixRain');
if(canvas && !reduce){
 const ctx=canvas.getContext('2d',{alpha:true});
 let w=0,h=0,cols=0,drops=[],raf=null,active=false,last=0;
 const glyphs='01°CARBONAMX';
 function resize(){ const d=Math.min(devicePixelRatio||1,2); w=innerWidth; h=innerHeight; canvas.width=w*d; canvas.height=h*d; canvas.style.width=w+'px'; canvas.style.height=h+'px'; ctx.setTransform(d,0,0,d,0,0); cols=Math.ceil(w/20); drops=Array.from({length:cols},()=>Math.random()*-40); }
 function frame(t){
   if(!active){raf=null;return}
   if(t-last>70){ last=t; ctx.fillStyle='rgba(3,3,3,.16)'; ctx.fillRect(0,0,w,h); ctx.font='10px ui-monospace,monospace'; for(let i=0;i<cols;i++){ const ch=glyphs[(Math.random()*glyphs.length)|0]; ctx.fillStyle=Math.random()>.84?'rgba(243,207,173,.5)':'rgba(220,220,212,.28)'; ctx.fillText(ch,i*20,drops[i]*20); if(drops[i]*20>h&&Math.random()>.975)drops[i]=0; drops[i]+=.55;} } raf=requestAnimationFrame(frame);
 }
 function pulse(){ if(active)return; active=true; canvas.classList.add('live'); if(!raf)raf=requestAnimationFrame(frame); setTimeout(()=>{canvas.classList.remove('live');setTimeout(()=>{active=false;ctx.clearRect(0,0,w,h)},1100)},2400); }
 resize(); addEventListener('resize',resize,{passive:true}); setTimeout(pulse,1800); setInterval(pulse,13000);
}
})();