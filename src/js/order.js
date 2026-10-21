(()=>{'use strict';
const form=document.getElementById('orderform');if(!form)return;
const catalog=JSON.parse(form.dataset.catalog),rows=document.getElementById('rows');
const byKey={};catalog.forEach(g=>g.items.forEach(i=>byKey[i.key]=i));
function sync(row){
  const it=byKey[row.querySelector('[name="item_key[]"]').value],opt=row.querySelector('[name="option[]"]');
  const want=opt.dataset.sel||opt.value;opt.replaceChildren();
  if(!it||!it.options.length){const o=document.createElement('option');o.value='';o.textContent=it?'—':'—';opt.appendChild(o);opt.disabled=true;opt.dataset.sel='';return}
  opt.disabled=false;
  it.options.forEach(t=>{const o=document.createElement('option');o.value=t;o.textContent=t;if(t===want)o.selected=true;opt.appendChild(o)});
  opt.dataset.sel='';
}
rows.addEventListener('change',e=>{if(e.target.name==='item_key[]'){const o=e.target.closest('.orow').querySelector('[name="option[]"]');o.dataset.sel='';sync(e.target.closest('.orow'))}});
rows.addEventListener('click',e=>{if(e.target.closest('.rm')){const all=rows.querySelectorAll('.orow');if(all.length>1)e.target.closest('.orow').remove()}});
document.getElementById('addrow').addEventListener('click',()=>{
  if(rows.querySelectorAll('.orow').length>=40)return;
  const c=rows.querySelector('.orow').cloneNode(true);
  c.querySelector('[name="item_key[]"]').value='';c.querySelector('[name="qty[]"]').value='';c.querySelector('[name="option[]"]').dataset.sel='';
  rows.appendChild(c);sync(c);
});
rows.querySelectorAll('.orow').forEach(sync);
})();
