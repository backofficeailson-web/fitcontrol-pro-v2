const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000/api';
function token(){ return localStorage.getItem('fit_token'); }
export async function api(path, options={}){
  const headers={ 'Content-Type':'application/json', ...(options.headers||{}) };
  const t=token(); if(t) headers.Authorization=`Bearer ${t}`;
  const res=await fetch(`${API_URL}${path}`,{...options,headers,body: options.body && typeof options.body !== 'string' ? JSON.stringify(options.body) : options.body});
  const json=await res.json().catch(()=>({success:false,message:'Resposta inválida'}));
  if(res.status===401){ localStorage.removeItem('fit_token'); localStorage.removeItem('fit_user'); }
  if(!res.ok || json.success===false) throw new Error(json.message || 'Erro na API');
  return json.data;
}
export { API_URL };
