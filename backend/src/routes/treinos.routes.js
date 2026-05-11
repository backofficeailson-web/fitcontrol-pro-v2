const express=require('express'); const db=require('../database/db'); const auth=require('../middlewares/auth'); const {gerarTreinoIA}=require('../services/iaTreino.service'); const {ok,fail}=require('../utils/apiResponse'); const router=express.Router(); router.use(auth);
router.get('/',(req,res)=>ok(res,db.list('treinos'))); router.get('/:id',(req,res)=>{const t=db.get('treinos',req.params.id); return t?ok(res,t):fail(res,404,'Treino não encontrado')});
router.post('/',(req,res)=>ok(res,db.create('treinos',{...req.body,exercicios:req.body.exercicios||[]}),'Treino criado'));
router.put('/:id',(req,res)=>{const t=db.update('treinos',req.params.id,req.body); return t?ok(res,t,'Treino atualizado'):fail(res,404,'Treino não encontrado')});
router.delete('/:id',(req,res)=>db.remove('treinos',req.params.id)?ok(res,true,'Treino excluído'):fail(res,404,'Treino não encontrado'));
router.post('/modelo',(req,res)=>{ const aluno=db.get('alunos',req.body.alunoId)||{}; ok(res,gerarTreinoIA(aluno,req.body),'Modelo gerado'); });
router.post('/gerar-ia',(req,res)=>{ const aluno=db.get('alunos',req.body.alunoId); if(!aluno) return fail(res,404,'Aluno não encontrado'); const treino=db.create('treinos',gerarTreinoIA(aluno,req.body)); ok(res,treino,'Treino gerado por IA de regras'); });
module.exports=router;
