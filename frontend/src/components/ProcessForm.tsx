import { useState } from "react";
import { criarProcesso } from "../services/api";

interface Props {
  onCriado: () => void;
}

export default function ProcessForm({ onCriado }: Props) {
  const [nome, setNome] = useState("");
  const [cliente, setCliente] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nome.trim() || !cliente.trim()) return;

    setSalvando(true);
    setErro("");

    try {
      await criarProcesso({ nome: nome.trim(), cliente: cliente.trim() });
      setNome("");
      setCliente("");
      onCriado();
    } catch (err: any) {
      setErro(err.message);
    } finally {
      setSalvando(false);
    }
  }

  return (
    <form className="process-form" onSubmit={handleSubmit}>
      <h3>Novo Processo</h3>
      <div className="form-group">
        <label htmlFor="nome">Nome do Processo</label>
        <input
          id="nome"
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="Ex: Processo 123/2024"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="cliente">Cliente</label>
        <input
          id="cliente"
          type="text"
          value={cliente}
          onChange={(e) => setCliente(e.target.value)}
          placeholder="Nome do cliente"
          required
        />
      </div>
      {erro && <p className="erro">{erro}</p>}
      <button type="submit" disabled={salvando || !nome.trim() || !cliente.trim()}>
        {salvando ? "Salvando..." : "Salvar Processo"}
      </button>
    </form>
  );
}
