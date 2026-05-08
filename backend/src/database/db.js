const fs = require('fs');
const path = require('path');
const { nanoid } = require('nanoid');
const file = path.join(__dirname, 'data.json');
const initial = { users: [], alunos: [], avaliacoes: [], treinos: [] };
function ensure(){ if(!fs.existsSync(file)) fs.writeFileSync(file, JSON.stringify(initial,null,2)); }
function read(){ ensure(); return JSON.parse(fs.readFileSync(file,'utf-8')); }
function write(data){ fs.writeFileSync(file, JSON.stringify(data,null,2)); return data; }
function now(){ return new Date().toISOString(); }
function list(col){ return read()[col] || []; }
function get(col,id){ return list(col).find(x => x.id === id) || null; }
function create(col,payload){ const data=read(); const item={id:nanoid(),...payload,createdAt:now(),updatedAt:now()}; data[col].push(item); write(data); return item; }
function update(col,id,payload){ const data=read(); const i=data[col].findIndex(x=>x.id===id); if(i<0) return null; data[col][i]={...data[col][i],...payload,id,updatedAt:now()}; write(data); return data[col][i]; }
function remove(col,id){ const data=read(); const old=data[col].length; data[col]=data[col].filter(x=>x.id!==id); write(data); return data[col].length !== old; }
function replaceAll(next){ write({ users: next.users||[], alunos: next.alunos||[], avaliacoes: next.avaliacoes||[], treinos: next.treinos||[] }); return read(); }
module.exports={read,write,list,get,create,update,remove,replaceAll};
