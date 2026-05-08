const n = v => { const x = Number(String(v ?? '').replace(',','.')); return Number.isFinite(x) ? x : null; };
const round = (v,d=2) => Number.isFinite(v) ? Number(v.toFixed(d)) : null;
const alturaM = a => { const x=n(a); if(!x || x<=0) return null; return x > 3 ? x/100 : x; };
function idade(data){ if(!data) return null; const d=new Date(data); if(isNaN(d)) return null; const h=new Date(); let i=h.getFullYear()-d.getFullYear(); const m=h.getMonth()-d.getMonth(); if(m<0 || (m===0 && h.getDate()<d.getDate())) i--; return i; }
function imc(peso, altura){ const p=n(peso), a=alturaM(altura); return p&&a ? round(p/(a*a),2) : null; }
function classificarIMC(v){ const x=n(v); if(x==null) return 'Não calculado'; if(x<18.5) return 'Baixo peso'; if(x<25) return 'Eutrofia'; if(x<30) return 'Sobrepeso'; if(x<35) return 'Obesidade I'; if(x<40) return 'Obesidade II'; return 'Obesidade III'; }
function rcq(cintura, quadril){ const c=n(cintura), q=n(quadril); return c&&q ? round(c/q,2) : null; }
function somaDobras(dobras={}){ return round(Object.values(dobras).map(n).filter(v=>v>0).reduce((a,b)=>a+b,0),1); }
function siri(densidade){ const d=n(densidade); return d ? round((495/d)-450,2) : null; }
function percentualGorduraSimples({sexo,peso,dobras}){ const s=somaDobras(dobras); if(!s) return null; const base = String(sexo||'').toLowerCase().startsWith('f') ? 8 : 5; return round(Math.min(55, Math.max(3, base + s*0.32)),2); }
function massaGorda(peso, pg){ const p=n(peso), g=n(pg); return p&&g!=null ? round(p*g/100,2) : null; }
function massaMagra(peso, pg){ const p=n(peso), mg=massaGorda(peso,pg); return p&&mg!=null ? round(p-mg,2) : null; }
function tmb(peso, altura, idadeAnos, sexo){ const p=n(peso), a=alturaM(altura), i=n(idadeAnos); if(!p||!a||!i) return null; const s=String(sexo||'').toLowerCase().startsWith('m') ? 5 : -161; return Math.round(10*p + 6.25*(a*100) - 5*i + s); }
function oneRmEpley(carga,reps){ const c=n(carga), r=n(reps); return c&&r ? round(c*(1+r/30),1) : null; }
function oneRmBrzycki(carga,reps){ const c=n(carga), r=n(reps); return c&&r&&r<37 ? round(c*(36/(37-r)),1) : null; }
function vo2Cooper12(dist){ const d=n(dist); return d ? round((d-504.9)/44.73,2) : null; }
function fcMax(idadeAnos){ const i=n(idadeAnos); return i ? Math.round(220-i) : null; }
function karvonen(fcmax, fcrepouso, intensidade){ const max=n(fcmax), rep=n(fcrepouso), int=n(intensidade); return max&&rep&&int ? Math.round(((max-rep)*(int/100))+rep) : null; }
function indicadores(av={}, aluno={}){ const peso=n(av.peso); const altura=av.altura || aluno.altura; const idadeAnos=idade(aluno.dataNascimento); const pg=av.percentualGordura ?? percentualGorduraSimples({sexo:aluno.sexoBiologico,peso,dobras:av.dobras}); const imcVal=imc(peso,altura); return { peso, imc:imcVal, classificacaoIMC:classificarIMC(imcVal), rcq:rcq(av.cintura,av.quadril), somaDobras:somaDobras(av.dobras), percentualGordura:pg, massaGorda:massaGorda(peso,pg), massaMagra:massaMagra(peso,pg), tmb:tmb(peso,altura,idadeAnos,aluno.sexoBiologico), vo2: av.vo2Manual ?? vo2Cooper12(av.cooper12), fcMax: fcMax(idadeAnos) }; }
module.exports={n,round,idade,imc,classificarIMC,rcq,somaDobras,siri,percentualGorduraSimples,massaGorda,massaMagra,tmb,oneRmEpley,oneRmBrzycki,vo2Cooper12,fcMax,karvonen,indicadores};
