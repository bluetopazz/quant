import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Macro Intelligence Desk",
  description: "Operator-facing intelligence desk for macro relative-value pairs."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
