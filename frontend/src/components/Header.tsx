import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">Nex-Júris</h1>
        <span className="header-subtitle">Gestão de Processos</span>
      </div>
      <nav className="header-nav">
        <Link to="/" className="nav-link">Dashboard</Link>
        <Link to="/processos" className="nav-link">Processos</Link>
        <Link to="/analise" className="nav-link">Análise</Link>
      </nav>
    </header>
  );
}
