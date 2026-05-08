const jwt = require('jsonwebtoken');
const { jwtSecret } = require('../config/env');
const db = require('../database/db');
module.exports = function auth(req,res,next){
  const header=req.headers.authorization || '';
  const token=header.startsWith('Bearer ') ? header.slice(7) : null;
  if(!token) return res.status(401).json({success:false,message:'Token ausente'});
  try{ const payload=jwt.verify(token,jwtSecret); const user=db.get('users',payload.id); if(!user) return res.status(401).json({success:false,message:'Usuário inválido'}); req.user={id:user.id,nome:user.nome,email:user.email}; next(); }
  catch(e){ return res.status(401).json({success:false,message:'Token inválido'}); }
};
