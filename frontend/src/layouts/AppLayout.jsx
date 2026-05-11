import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
const links=[['/dashboard','Dashboard'],['/alunos','Alunos'],['/avaliacoes','Avaliações'],['/treinos','Treinos'],['/protocolos','Protocolos'],['/evolucao','Evolução'],['/relatorios','Relatórios'],['/configuracoes','Configurações']];
export default function AppLayout(){ const {user,logout}=useAuth(); return <div className="app-shell"><aside><h1>FitControl<span>Pro 2.0</span></h1><nav>{links.map(([to,label])=><NavLink key={to} to={to}>{label}</NavLink>)}</nav></aside><main><header><div><strong>Olá, {user?.nome}</strong><small>Sistema profissional de avaliação e treinos</small></div><button onClick={logout}>Sair</button></header><section className="content"><Outlet/></section></main></div> }
