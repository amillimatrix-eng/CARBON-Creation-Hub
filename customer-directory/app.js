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
 {index:'FIRST MOVE / 01',title:'Fix One Thing',copy:'One visible defect. One focused correction. One clear definition of done.',glow:'#555550',tags:['Fast','Focused'],detail:['Best for a visible website, workflow, document, interface or process defect.','Keep the first move small enough to verify quickly.']},
 {index:'FIRST MOVE / 02',title:'Audit + Priorities',copy:'Inspect one surface, rank what matters, and turn the strongest finding into action.',glow:'#676761',tags:['Audit','Prioritized'],detail:['Website, conversion path, presentation, workflow, data or customer journey.','Evidence first; recommendations second.']},
 {index:'FIRST MOVE / 03',title:'One Conversion Asset',copy:'A page, deck, proposal, offer sheet or campaign asset built to move one decision.',glow:'#76766f',tags:['Commercial','Design'],detail:['Useful when presentation or positioning is the bottleneck.','Built around one audience and one next action.']},
 {index:'FIRST MOVE / 04',title:'Automate One Task',copy:'Remove one repetitive manual step without turning the buyer into an IT project.',glow:'#60605b',tags:['Automation','Workflow'],detail:['Start with the repeated action that wastes the most effort.','Extend only after the first automation works.']},
 {index:'FIRST MOVE / 05',title:'Test One Flow',copy:'QA one workflow, API, product path or AI interaction and return concise evidence.',glow:'#686862',tags:['QA','Evidence'],detail:['Useful for regression, API, UX or AI-evaluation work.','Defects are documented with evidence and acceptance criteria.']},
 {index:'FIRST MOVE / 06',title:'Prototype One Outcome',copy:'Make one working proof so the next decision is based on something real.',glow:'#74746d',tags:['Prototype','Proof'],detail:['Interactive concept, automation proof, utility surface or production sample.','The next step is earned by the result.']}
];

const studio=[
 {index:'SELECTED PROPERTY',title:'The Dragon Who Could Not Claim Me',subtitle:'Vertical fantasy-romance',copy:'A CARBON° Studios property with a controlled buyer-review package, 9:16 vertical format and commissioned-development route.',glow:'#7a3325',tags:['Vertical','Fantasy romance','Private review'],detail:['Buyer-review material and visual-continuity documentation are available in controlled form.','The review package is structured around format, story, visual continuity and commissioning options.'],url:'./work/dragon.html',cta:'View property overview'},
 {index:'STUDIOS CAPABILITY',title:'Vertical Series Development',subtitle:'Story engine to production package',copy:'Series concepts, episode engines, scripts, visual continuity and production direction built for vertical-native review and commissioning.',glow:'#57423c',tags:['Series','9:16','Development'],detail:['Concept and series-engine development','Pilot/sample scripting','Character and visual continuity','Shot, audio and edit direction','Buyer-specific adaptation']},
 {index:'STUDIOS CAPABILITY',title:'Short Film + Trailer',subtitle:'Narrative and campaign production',copy:'Focused story, trailer and short-form packages developed around a clear audience, platform and commercial purpose.',glow:'#4f4f4a',tags:['Film','Trailer','Campaign'],detail:['Creative concept and script','Shot and visual direction','Poster / key-art systems','Audio / edit briefing','Review and delivery packaging']},
 {index:'PRIVATE SLATE',title:'More titles are moving through CARBON° Studios',subtitle:'Buyer review by request',copy:'The public slate will expand as buyer-ready packages are completed. Private review can be arranged for relevant material before public release.',glow:'#484844',tags:['Private review','Commissioning'],detail:['Additional story development is active across multiple formats and genres.','Public breadth will reflect finished buyer packages, not idea counts.']}
];

const work=[
 {index:'SYSTEMS + INTELLIGENCE',title:'AMX Evidence House',subtitle:'Evidence-aware retrieval',copy:'A provider-neutral evidence and workflow system designed to keep claims tied to inspectable sources.',glow:'#595954',tags:['Evidence','Workflow','Systems'],url:'./work/evidence-house.html',cta:'View build overview'},
 {index:'UTILITY + SYSTEMS',title:'ORACL3 Token Preflight',subtitle:'Read-only preflight checks',copy:'A read-only preflight utility designed to check token and network conditions before downstream action.',glow:'#65655f',tags:['API','Preflight','Utility'],url:'./work/oracl3.html',cta:'View build overview'},
 {index:'INTERACTIVE + PRODUCT',title:'H0B° unchAIned',subtitle:'Interactive product surface',copy:'An interactive AMX surface built around state, presentation and explicit truth labels.',glow:'#4e4e49',tags:['Interactive','Product','Experience'],url:'./work/hob.html',cta:'View build overview'}
];

const $=id=>document.getElementById(id);

function tile(item){
 const el=document.createElement('article');
 el.className='tile';
 el.tabIndex=0;
 el.setAttribute('role','button');
 el.innerHTML=
   '<div class="tile-bg" style="--glow:'+item.glow+'"></div>'+
   '<div class="tile-copy">'+
   '<div class="tile-index">'+item.index+'</div>'+
   '<h3>'+item.title+'</h3>'+
   (item.subtitle?'<div class="tile-subtitle">'+item.subtitle+'</div>':'')+
   '<p>'+item.copy+'</p>'+
   '<div class="mini">'+(item.tags||[]).map(x=>'<span>'+x+'</span>').join('')+'</div>'+
   '</div>';
 const open=()=>openDrawer(item);
 el.addEventListener('click',open);
 el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}});
 return el;
}
function fill(id,data){const box=$(id);data.forEach(x=>box.append(tile(x)))}

function openDrawer(item){
 const action=item.url
   ? '<div class="drawer-cta"><a class="button primary" href="'+item.url+'">'+(item.cta||'View overview')+' →</a></div>'
   : '<div class="drawer-cta"><a class="button primary" href="#contact" data-close-drawer>Discuss this capability</a></div>';

 $('drawerBody').innerHTML=
   '<span class="kicker">'+item.index+'</span>'+
   '<h2>'+item.title+'</h2>'+
   (item.subtitle?'<p class="drawer-subtitle">'+item.subtitle+'</p>':'')+
   '<p>'+item.copy+'</p>'+
   (item.detail?'<div class="drawer-list">'+item.detail.map(x=>'<div>'+x+'</div>').join('')+'</div>':'')+
   action;

 $('drawerBackdrop').hidden=false;
 $('drawer').classList.add('open');
 $('drawer').setAttribute('aria-hidden','false');
 const closeLink=$('drawerBody').querySelector('[data-close-drawer]');
 if(closeLink) closeLink.addEventListener('click',closeDrawer);
}

function closeDrawer(){
 $('drawer').classList.remove('open');
 $('drawer').setAttribute('aria-hidden','true');
 setTimeout(()=>{$('drawerBackdrop').hidden=true},220);
}

$('drawerClose').addEventListener('click',closeDrawer);
$('drawerBackdrop').addEventListener('click',closeDrawer);
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){
  closeDrawer();
  $('degreeModal').hidden=true;
 }
});
document.querySelector('[data-open="degree"]').addEventListener('click',()=>{$('degreeModal').hidden=false});
document.querySelector('[data-close-modal]').addEventListener('click',()=>{$('degreeModal').hidden=true});
$('degreeModal').addEventListener('click',e=>{if(e.target===$('degreeModal')) $('degreeModal').hidden=true});

fill('degreeRail',degreeData);
fill('sprintRail',sprints);
fill('studioRail',studio);
fill('workRail',work);
})();