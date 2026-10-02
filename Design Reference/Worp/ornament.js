/* Worp skin: the etched ornament behind the NEW button (gold linework on black, after Folktek's Alter), and --v on every slider for the lit part */
(function(){
  const NS='http://www.w3.org/2000/svg',c=200,P=(r,a)=>[c+r*Math.cos(a),c+r*Math.sin(a)].map(v=>v.toFixed(1)).join(' ');
  let d='';
  // the rosette: 18 circles through the centre, the spirograph of Alter X
  let ros='';for(let i=0;i<18;i++){const a=i/18*Math.PI*2;ros+=`<circle cx="${(c+78*Math.cos(a)).toFixed(1)}" cy="${(c+78*Math.sin(a)).toFixed(1)}" r="78"/>`}
  // a leaf from r1 to r2 at angle a, width w (radians at mid), with a midrib
  const leaf=(a,r1,r2,w)=>{const m=(r1+r2)/2;return `M${P(r1,a)} Q${P(m,a-w)} ${P(r2,a)} Q${P(m,a+w)} ${P(r1,a)} Z M${P(r1+4,a)} L${P(r2-6,a)} `};
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2-Math.PI/2;d+=leaf(a,160,197,.09)}
  for(let i=0;i<8;i++){const a=(i+.5)/8*Math.PI*2-Math.PI/2;d+=leaf(a,166,186,.06)}
  // four sprays out to the corners: a stem with leaves on both sides
  let spr='',buds='';
  for(let k=0;k<4;k++){const a=Math.PI/4+k*Math.PI/2;spr+=`M${P(197,a)} L${P(276,a)} `;
    for(let j=0;j<3;j++){const r=210+j*22,s=12-j*2;spr+=leaf(a-.16+j*.02,r,r+s+12,.05)+leaf(a+.16-j*.02,r,r+s+12,.05);}
    buds+=`<circle cx="${P(279,a).split(' ')[0]}" cy="${P(279,a).split(' ')[1]}" r="3.2"/>`}
  for(let i=0;i<16;i++){const p=P(176,(i+.25)/16*Math.PI*2-Math.PI/2).split(' ');buds+=`<circle cx="${p[0]}" cy="${p[1]}" r="1.6"/>`}
  const svg=`<svg class="worn" viewBox="0 0 400 400" aria-hidden="true"><g fill="none" stroke="currentColor">
    <circle cx="200" cy="200" r="199" stroke-width=".7" opacity=".55"/><circle cx="200" cy="200" r="156" stroke-width="1.1"/><circle cx="200" cy="200" r="151" stroke-width=".5" opacity=".7"/>
    <g class="ros" stroke-width=".55" opacity=".75">${ros}</g><path d="${d}" stroke-width=".9"/><path d="${spr}" stroke-width=".8" opacity=".8"/></g>
    <g fill="currentColor">${buds}</g></svg>`;
  const w=document.querySelector('.ringwrap');if(w&&!w.querySelector('.worn'))w.insertAdjacentHTML('afterbegin',svg);
  const fill=el=>{const mn=+el.min||0,mx=+el.max||1;el.style.setProperty('--v',((+el.value-mn)/(mx-mn)*100).toFixed(1)+'%')};
  const all=()=>document.querySelectorAll('input[type=range]').forEach(fill);
  document.addEventListener('input',e=>{if(e.target.type==='range')fill(e.target)},true);
  new MutationObserver(all).observe(document.body,{childList:true,subtree:true});all();setInterval(all,500);
})();
