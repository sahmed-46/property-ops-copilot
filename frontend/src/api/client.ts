import type { ChatRequest, ChatResponse, Unit } from "../types";

function resolveApiBase(): string {
  const configured = import.meta.env.VITE_API_BASE;
  if (configured !== undefined && configured !== null) {
    return configured;
  }
  return import.meta.env.DEV ? "/api" : "";
}

const API_BASE = resolveApiBase();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export function fetchUnits(): Promise<Unit[]> {
  return request<Unit[]>("/units");
}

export function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchReady(): Promise<{ status: string; units: Unit[] }> {
  return request<{ status: string; units: Unit[] }>("/ready");
}

export function checkHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}
