import { useState, useRef } from "react";
import axios from "axios";
import GeracaoPecas from "./GeracaoPecas";
import AlertBadge from "./AlertBadge";

interface Analise {
  partes?: { autor: string; reu: string };
  resumo_fatos?: string;
  pedidos_autor?: string[];
  fundamentacao_juridica?: string;
  pontos_fracos?: string[];
  prazos_importantes?: string[];
  erro?: string;
  resposta_bruta?: string;
  aviso?: string;
}

interface Alerta {
  tipo: string;
  severidade: string;
  mensagem: string;
  trecho?: string;
}

interface Resultado {
  analise: Analise;
  alertas?: Alerta[];
  cache_hit?: boolean;
  processo_id: number;
  tempo_segundos: number;
  analise_id: number;
}

export default function DocumentUpload() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [arrastando, setArrastando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleUpload(file: File) {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "docx", "png", "jpg", "jpeg"].includes(ext || "")) {
      setErro("Formato não suportado. Use PDF, DOCX, PNG ou JPG.");
      return;
    }

    setArquivo(file);
    setCarregando(true);
    setErro("");
    setResultado(null);

    const formData = new FormData();
    formData.append("arquivo", file);

    try {
      const resp = await axios.post<Resultado>(
        "/api/documentos/upload",
        formData
      );
      setResultado(resp.data);
    } catch (err: any) {
      const msg =
        err.response?.data?.detail || "Erro ao processar documento.";
      setErro(msg);
    } finally {
      setCarregando(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setArrastando(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setArrastando(true);
  }

  function handleDragLeave() {
    setArrastando(false);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  }

  const a = resultado?.analise;

  return (
    <div className="document-upload">
      <h2>Análise de Documentos</h2>

      <div
        className={`dropzone ${arrastando ? "dropzone-active" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg"
          onChange={handleChange}
          hidden
        />
        {carregando ? (
          <div className="upload-progress">
            <div className="spinner" />
            <p>Analisando documento...</p>
          </div>
        ) : (
          <div className="upload-placeholder">
            <span className="upload-icon">&#128196;</span>
            <p>Arraste um documento ou clique para selecionar</p>
            <small>PDF, DOCX, PNG, JPG</small>
          </div>
        )}
      </div>

      {arquivo && !carregando && !resultado && !erro && (
        <p className="file-info">Arquivo: {arquivo.name}</p>
      )}

      {erro && <p className="erro">{erro}</p>}

      {resultado?.cache_hit && (
        <div className="cache-badge">
          Resultado do cache ({resultado.tempo_segundos}s)
        </div>
      )}

      {resultado?.alertas && resultado.alertas.length > 0 && (
        <AlertBadge alertas={resultado.alertas} />
      )}

      {resultado && a && !a.erro && (
        <div className="analise-resultado">
          <div className="analise-header">
            <h3>Resultado da Análise</h3>
            <span className="tempo">{resultado.tempo_segundos}s</span>
          </div>

          <div className="analise-cards">
            {a.partes && (
              <div className="analise-card">
                <h4>Partes</h4>
                <p><strong>Autor:</strong> {a.partes.autor}</p>
                <p><strong>Réu:</strong> {a.partes.reu}</p>
              </div>
            )}

            {a.resumo_fatos && (
              <div className="analise-card">
                <h4>Resumo dos Fatos</h4>
                <p>{a.resumo_fatos}</p>
              </div>
            )}

            {a.pedidos_autor && a.pedidos_autor.length > 0 && (
              <div className="analise-card">
                <h4>Pedidos do Autor</h4>
                <ul>
                  {a.pedidos_autor.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {a.fundamentacao_juridica && (
              <div className="analise-card">
                <h4>Fundamentação Jurídica</h4>
                <p>{a.fundamentacao_juridica}</p>
              </div>
            )}

            {a.pontos_fracos && a.pontos_fracos.length > 0 && (
              <div className="analise-card card-alerta">
                <h4>Pontos Fracos</h4>
                <ul>
                  {a.pontos_fracos.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {a.prazos_importantes && a.prazos_importantes.length > 0 && (
              <div className="analise-card card-prazo">
                <h4>Prazos Importantes</h4>
                <ul>
                  {a.prazos_importantes.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {a?.erro && (
        <div className="analise-resultado">
          <div className="analise-card card-alerta">
            <h4>Erro na Análise</h4>
            <p>{a.erro}</p>
          </div>
        </div>
      )}

      {a?.resposta_bruta && (
        <div className="analise-resultado">
          <div className="analise-card">
            <h4>Resposta Bruta (fallback)</h4>
            <pre>{a.resposta_bruta}</pre>
          </div>
        </div>
      )}

      {resultado && resultado.analise_id && (
        <GeracaoPecas analiseId={resultado.analise_id} />
      )}
    </div>
  );
}
