"use client";

import { useEffect, useState } from "react";

import { getStoredUser, getToken } from "@/lib/auth";
import { fetchMe } from "@/lib/api";

export function useSession() {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<ReturnType<typeof getStoredUser>>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setAuthenticated(false);
      setLoading(false);
      return;
    }

    const storedUser = getStoredUser();
    setUser(storedUser);

    fetchMe()
      .then((resolvedUser) => {
        setUser(resolvedUser);
        setAuthenticated(true);
      })
      .catch(() => {
        setAuthenticated(false);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return { loading, authenticated, user };
}
