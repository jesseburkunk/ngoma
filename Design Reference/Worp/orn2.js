/* Worp skin: button surround variants. window.WORN = 'bare' | 'dots' | 'scale' | 'leaves4' | 'rosette' | 'well' */
window.wornSVG=function(v){
  const c=200,P=(r,a)=>[c+r*Math.cos(a),c+r*Math.sin(a)].map(x=>x.toFixed(1));
  const leaf=(a,r1,r2,w)=>{const m=(r1+r2)/2,p1=P(r1,a),p2=P(r2,a),q1=P(m,a-w),q2=P(m,a+w);return `M${p1} Q${q1} ${p2} Q${q2} ${p1} Z`};
  let g='',f='';
  if(v==='dots'){g+=`<circle cx="200" cy="200" r="158" stroke-width=".8" opacity=".7"/>`;
    for(let i=0;i<8;i++){const p=P(172,i/8*Math.PI*2-Math.PI/2);f+=`<circle cx="${p[0]}" cy="${p[1]}" r="${i%2?1.8:3}"/>`}}
  if(v==='scale'){for(let i=0;i<48;i++){const a=i/48*Math.PI*2-Math.PI/2,big=i%6===0;const p1=P(160,a),p2=P(big?178:168,a);g+=`<path d="M${p1} L${p2}" stroke-width="${big?1.1:.6}" opacity="${big?.9:.55}"/>`}
    g+=`<circle cx="200" cy="200" r="184" stroke-width=".5" opacity=".45"/>`}
  if(v==='leaves4'){g+=`<circle cx="200" cy="200" r="158" stroke-width=".8" opacity=".6"/>`;
    for(let i=0;i<4;i++){const a=i/4*Math.PI*2-Math.PI/2;g+=`<path d="${leaf(a,162,196,.1)}" stroke-width=".9"/><path d="M${P(166,a)} L${P(190,a)}" stroke-width=".6"/>`;
      [-.13,.13].forEach(o=>{const p=P(168,a+o);f+=`<circle cx="${p[0]}" cy="${p[1]}" r="1.6"/>`})}}
  if(v==='rosette'){let r='';for(let i=0;i<12;i++){const a=i/12*Math.PI*2;r+=`<circle cx="${(c+64*Math.cos(a)).toFixed(1)}" cy="${(c+64*Math.sin(a)).toFixed(1)}" r="100"/>`}
    g+=`<g class="ros" stroke-width=".5" opacity=".45">${r}</g><circle cx="200" cy="200" r="168" stroke-width=".8" opacity=".7"/>`}
  if(v==='well'){g+=`<circle cx="200" cy="200" r="150" stroke-width="1" opacity=".6"/>`}
  return `<svg class="worn" viewBox="0 0 400 400" aria-hidden="true"><g fill="none" stroke="currentColor">${g}</g><g fill="currentColor">${f}</g></svg>`;
};
(function(){const w=document.querySelector('.ringwrap');if(!w)return;w.querySelector('.worn')?.remove();w.insertAdjacentHTML('afterbegin',wornSVG(window.WORN||'dots'));
  document.body.dataset.worn=window.WORN||'dots';
  const fill=el=>{const mn=+el.min||0,mx=+el.max||1;el.style.setProperty('--v',((+el.value-mn)/(mx-mn)*100).toFixed(1)+'%')};
  const all=()=>document.querySelectorAll('input[type=range]').forEach(fill);
  document.addEventListener('input',e=>{if(e.target.type==='range')fill(e.target)},true);all();setInterval(all,500)})();
