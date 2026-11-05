// ---------- add-on (2 Nov 2026): "What if?" switches (explore mode) and guess-first questions (outbreak mode)
(function(){
const KN=/kannada/.test(location.pathname);
const T=KN?{
 wiH:'ಹೀಗಾದರೆ ಏನು?',
 wiP:'ಒಂದನ್ನು ಆರಿಸಿ, ಯಾವ ಪೀಡೆ ಕೀಟಗಳನ್ನು ಬೇಟೆಯಾಡುವ ಮಿತ್ರ ಜೀವಿಗಳು ಈ ಜಾಲದಲ್ಲಿ ಇಲ್ಲವಾಗುತ್ತವೆ ಎಂದು ನೋಡಿ.',
 spray:'ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಿದರೆ',noshade:'ನಾಟಿ ನೆರಳು ಮರಗಳನ್ನು ಕಡಿದರೆ',nobirds:'ಕೀಟ ತಿನ್ನುವ ಹಕ್ಕಿಗಳು ಇಲ್ಲದಿದ್ದರೆ',
 removed:n=>`ಜಾಲದಿಂದ ಹೋದ ಜೀವಿಗಳು: ${n} (ಅಡ್ಡಗೆರೆ ಹಾಕಿದವು).`,
 none:'ಬೇಟೆಯಾಡುವ ಮಿತ್ರ ಜೀವಿ ಒಂದೂ ಉಳಿಯದ ಪೀಡೆಗಳು',few:'ಬೇಟೆಯಾಡುವ ಮಿತ್ರ ಜೀವಿಗಳು ಕಡಿಮೆಯಾದ ಪೀಡೆಗಳು',
 left:(a,b)=>a==0?`${b}ರಲ್ಲಿ ಒಂದೂ ಉಳಿದಿಲ್ಲ`:`${b}ರಲ್ಲಿ ${a} ಉಳಿದಿ${a==1?'ದೆ':'ವೆ'}`,
 hungry:'ಈ ಜಾಲದಲ್ಲಿ ತಮ್ಮ ಆಹಾರದ ಅರ್ಧಕ್ಕಿಂತ ಹೆಚ್ಚನ್ನು ಕಳೆದುಕೊಳ್ಳುವ ಜೀವಿಗಳು',
 shadeDep:a=>`ನೆರಳು ಮರಗಳೊಂದಿಗೆ ಅವುಗಳನ್ನೇ ಅವಲಂಬಿಸಿರುವ ಜೀವಿಗಳೂ ಹೋಗುತ್ತವೆ: ಹೆಚ್ಚಿನ ಹಣ್ಣು ತಿನ್ನುವ ಹಕ್ಕಿಗಳು, ಕಾಡಿನ ಕೀಟ ತಿನ್ನುವ ಹಕ್ಕಿಗಳು, ಮತ್ತು ಮರಗಳ ಮೇಲೆ ಹಾಗೂ ಕಾಡಿನ ನೆಲದ ಮೇಲೆ ವಾಸಿಸುವ ಕಪ್ಪೆಗಳು. ${a.join(', ')} ಮುಂತಾದ ಬಯಲಿನ ಹಕ್ಕಿಗಳು ಉಳಿಯುತ್ತವೆ.`,
 shadeNote:'ಕಾಂಡ ಕೊರಕದ ವಿರುದ್ಧ ನೆರಳೇ ಮುಖ್ಯ ರಕ್ಷಣೆ; ನೆರಳು ಮರಗಳನ್ನು ಕಡಿದರೆ ಅದು ಹೋಗುತ್ತದೆ.',
 nothing:'ಪೀಡೆಗಳನ್ನು ಬೇಟೆಯಾಡುವ ಮಿತ್ರ ಜೀವಿಗಳಲ್ಲಿ ಯಾವುದೂ ಈ ಜಾಲದಲ್ಲಿ ಇಲ್ಲವಾಗುವುದಿಲ್ಲ.',
 caveat:'ಇದು ಇಲ್ಲಿ ತೋರಿಸಿರುವ ಸಂಬಂಧಗಳನ್ನು ಮಾತ್ರ ಎಣಿಸುತ್ತದೆ. ನಿಜವಾದ ತೋಟದಲ್ಲಿ ಇನ್ನೂ ಹೆಚ್ಚು ಜೀವಿಗಳು ಮತ್ತು ಸಂಬಂಧಗಳಿವೆ; ಆದ್ದರಿಂದ ಇದು ಬದಲಾವಣೆಯ ದಿಕ್ಕನ್ನು ತೋರಿಸುತ್ತದೆ, ಎಷ್ಟು ಎಂದಲ್ಲ.',
 clearBtn:'ಎಲ್ಲ ತೆಗೆಯಿರಿ',
 qH:'ಮೊದಲು ಊಹಿಸಿ',skip:'ಪ್ರಶ್ನೆ ಬಿಟ್ಟು ಮುಂದುವರಿಯಿರಿ',right:'ಸರಿ!',wrong:'ಅಲ್ಲ.',ans:'ಉತ್ತರ:',
 play:'ಈಗ ▶ ಒತ್ತಿ ಅದು ಹೇಗೆ ನಡೆಯುತ್ತದೆ ಎಂದು ನೋಡಿ.',again:'ಮತ್ತೆ ಉತ್ತರಿಸಿ'
}:{
 wiH:'What if…?',
 wiP:'Switch something off and see which pests lose their natural enemies on this web.',
 spray:'we sprayed insecticide',noshade:'we cut the native shade trees',nobirds:'the insect-eating birds were gone',
 removed:n=>`Gone from the web: ${n} species (crossed out).`,
 none:'Pests left with no natural enemies here',few:'Pests with fewer natural enemies',
 left:(a,b)=>`${a} of ${b} left`,
 hungry:'Species that lose more than half their food on this web',
 shadeDep:a=>`The birds and frogs that need the canopy go with it: most fruit-eating birds, the forest insect-eaters, and the canopy and forest-floor frogs. Birds of open country, such as ${a.join(', ')}, stay.`,
 shadeNote:'Shade is the main defence against the white stem borer; cutting the shade trees removes it.',
 nothing:'No pest loses any of its enemies on this web.',
 caveat:'This counts only the links drawn here. A real plantation has more species and links, so it shows the direction of change, not its size.',
 clearBtn:'Clear all',
 qH:'Guess first',skip:'Skip the question',right:'Right!',wrong:'Not quite.',ans:'The answer:',
 play:'Now press ▶ Play to watch it happen.',again:'Answer again'
};
const css=document.createElement('style');
css.textContent=`.egfw .wi{margin-top:16px;padding:12px 14px;border:1px solid var(--line,rgba(207,220,207,.2));border-radius:10px}
.egfw .wi h3{margin:0 0 4px;font-size:18px}.egfw .wi p{margin:4px 0}
.egfw .wi label{display:flex;gap:8px;align-items:center;margin:6px 0;cursor:pointer;font-size:15px}
.egfw .wi input{width:18px;height:18px;accent-color:var(--pred,#e8653c)}
.egfw .wires{margin-top:8px;font-size:14.5px}.egfw .wires ul{margin:4px 0 8px;padding-left:18px}
.egfw .wires b{font-weight:600}.egfw .wi .note{font-size:13px;opacity:.8}
.egfw .wi .wiclr{background:none;border:0;color:inherit;text-decoration:underline;cursor:pointer;padding:0;font-size:13px;opacity:.85}
.egfw .node.wi-bad .ph{box-shadow:0 0 0 3px var(--pred,#e8653c)!important}
.egfw .node.wi-few .ph{box-shadow:0 0 0 3px #e0b04a!important}
.egfw .node.wi-hungry .ph{box-shadow:0 0 0 2px #e0b04a!important;outline:2px dashed #e0b04a;outline-offset:3px}
.egfw .node .badge.wib{background:var(--pred,#e8653c);color:#fff}
.egfw .gq{margin:12px 0;padding:12px 14px;border:1px solid var(--accent,#e8653c);border-radius:10px}
.egfw .gq h3{margin:0 0 6px;font-size:16px;text-transform:uppercase;letter-spacing:.06em;opacity:.85}
.egfw .gq p.q{margin:0 0 8px;font-weight:600}
.egfw .gq .opts{display:flex;flex-direction:column;gap:6px}
.egfw .gq .opts button{text-align:left;padding:9px 12px;border-radius:8px;border:1px solid var(--line,rgba(207,220,207,.25));background:transparent;color:inherit;font:inherit;font-size:15px;cursor:pointer;line-height:1.35}
.egfw .gq .opts button:hover{border-color:var(--accent,#e8653c)}
.egfw .gq .opts button.ok{border-color:#7cc495;background:rgba(124,196,149,.14)}
.egfw .gq .opts button.no{border-color:var(--pred,#e8653c);background:rgba(232,101,60,.12)}
.egfw .gq .fb{margin-top:8px;font-size:14.5px}.egfw .gq .lk{background:none;border:0;color:inherit;text-decoration:underline;cursor:pointer;padding:0;font-size:13px;opacity:.85;margin-top:6px}
.egfw .gqlock{opacity:.4;pointer-events:none}`;
document.head.appendChild(css);

// ----- 1. What if?
const WI={spray:false,noshade:false,nobirds:false};
const PESTS=['cbb','wsb','scale','rats'].concat(SCEN.cat.focus).filter(p=>byId[p]);
const BIRDS=N.filter(n=>n[3]==='t2').map(n=>n[0]);
// species that need the native canopy: most fruit-eating birds, forest insect-eaters, canopy and forest-floor frogs
const SHADEDEP=['barbet','bluebird','starling','sqbulbul','oriole','parrot','trogon','leafbird','blackbird','malglide','winged','dotfrog'].filter(x=>byId[x]);
function removedSet(){const r=new Set();if(WI.spray)SPRAYKILL.forEach(x=>r.add(x));if(WI.noshade){(G.trees||[]).forEach(x=>r.add(x));SHADEDEP.forEach(x=>r.add(x))}if(WI.nobirds)BIRDS.forEach(x=>r.add(x));return r}
function wiCalc(){const R=removedSet();const res={R,none:[],few:[],hungry:[]};if(!R.size)return res;
PESTS.forEach(p=>{if(R.has(p))return;const en=predsOf([p]);const left=en.filter(x=>!R.has(x));if(!en.length)return;if(!left.length)res.none.push([p,0,en.length]);else if(left.length<en.length)res.few.push([p,left.length,en.length])});
Object.keys(byId).forEach(a=>{if(R.has(a)||PESTS.includes(a))return;const food=[...new Set(E.filter(e=>e.a===a&&(e.type==='eats'||e.type==='feeds')).map(e=>e.b))];if(food.length<2)return;const lost=food.filter(b=>R.has(b)).length;if(lost*2>food.length)res.hungry.push(a)});
return res}
function wiMark(){if(mode!=='explore')return;const r=wiCalc();if(!r.R.size)return;
r.R.forEach(x=>el[x]&&el[x].classList.add('killed'));
r.none.forEach(([p,a,b])=>{el[p].classList.add('wi-bad');const s=document.createElement('span');s.className='badge wib';s.textContent=a+'/'+b;el[p].appendChild(s)});
r.few.forEach(([p,a,b])=>{el[p].classList.add('wi-few');const s=document.createElement('span');s.className='badge';s.textContent=a+'/'+b;el[p].appendChild(s)});
r.hungry.forEach(a=>el[a]&&el[a].classList.add('wi-hungry'))}
const nm=id=>`<button data-go="${id}">${byId[id].name}</button>`;
function wiResults(){const r=wiCalc();if(!r.R.size)return '';let h=`<p>${T.removed(r.R.size)}</p>`;
if(r.none.length)h+=`<p><b>${T.none}</b></p><ul>${r.none.map(([p,a,b])=>`<li>${nm(p)} (${T.left(a,b)})</li>`).join('')}</ul>`;
if(r.few.length)h+=`<p><b>${T.few}</b></p><ul>${r.few.map(([p,a,b])=>`<li>${nm(p)} (${T.left(a,b)})</li>`).join('')}</ul>`;
if(WI.noshade)h+=`<p>${T.shadeDep(['drongo','gbee','rvbulbul'].filter(x=>byId[x]).map(x=>byId[x].name))}</p>`;
if(WI.noshade&&byId.wsb)h+=`<p>${T.shadeNote}</p>`;
if(!r.none.length&&!r.few.length)h+=`<p>${T.nothing}</p>`;
if(r.hungry.length)h+=`<p><b>${T.hungry}</b></p><p>${r.hungry.map(nm).join(', ')}</p>`;
return h}
function wiBox(){return `<div class="wi"><h3>${T.wiH}</h3><p class="empty">${T.wiP}</p>
${['spray','noshade','nobirds'].map(k=>`<label><input type="checkbox" data-wi="${k}" ${WI[k]?'checked':''}>…${T[k]}</label>`).join('')}
<div class="wires" aria-live="polite">${wiResults()}</div>
${Object.values(WI).some(Boolean)?`<button class="wiclr" type="button">${T.clearBtn}</button>`:''}
<p class="note">${T.caveat}</p></div>`}
function wiBind(){panel.querySelectorAll('[data-wi]').forEach(c=>c.onchange=()=>{WI[c.dataset.wi]=c.checked;clear();intro()});
const cl=panel.querySelector('.wiclr');if(cl)cl.onclick=()=>{Object.keys(WI).forEach(k=>WI[k]=false);clear();intro()};
panel.querySelectorAll('.wi [data-go]').forEach(b=>b.onclick=()=>select(b.dataset.go))}
const _clear=clear;clear=function(){_clear();wiMark()};
const _intro=intro;intro=function(){_intro();if(VAR==='web'){panel.insertAdjacentHTML('beforeend',wiBox());wiBind()}};

// ----- 2. Guess first (outbreak mode)
const Q=KN?{
cat:['ಮೊದಲ ಮಳೆಯ ನಂತರ ನೆರಳು ಮರಗಳ ಮೇಲೆ ಕಂಬಳಿಹುಳುಗಳು ತುಂಬಿಕೊಂಡಿವೆ. ನೀವು ಏನೂ ಮಾಡದಿದ್ದರೆ ಹೆಚ್ಚಾಗಿ ಏನಾಗುತ್ತದೆ?',
 ['ಮರಗಳ ಮತ್ತು ಕಾಫಿಯ ಎಲೆಗಳನ್ನೆಲ್ಲ ತಿನ್ನುವವರೆಗೆ ಅವು ಹೆಚ್ಚುತ್ತಲೇ ಇರುತ್ತವೆ.','ಕಣಜಗಳು, ಒಂಟೆಹುಳುಗಳು, ಇರುವೆಗಳು, ಕಪ್ಪೆಗಳು, ಜೇಡಗಳು ಮತ್ತು ಹಕ್ಕಿಗಳು ಬಂದು, ಸಂಖ್ಯೆ ಮತ್ತೆ ಹತೋಟಿಗೆ ಬರುತ್ತದೆ.','ಅವನ್ನು ಯಾವುದೂ ತಿನ್ನುವುದಿಲ್ಲ, ಎಲೆಗಳು ಮುಗಿದಾಗ ಮಾತ್ರ ನಿಲ್ಲುತ್ತವೆ.'],1,
 'ಕಂಬಳಿಹುಳುಗಳ ಹಾವಳಿಗೆ ಹಲವು ಬೇಟೆಗಾರ ಜೀವಿಗಳು ಒಟ್ಟಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತವೆ; ಪ್ರತಿಯೊಂದೂ ಗಿಡದ ಬೇರೆ ಭಾಗದಲ್ಲಿ, ಬೇರೆ ಸಮಯದಲ್ಲಿ ಬೇಟೆಯಾಡುತ್ತದೆ [1]. ಕೀಟನಾಶಕ ಈ ಬೇಟೆಗಾರರನ್ನೂ ಕೊಲ್ಲುತ್ತದೆ, ಆಗ ಕಂಬಳಿಹುಳುಗಳು ಹಲವು ಸಲ ಮೊದಲಿಗಿಂತ ಹೆಚ್ಚು ಸಂಖ್ಯೆಯಲ್ಲಿ ಮರಳಿ ಬರುತ್ತವೆ [11].'],
cbb:['ಕಾಫಿ ಕಾಯಿ ಕೊರಕ ನಿಮ್ಮ ಕಾಫಿ ಕಾಯಿಗಳಲ್ಲಿದೆ. ವರ್ಷದಿಂದ ವರ್ಷಕ್ಕೆ ಅದನ್ನು ಕಡಿಮೆ ಇಡಲು ಯಾವುದು ಹೆಚ್ಚು ನೆರವಾಗುತ್ತದೆ?',
 ['ನೆರಳು ಮರಗಳನ್ನು ಉಳಿಸುವುದು, ಆಗ ಇರುವೆಗಳು ಮತ್ತು ಕೀಟ ತಿನ್ನುವ ಹಕ್ಕಿಗಳು ತೋಟದಲ್ಲೇ ಉಳಿಯುತ್ತವೆ.','ನಿಯಮಿತವಾಗಿ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವುದು.','ಏನೂ ಮಾಡಲಾಗದು: ಯಾವ ಪ್ರಾಣಿಯೂ ಕೊರಕವನ್ನು ತಿನ್ನುವುದಿಲ್ಲ.'],0,
 'ಇರುವೆಗಳು ಹೊರಗೆ ಓಡಾಡುವ ಕೊರಕಗಳನ್ನು ಹಿಡಿಯುತ್ತವೆ [2], ಮತ್ತು ಜಮೈಕಾ ಹಾಗೂ ಕೋಸ್ಟರಿಕಾದ ತೋಟಗಳಲ್ಲಿ ಕೀಟ ತಿನ್ನುವ ಹಕ್ಕಿಗಳು ಕೊರಕದ ಹಾನಿಯನ್ನು ಕಡಿಮೆ ಮಾಡಿದವು [5, 6]. ಕೊರಕ ತನ್ನ ಜೀವನದ ಹೆಚ್ಚಿನ ಭಾಗ ಕಾಯಿಯೊಳಗೇ ಇರುತ್ತದೆ, ಅಲ್ಲಿಗೆ ಸಿಂಪಡಣೆ ತಲುಪುವುದಿಲ್ಲ; ಮತ್ತು ಸಿಂಪಡಣೆ ಅದನ್ನು ಬೇಟೆಯಾಡುವ ಇರುವೆಗಳನ್ನು ಕೊಲ್ಲುತ್ತದೆ [11].'],
scale:['ಎಳೆ ಚಿಗುರುಗಳ ಮೇಲೆ ಹಸಿರು ಸ್ಕೇಲ್ ಕೀಟ (Coccus viridis) ಹರಡುತ್ತಿದೆ. ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಿದ ನಂತರ ಹೆಚ್ಚಾಗಿ ಏನಾಗುತ್ತದೆ?',
 ['ಸ್ಕೇಲ್ ಶಾಶ್ವತವಾಗಿ ನಾಶವಾಗುತ್ತದೆ.','ಏನೂ ಬದಲಾಗುವುದಿಲ್ಲ.','ಸ್ಕೇಲ್ ಹಲವು ಸಲ ಮೊದಲಿಗಿಂತ ಹೆಚ್ಚು ಸಂಖ್ಯೆಯಲ್ಲಿ ಮರಳಿ ಬರುತ್ತದೆ, ಏಕೆಂದರೆ ಸಿಂಪಡಣೆ ಸ್ಕೇಲ್‌ಗಿಂತ ಸುಲಭವಾಗಿ ಒಡತಿಜೀರುಂಡೆಗಳನ್ನು ಮತ್ತು ಪರಾವಲಂಬಿ ಕಣಜಗಳನ್ನು ಕೊಲ್ಲುತ್ತದೆ.'],2,
 'ಒಡತಿಜೀರುಂಡೆಗಳು ಸ್ಕೇಲ್ ತಿನ್ನುತ್ತವೆ, ಪರಾವಲಂಬಿ ಕಣಜಗಳು ಅವುಗಳೊಳಗೆ ಮೊಟ್ಟೆ ಇಡುತ್ತವೆ, ಮತ್ತು ತೇವದ ಹವಾಮಾನದಲ್ಲಿ ಬಿಳಿ ಶಿಲೀಂಧ್ರ (ಬೂಷ್ಟು) ಇಡೀ ಗುಂಪುಗಳನ್ನು ನಾಶಮಾಡಬಹುದು [1]. ಮೇಣದ ಕವಚದ ಕೆಳಗಿರುವ ಸ್ಕೇಲ್‌ಗಿಂತ ಈ ಮಿತ್ರ ಜೀವಿಗಳು ಸಿಂಪಡಣೆಯಿಂದ ಸುಲಭವಾಗಿ ಸಾಯುತ್ತವೆ, ಆದ್ದರಿಂದ ಸಿಂಪಡಣೆಯ ನಂತರ ಸ್ಕೇಲ್ ಹಾವಳಿ ಹೆಚ್ಚಾಗಿ ಬರುತ್ತದೆ [11].'],
wsb:['ಕಾಂಡ ಕೊರಕದ ವಿರುದ್ಧ ಮುಖ್ಯ ರಕ್ಷಣೆ ಯಾವುದು?',
 ['ಕಾಂಡದೊಳಗಿನ ಹುಳುಗಳಿಗೆ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವುದು.','ಎರಡು ಹಂತದ ನೆರಳು, ಏಕೆಂದರೆ ಜೀರುಂಡೆಗಳು ಬಿಸಿಲಿನಲ್ಲಿರುವ ಕಾಫಿಯ ಮೇಲೆ ಮೊಟ್ಟೆ ಇಡಲು ಇಷ್ಟಪಡುತ್ತವೆ.','ಬೆಳಕು ಬರಲು ಮರಗಳ ಹೊದಿಕೆಯನ್ನು ತೆಳುವಾಗಿಸುವುದು.'],1,
 'ಹೆಣ್ಣು ಜೀರುಂಡೆಗಳು ಬಿಸಿಲಿನ ಕಾಫಿಯ ಮೇಲೆ ಮೊಟ್ಟೆ ಇಡಲು ಇಷ್ಟಪಡುತ್ತವೆ, ಆದ್ದರಿಂದ ಎರಡು ಹಂತದ ನೆರಳು ಮುಖ್ಯ ರಕ್ಷಣೆ; ಮರಗಳ ಹೊದಿಕೆಯನ್ನು ತೆಳುವಾಗಿಸಿದರೆ ಸಮಸ್ಯೆ ಹೆಚ್ಚಾಗುತ್ತದೆ [8]. ಕಾಂಡದೊಳಗಿನ ಹುಳುಗಳಿಗೆ ಸಿಂಪಡಣೆ ತಲುಪುವುದಿಲ್ಲ [18].']
}:{
cat:['After the first rains, caterpillars swarm over the shade trees. If you do nothing, what is most likely?',
 ['They keep multiplying until they strip the trees and the coffee.','Wasps, mantises, ants, frogs, spiders and birds move in, and numbers settle again.','Nothing eats them, so they stop only when the leaves run out.'],1,
 'Many hunters answer a caterpillar boom together, each working a different part of the plant at a different time [1]. A pesticide kills those hunters too, and caterpillars then often come back in greater numbers than before [11].'],
cbb:['Coffee berry borer is in your berries. What helps most to keep it down year after year?',
 ['Keeping the shade trees, so ants and insect-eating birds stay on the plantation.','Spraying insecticide regularly.','Nothing: no animal eats the borer.'],0,
 'Ants catch adult borers in the open [2], and insect-eating birds cut borer damage on farms in Jamaica and Costa Rica [5, 6]. The borer spends most of its life inside the berry, out of reach of sprays, and sprays kill the ants that hunt it [11].'],
scale:['Green scale is spreading on the young shoots. What often happens after an insecticide spray?',
 ['The scale is wiped out for good.','Nothing changes either way.','The scale often comes back worse, because the spray kills lady beetles and parasitic wasps more easily than the scale.'],2,
 'Lady beetles eat scale, parasitic wasps lay eggs inside it, and in wet weather a white fungus can wipe out whole colonies [1]. These enemies die from sprays more easily than scale sheltering under its waxy cover, so outbreaks often follow spraying [11].'],
wsb:['What is the main defence against the white stem borer?',
 ['Spraying the grubs inside the stems.','Two tiers of shade, because the beetles prefer to lay eggs on coffee in the sun.','Thinning the canopy to let in more light.'],1,
 'Female beetles prefer to lay eggs on coffee in the sun, so two tiers of shade are the key defence, and thinning the canopy makes things worse [8]. Grubs inside the stem are out of reach of sprays [18].']
};
const ANS={};
const _render=renderScen;renderScen=function(anim){_render(anim);const q=Q[scen];if(!q||step!==0)return;
const a=ANS[scen];const chips=panel.querySelector('.chips');if(!chips)return;
const box=document.createElement('div');box.className='gq';
box.innerHTML=`<h3>${T.qH}</h3><p class="q">${q[0]}</p><div class="opts">${q[1].map((o,i)=>`<button type="button" data-q="${i}" class="${a==null||a==='skip'?'':(i===q[2]?'ok':(i===a?'no':''))}">${o}</button>`).join('')}</div>`+
(a==null?`<button type="button" class="lk" data-skip>${T.skip}</button>`:(a==='skip'?'':`<p class="fb"><b>${a===q[2]?T.right:T.wrong}</b> ${a===q[2]?'':T.ans+' '+q[1][q[2]].replace(/[.।]$/,'')+'. '}${q[3]}</p><p class="fb">${T.play}</p><button type="button" class="lk" data-again>${T.again}</button>`));
chips.insertAdjacentElement('afterend',box);
if(a==null){['.playrow','.stepnav'].forEach(s=>panel.querySelector(s)?.classList.add('gqlock'));stopPlay()}
box.querySelectorAll('[data-q]').forEach(b=>b.onclick=()=>{if(ANS[scen]!=null&&ANS[scen]!=='skip')return;ANS[scen]=+b.dataset.q;renderScen(false);panel.querySelector('.gq .fb')?.scrollIntoView({block:'nearest'})});
box.querySelector('[data-skip]')?.addEventListener('click',()=>{ANS[scen]='skip';renderScen(false)});
box.querySelector('[data-again]')?.addEventListener('click',()=>{delete ANS[scen];renderScen(false)})};
})();
