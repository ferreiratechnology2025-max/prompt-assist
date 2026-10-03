interface Alerta {
  tipo: string;
  severidade: string;
  mensagem: string;
  trecho?: string;
}

interface Props {
  alertas: Alerta[];
}

const SEVERIDADE_CORES: Record<string, string> = {
  alta: "#b33c3c",
  media: "#e6a817",
  baixa: "#2d4a3e",
};

const SEVERIDADE_LABELS: Record<string, string> = {
  alta: "Alto",
  media: "Médio",
  baixa: "Baixo",
};

const TIPO_ICONES: Record<string, string> = {
  prazo_vencido: "\u26A0\uFE0F",
  inconsistencia: "\u2757",
  valor_desproporcional: "\uD83D\uDCCA",
};

export default function AlertBadge({ alertas }: Props) {
  if (!alertas || alertas.length === 0) return null;

  return (
    <div className="alertas-container">
      <h4>
        <span className="alerta-icone-titulo">{'\u26A0\uFE0F'}</span> Alertas
        Encontrados ({alertas.length})
      </h4>
      <div className="alertas-lista">
        {alertas.map((a, i) => (
          <div
            key={i}
            className="alerta-item"
            style={{
              borderLeftColor: SEVERIDADE_CORES[a.severidade] || "#e6a817",
            }}
          >
            <div className="alerta-header">
              <span className="alerta-icone">
                {TIPO_ICONES[a.tipo] || "\uD83D\uDCE2"}
              </span>
              <span className="alerta-tipo">
                {a.tipo.replace(/_/g, " ")}
              </span>
              <span
                className="alerta-severidade"
                style={{
                  background: SEVERIDADE_CORES[a.severidade] || "#e6a817",
                }}
              >
                {SEVERIDADE_LABELS[a.severidade] || a.severidade}
              </span>
            </div>
            <p className="alerta-mensagem">{a.mensagem}</p>
            {a.trecho && (
              <code className="alerta-trecho">{a.trecho}</code>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
