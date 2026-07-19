import type { Metadata } from "next";
import "./styles.css";
import Link from "next/link";
import { BrandMark } from "@/components/BrandMark";

export const metadata: Metadata = {
  title: "Cacau Sul da Bahia",
  description: "Referências públicas do mercado de cacau para pequenos produtores",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <header className="site-header">
          <Link href="/" className="brand" aria-label="Cacau Bahia — início">
            <BrandMark />
            <span>Cacau Bahia</span>
          </Link>
          <nav className="main-nav" aria-label="Navegação principal">
            <Link href="/">Início</Link>
            <Link href="/historico">Histórico</Link>
            <Link href="/fontes">Fontes</Link>
            <Link href="/metodologia">Como funciona</Link>
          </nav>
          <Link className="header-action" href="/api/dados.csv">Baixar dados</Link>
        </header>
        {children}
        <footer>
          <div className="footer-brand"><BrandMark size={30} /><strong>Cacau Bahia</strong></div>
          <p>Dados públicos para apoiar decisões mais informadas no Sul da Bahia.</p>
          <p className="footer-note">Uso informativo. Confirme o valor e as condições com o comprador antes de negociar.</p>
        </footer>
      </body>
    </html>
  );
}
