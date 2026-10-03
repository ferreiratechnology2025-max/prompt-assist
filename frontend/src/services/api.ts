import axios from "axios";
import type { Processo } from "../types/Processo";

const api = axios.create({
  baseURL: "/api",
});

export async function listarProcessos(): Promise<Processo[]> {
  try {
    const response = await api.get<Processo[]>("/processos");
    return response.data;
  } catch (error) {
    console.error("Erro ao listar processos:", error);
    throw new Error("Não foi possível carregar a lista de processos.");
  }
}

export async function criarProcesso(data: {
  nome: string;
  cliente: string;
}): Promise<Processo> {
  try {
    const response = await api.post<Processo>("/processos/upload", data);
    return response.data;
  } catch (error) {
    console.error("Erro ao criar processo:", error);
    throw new Error("Não foi possível criar o processo.");
  }
}
