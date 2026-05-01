"use client";

import { LoginResponse } from "./types";

const TOKEN_KEY = "macro_intel_token";
const USER_KEY = "macro_intel_user";

export function saveSession(session: LoginResponse) {
  localStorage.setItem(TOKEN_KEY, session.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): LoginResponse["user"] | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as LoginResponse["user"];
  } catch {
    return null;
  }
}
