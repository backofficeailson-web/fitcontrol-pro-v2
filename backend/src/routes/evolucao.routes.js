const express=require('express'); const db=require('../database/db'); const auth=require('../middlewares/auth'); const {montarEvolucao}=require('../services/evolucao.service'); const {ok,fail}=require('../utils/apiResponse'); const router=express.Router(); router.use(auth);
router.get('/',(req,res)=>{ const alunos=db.list('alunos'); const avaliacoes=db.list('avaliacoes'); ok(res,alunos.map(aluno=>montarEvolucao(aluno,avaliacoes.filter(a=>a.alunoId===aluno.id)))); });
router.get('/aluno/:alunoId',(req,res)=>{ const aluno=db.get('alunos',req.params.alunoId); if(!aluno) return fail(res,404,'Aluno não encontrado'); ok(res,montarEvolucao(aluno,db.list('avaliacoes').filter(a=>a.alunoId===aluno.id))); });
module.exports=router;
