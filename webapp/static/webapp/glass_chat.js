async function loadConfig(){
  const r=await fetch('/api/glass/config/'); const d=await r.json();
  document.getElementById('config_status').textContent = `API key configured: ${d.api_key_configured} | base: ${d.base_url} | version: ${d.version}`;
}
loadConfig();

document.getElementById('ask').addEventListener('click', async ()=>{
 const out=document.getElementById('output'); out.textContent='Loading...';
 const task=document.getElementById('raw_mode').checked ? 'raw_prompt' : task_type.value;
 const payload={task_type:task,patient_context:patient_context.value,question:question.value};
 const resp=await fetch('/api/glass/ask/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 const data=await resp.json();
 if(!resp.ok){out.textContent=data.detail||'Request failed'; document.getElementById('meta').textContent='Error'; return;}
 document.getElementById('meta').textContent=`schema=${data.detected_schema||''} latency_ms=${data.latency_ms||''}`;
 out.textContent=data.extracted_content||'';
 refs.textContent=JSON.stringify(data.references||[],null,2);
 cites.textContent=JSON.stringify(data.citations||[],null,2);
 usage.textContent=JSON.stringify(data.usage||{},null,2);
 raw.textContent=document.getElementById('show_raw').checked ? JSON.stringify(data.raw_response||{},null,2) : '(hidden; enable show raw response)';
});
