import { useState, useEffect } from "react";
import axios from "axios";

interface TipoPeca {
  id: string;
  nome: string;
}

interface PecaHistorico {
  id: number;
  tipo: string;
  data_geracao: string;
  tamanho_bytes: number;
  download_url: string;
}

interface Props {
  analiseId: number;
}

const CORES_PECA: Record<string, string> = {
  contestacao: "#2d4a3e",
  peticao_inicial: "#1a5a7a",
  recurso: "#7a4a1a",
  parecer: "#4a2d7a",
  memoriais: "#2d6a4a",
  alegacoes_finais: "#7a2d2d",
  notificacao: "#6a5a2d",
  contrato: "#2d4a6a",
  defesa: "#4a6a2d",
  replica: "#6a2d4a",
  analise_estrategica: "#2d2d7a",
};

export default function GeracaoPecas({ analiseId }: Props) {
  const [tipos, setTipos] = useState<TipoPeca[]>([]);
  const [gerando, setGerando] = useState<string | null>(null);
  const [historico, setHistorico] = useState<PecaHistorico[]>([]);
  const [erro, setErro] = useState("");

  useEffect(() => {
    axios.get<TipoPeca[]>("/api/pecas/tipos").then((r) => setTipos(r.data));
    carregarHistorico();
  }, [analiseId]);

  async function carregarHistorico() {
    try {
      const r = await axios.get<PecaHistorico[]>(
        `/api/pecas/historico/${analiseId}`
      );
      setHistorico(r.data);
    } catch {
      // histórico vazio é normal
    }
  }

  async function handleGerar(tipo: string) {
    setGerando(tipo);
    setErro("");
    try {
      await axios.post("/api/pecas/gerar", {
        analise_id: analiseId,
        tipo,
      });
      await carregarHistorico();
    } catch (err: any) {
      setErro(err.response?.data?.detail || "Erro ao gerar peça.");
    } finally {
      setGerando(null);
    }
  }

  const historicoMap = new Map(
    historico.map((h) => [h.tipo, h])
  );

  return (
    <div className="geracao-pecas">
      <h3>Peças Disponíveis</h3>

      <div className="pecas-grid">
        {tipos.map((t) => {
          const hist = historicoMap.get(t.id);
          const cor = CORES_PECA[t.id] || "var(--primary)";
          return (
            <div key={t.id} className="peca-card" style={{ borderLeftColor: cor }}>
              <div className="peca-info">
                <strong>{t.nome}</strong>
                {hist && (
                  <small>
                    Gerada há{" "}
                    {Math.round(
                      (Date.now() - new Date(hist.data_geracao).getTime()) /
                        60000
                    )}{" "}
                    min |{" "}
                    {hist.tamanho_bytes > 1024
                      ? `${(hist.tamanho_bytes / 1024).toFixed(1)} KB`
                      : `${hist.tamanho_bytes} B`}
                  </small>
                )}
              </div>
              <div className="peca-acoes">
                {hist && (
                  <a
                    href={hist.download_url}
                    className="btn-download"
                    download
                  >
                    &#8681; Baixar
                  </a>
                )}
                <button
                  className="btn-gerar"
                  onClick={() => handleGerar(t.id)}
                  disabled={gerando === t.id}
                  style={{ background: cor }}
                >
                  {gerando === t.id ? "Gerando..." : "Gerar"}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {erro && <p className="erro">{erro}</p>}
      <p className="aviso-legal-peca">
        Documentos gerados por IA. Revisão obrigatória pelo advogado responsável.
      </p>
    </div>
  );
}
