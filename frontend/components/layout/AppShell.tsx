"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { clearSession } from "@/lib/auth";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const logout = () => {
    clearSession();
    router.push("/login");
  };

  return (
    <div className="desk-layout">
      <aside className="desk-sidebar">
        <h1>Macro Intel Desk</h1>
        <nav className="desk-nav">
          <Link href="/dashboard" aria-current={pathname === "/dashboard" ? "page" : undefined}>
            Dashboard
          </Link>
          <Link href="/intelligence" aria-current={pathname === "/intelligence" ? "page" : undefined}>
            Intelligence
          </Link>
          <Link href="/pairs/CHF_EUR" aria-current={pathname === "/pairs/CHF_EUR" ? "page" : undefined}>
            CHF / EUR
          </Link>
          <Link href="/pairs/ZB_GC" aria-current={pathname === "/pairs/ZB_GC" ? "page" : undefined}>
            10Y / Gold
          </Link>
          <Link href="/pairs/BZ_GC" aria-current={pathname === "/pairs/BZ_GC" ? "page" : undefined}>
            Crude / Gold
          </Link>
          <Link href="/pairs/CHF_GC" aria-current={pathname === "/pairs/CHF_GC" ? "page" : undefined}>
            CHF / Gold
          </Link>
          <Link href="/journals" aria-current={pathname === "/journals" ? "page" : undefined}>
            Journals
          </Link>
          <Link href="/settings" aria-current={pathname === "/settings" ? "page" : undefined}>
            Settings
          </Link>
        </nav>
        <div style={{ marginTop: 24 }}>
          <button className="button-secondary" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="desk-main">{children}</main>
    </div>
  );
}
