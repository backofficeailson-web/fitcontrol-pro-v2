function riscoClinico(aluno={}){ const pats=(aluno.patologias||[]).map(x=>String(x).toLowerCase()); return pats.some(p=>['cardiopatia','gestante','diabetes','hipertensão','hipertensao','pós-operatório','pos-operatorio'].includes(p)); }
const baseExercicios = {
  hipertrofia:['Agachamento livre','Supino reto','Remada baixa','Desenvolvimento','Puxada frente','Levantamento terra romeno'],
  powerlifting:['Agachamento competitivo','Supino competitivo','Levantamento terra','Supino pausado','Agachamento pausa'],
  beach:['Agachamento goblet','Avanço','Remada elástica','Rotação externa','Prancha','Deslocamento lateral'],
  saude:['Leg press leve','Puxada frente leve','Supino máquina','Remada sentada','Bike ergométrica','Mobilidade']
};
function gerarTreinoIA(aluno={}, params={}){
  const modalidade=(params.modalidade || aluno.modalidadePrincipal || 'Saúde e qualidade de vida').toLowerCase();
  const nivel=(params.nivel || aluno.nivel || 'iniciante').toLowerCase();
  const risco=riscoClinico(aluno);
  const freq=Number(aluno.frequenciaSemanal || params.frequenciaSemanal || (nivel==='avançado'?5:3));
  let chave='saude';
  if(modalidade.includes('power')) chave='powerlifting';
  else if(modalidade.includes('bench') || modalidade.includes('supino')) chave='powerlifting';
  else if(modalidade.includes('beach')) chave='beach';
  else if(modalidade.includes('hipertrof') || modalidade.includes('body')) chave='hipertrofia';
  const intensidade = risco ? 'baixa a moderada' : nivel.includes('av') ? 'moderada a alta' : 'moderada controlada';
  const divisao = freq <= 3 ? 'Full body / AB alternado' : freq === 4 ? 'Upper/Lower' : 'ABC + acessórios';
  const exercicios = baseExercicios[chave].map((nome,i)=>({ nome, grupoMuscular:'geral', tipo:i<3?'principal':'acessório', diaSemana:`Dia ${(i%Math.max(1,Math.min(freq,5)))+1}`, series: risco?2:3, repeticoes: chave==='powerlifting'?'3-6':'8-12', carga:'Ajustar por técnica', descanso: chave==='powerlifting'?'120-180s':'60-90s', rpe: risco?'5-6':'6-8', rir: risco?'3-4':'1-3', tempoExecucao:'controlado', observacoes: risco?'Evitar manobra de Valsalva e monitorar sinais clínicos.':'Progredir carga apenas com técnica estável.' }));
  return { nome:`Treino IA - ${aluno.nome || 'Aluno'}`, alunoId:aluno.id, objetivo:params.objetivo || aluno.objetivoPrincipal || 'Condicionamento', modalidade:params.modalidade || aluno.modalidadePrincipal || 'Saúde', fase:'Base técnica', divisao, frequenciaSemanal:freq, intensidade, geradoPorIA:true, observacoes: risco ? 'Aluno com fator de risco: manter intensidade controlada e exigir liberação quando necessário.' : 'Treino gerado por regras iniciais. Revisar individualmente antes de prescrever.', exercicios };
}
module.exports={gerarTreinoIA, riscoClinico};
