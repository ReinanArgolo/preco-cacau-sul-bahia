import { getSourceStatus } from "@/lib/data/cocoa";

export const dynamic = "force-dynamic";

const labels: Record<string, string> = { healthy: "Atualizada", degraded: "Com ressalvas", failed: "Falhou", stale: "Atrasada", unknown: "Sem diagnóstico" };

export default async function SourcesPage() {
  const sources = await getSourceStatus();
  return (
    <main>
      <p className="eyebrow">Transparência operacional</p>
      <h1 className="page-title">Fontes</h1>
      <p className="lead">Cada fonte mostra a observação mais recente e a saúde da coleta. Mensagens técnicas sensíveis nunca são publicadas.</p>
      {sources.length === 0 ? <p className="empty-state">Status ainda não publicado. As séries continuam disponíveis, mas a saúde da coleta não pode ser confirmada.</p> : (
        <div className="table-wrap"><table><thead><tr><th>Fonte</th><th>Situação</th><th>Último dado</th><th>Último sucesso</th><th>Registros na coleta</th></tr></thead><tbody>
          {sources.map((source) => <tr key={source.source}><td><strong>{source.display_name}</strong>{source.essential && <small>essencial</small>}</td><td><span className={`status status-${source.status}`}>{labels[source.status] ?? source.status}</span></td><td>{source.latest_observation_date ?? "sem dado"}</td><td>{source.last_success_at ? new Date(source.last_success_at).toLocaleString("pt-BR", { timeZone: "America/Bahia" }) : "—"}</td><td>{source.row_count}</td></tr>)}
        </tbody></table></div>
      )}
    </main>
  );
}
