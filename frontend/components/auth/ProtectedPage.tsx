"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { useSession } from "@/hooks/useSession";

export function ProtectedPage({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { loading, authenticated } = useSession();

  useEffect(() => {
    if (!loading && !authenticated) {
      router.push("/login");
    }
  }, [authenticated, loading, router]);

  if (loading) {
    return (
      <main className="page-shell">
        <div className="form-card panel">Checking session...</div>
      </main>
    );
  }

  if (!authenticated) {
    return null;
  }

  return <AppShell>{children}</AppShell>;
}
