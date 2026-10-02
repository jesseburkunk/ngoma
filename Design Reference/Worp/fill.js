
/* v1.26 skin: the lit part of every slider (--v), also when the code sets a value */
function fillRange(el){const mn=+el.min||0,mx=+el.max||1,v=((+el.value-mn)/(mx-mn)*100).toFixed(1)+'%';if(el._v!==v){el._v=v;el.style.setProperty('--v',v)}}
document.addEventListener('input',e=>{if(e.target.type==='range')fillRange(e.target)},true);
setInterval(()=>{if(!document.hidden)document.querySelectorAll('input[type=range]').forEach(fillRange)},250);
