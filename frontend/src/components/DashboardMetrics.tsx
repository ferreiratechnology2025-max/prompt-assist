import { useEffect, useState } from "react";
import axios from "axios";

interface Metricas {
  total_pecas_geradas: number;
  total_analises: number;
  total_processos: number;
  tempo_medio_analise_segundos: number;
  cache_hit_rate: number;
  pecas_por_tipo: Record<string, number>;
  total_arquivos_processados: number;
  economia_tempo_estimada_horas: number;
}

export default function DashboardMetrics() {
  const [metricas, setMetricas] = useState<Metricas | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    axios
      .get<Metricas>("/api/metricas/dashboard")
      .then((r) => setMetricas(r.data))
      .catch(() => setErro("Não foi possível carregar métricas."));
  }, []);

  if (erro) return <p className="erro">{erro}</p>;
  if (!metricas) return <p className="loading">Carregando métricas...</p>;

  const pecasEntries = Object.entries(metricas.pecas_por_tipo);

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="cards">
        <div className="card">
          <span className="card-valor">{metricas.total_processos}</span>
          <span className="card-rotulo">Processos</span>
        </div>
        <div className="card">
          <span className="card-valor">{metricas.total_analises}</span>
          <span className="card-rotulo">Análises Realizadas</span>
        </div>
        <div className="card">
          <span className="card-valor">{metricas.total_pecas_geradas}</span>
          <span className="card-rotulo">Peças Geradas</span>
        </div>
        <div className="card">
          <span className="card-valor">{metricas.tempo_medio_analise_segundos}s</span>
          <span className="card-rotulo">Tempo Médio</span>
        </div>
        <div className="card">
          <span className="card-valor">{(metricas.cache_hit_rate * 100).toFixed(0)}%</span>
          <span className="card-rotulo">Cache Hit</span>
        </div>
        <div className="card card-destaque">
          <span className="card-valor">{metricas.economia_tempo_estimada_horas}h</span>
          <span className="card-rotulo">Tempo Economizado</span>
        </div>
      </div>

      {pecasEntries.length > 0 && (
        <div className="grafico-section">
          <h3>Peças por Tipo</h3>
          <div className="grafico-barras">
            {pecasEntries.map(([tipo, count]) => {
              const maxCount = Math.max(...pecasEntries.map(([, c]) => c));
              const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
              const labels: Record<string, string> = {
                contestacao: "Contestação",
                peticao_inicial: "Pet. Inicial",
                recurso: "Recurso",
                parecer: "Parecer",
                memoriais: "Memoriais",
                alegacoes_finais: "Aleg. Finais",
                notificacao: "Notificação",
                contrato: "Contrato",
                defesa: "Defesa",
                replica: "Réplica",
                analise_estrategica: "Análise Estrat.",
              };
              return (
                <div key={tipo} className="barra-row">
                  <span className="barra-label">
                    {labels[tipo] || tipo}
                  </span>
                  <div className="barra-track">
                    <div
                      className="barra-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="barra-valor">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
