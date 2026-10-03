import { useEffect, useState } from "react";
import { listarProcessos } from "../services/api";
import type { Processo } from "../types/Processo";

export default function ProcessList() {
  const [processos, setProcessos] = useState<Processo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  function carregar() {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then(setProcessos)
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
  }, []);

  return (
    <div className="process-list">
      <div className="list-header">
        <h3>Processos Cadastrados</h3>
        <button className="btn-atualizar" onClick={carregar} disabled={carregando}>
          {carregando ? "Carregando..." : "Atualizar"}
        </button>
      </div>

      {erro && <p className="erro">{erro}</p>}

      {!carregando && processos.length === 0 && (
        <p className="vazio">Nenhum processo cadastrado.</p>
      )}

      {processos.length > 0 && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Cliente</th>
                <th>Data</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {processos.map((p) => (
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td>{p.nome}</td>
                  <td>{p.cliente}</td>
                  <td>{new Date(p.data_criacao).toLocaleDateString("pt-BR")}</td>
                  <td>
                    <span className={`status status-${p.status}`}>{p.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
