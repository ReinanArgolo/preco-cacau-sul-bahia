import type { Metadata } from "next";
import "./styles.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cacau Sul da Bahia",
  description: "Referências públicas do mercado de cacau para pequenos produtores",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <header className="site-header">
          <Link href="/" className="brand">Cacau Bahia</Link>
          <nav aria-label="Navegação principal">
            <Link href="/">Visão geral</Link>
            <Link href="/historico">Histórico</Link>
            <Link href="/fontes">Fontes</Link>
            <Link href="/metodologia">Metodologia</Link>
          </nav>
        </header>
        {children}
        <footer>Dados públicos, metodologia aberta e uso informativo.</footer>
      </body>
    </html>
  );
}
