"use client";

import { getToken } from "./auth";
import {
  IntelligenceOverview,
  JournalEntry,
  LoginResponse,
  PairCard,
  PairDetail,
  PairRunResult,
  PairRunSummary
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function apiFetch<T>(path: string, init?: RequestInit, auth = true): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  headers.set("Content-Type", "application/json");
  if (auth) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers
    });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Failed to reach API at ${API_BASE_URL}. Check that the FastAPI server is running and that CORS allows your frontend origin.`
      );
    }
    throw error;
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ username, password })
    },
    false
  );
}

export async function fetchMe() {
  return apiFetch<LoginResponse["user"]>("/auth/me");
}

export async function fetchHealth() {
  return apiFetch<Record<string, unknown>>("/health", undefined, false);
}

export async function fetchPairs() {
  return apiFetch<PairCard[]>("/pairs");
}

export async function fetchPair(pairId: string) {
  return apiFetch<PairDetail>(`/pairs/${pairId}`);
}

export async function fetchLatestRun(pairId: string) {
  return apiFetch<PairRunResult>(`/pairs/${pairId}/latest`);
}

export async function runPair(pairId: string) {
  return apiFetch<PairRunResult>(`/pairs/${pairId}/run`, {
    method: "POST",
    body: JSON.stringify({ pair_id: pairId, persist_journal: false, trigger_source: "ui_manual" })
  });
}

export async function fetchPairHistory(pairId: string) {
  return apiFetch<PairRunSummary[]>(`/pairs/${pairId}/history`);
}

export async function fetchPairJournals(pairId: string) {
  return apiFetch<JournalEntry[]>(`/journals/${pairId}`);
}

export async function fetchAllJournals() {
  return apiFetch<JournalEntry[]>("/journals");
}

export async function appendJournal(pairId: string, runId: string) {
  return apiFetch<JournalEntry>(`/journals/${pairId}`, {
    method: "POST",
    body: JSON.stringify({ run_id: runId })
  });
}

export async function fetchIntelligenceOverview() {
  return apiFetch<IntelligenceOverview>("/intelligence");
}

export async function refreshIntelligenceOverview() {
  return apiFetch<IntelligenceOverview>("/intelligence/refresh", { method: "POST" });
}
