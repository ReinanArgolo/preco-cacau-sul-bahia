import Link from "next/link";
import { HistoryChart } from "@/components/HistoryChart";
import { getHistory } from "@/lib/data/cocoa";

export const dynamic = "force-dynamic";

export default async function HistoryPage() {
  const { rows, errors } = await getHistory();
  const aligned = rows.filter((row) => row.parity != null);
  return (
    <main>
      <p className="eyebrow">Séries públicas alinhadas</p>
      <h1 className="page-title">Histórico</h1>
      <p className="lead">A paridade só aparece quando cotação local, ICCO e PTAX pertencem à mesma data. Não preenchemos dias ausentes com valores futuros.</p>
      {errors.length > 0 && <p className="data-warning">Parte do histórico está indisponível agora.</p>}
      <HistoryChart rows={rows} />
      <section className="summary-strip" aria-label="Cobertura exibida">
        <div><strong>{rows.length}</strong><span>datas locais</span></div>
        <div><strong>{aligned.length}</strong><span>datas comparáveis</span></div>
        <div><strong>{rows.at(0)?.date ?? "—"}</strong><span>início</span></div>
        <div><strong>{rows.at(-1)?.date ?? "—"}</strong><span>fim</span></div>
      </section>
      <p><Link className="button" href="/api/dados.csv">Exportar dados públicos em CSV</Link></p>
    </main>
  );
}
