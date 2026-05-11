const express=require('express'); const cors=require('cors'); const {port,frontendUrl}=require('./config/env'); const app=express();
app.use(cors({origin:frontendUrl,credentials:true})); app.use(express.json({limit:'5mb'}));
app.get('/api/health',(req,res)=>res.json({success:true,message:'FitControl API online'}));
app.use('/api/auth',require('./routes/auth.routes')); app.use('/api/alunos',require('./routes/alunos.routes')); app.use('/api/avaliacoes',require('./routes/avaliacoes.routes')); app.use('/api/alunos/:alunoId/avaliacoes',(req,res,next)=>next());
app.use('/api/calculos',require('./routes/calculos.routes')); app.use('/api/treinos',require('./routes/treinos.routes')); app.use('/api/evolucao',require('./routes/evolucao.routes')); app.use('/api/relatorios',require('./routes/relatorios.routes')); app.use('/api',require('./routes/backup.routes'));
app.use((req,res)=>res.status(404).json({success:false,message:'Rota não encontrada'})); app.listen(port,()=>console.log(`FitControl API rodando na porta ${port}`));
