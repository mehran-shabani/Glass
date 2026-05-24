document.getElementById('ask').addEventListener('click', async ()=>{
 const out=document.getElementById('output'); out.textContent='Loading...';
 const resp=await fetch('/api/glass/ask/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_type:task_type.value,patient_context:patient_context.value,question:question.value})});
 const data=await resp.json();
 if(!resp.ok){out.textContent=data.detail||'Request failed';return;}
 out.textContent=data.extracted_content||'';
 const refs=document.getElementById('refs');refs.innerHTML='';(data.references||[]).forEach(r=>{const li=document.createElement('li');li.textContent=(r.title||JSON.stringify(r));refs.appendChild(li);});
});
