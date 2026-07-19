import Link from "next/link";
import { HistoryChart } from "@/components/HistoryChart";
import { getCocoaSnapshot, getHistory, getSourceStatus } from "@/lib/data/cocoa";

export const dynamic = "force-dynamic";

function money(value: string | number | null) {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
}

function number(value: string | number | null, digits = 2) {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value));
}

function dateLabel(value: string | null) {
  if (!value) return "data indisponível";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function ageInDays(value: string | null) {
  if (!value) return null;
  return Math.max(0, Math.floor((Date.now() - new Date(`${value}T00:00:00Z`).getTime()) / 86_400_000));
}

const sourceLabels: Record<string, string> = {
  seagri: "Seagri",
  icco: "ICCO",
  bcb: "Banco Central",
  weather: "Open-Meteo",
};

export default async function Page() {
  const [snapshot, history, sourceStatus] = await Promise.all([
    getCocoaSnapshot(),
    getHistory(30),
    getSourceStatus(),
  ]);
  const { ilheus, international, ptax, parity, basis, errors, isStale, referenceDate } = snapshot;
  const age = ageInDays(referenceDate);
  const publicSources = sourceStatus.filter((source) => source.source in sourceLabels);

  return (
    <main className="home-page">
      <section className="home-hero">
        <div className="hero-copy">
          <div className={`update-pill ${isStale ? "update-pill-stale" : ""}`}>
            <span aria-hidden="true" className="status-dot" />
            {referenceDate ? `Última publicação: ${dateLabel(referenceDate)}` : "Cotação local indisponível"}
          </div>
          <h1>Preço do cacau no Sul da Bahia</h1>
          <p className="lead">Compare a referência de Ilhéus com o mercado internacional e veja claramente a data de cada informação.</p>
          <p className="hero-trust">Dados públicos, metodologia aberta e nenhum valor preenchido artificialmente.</p>
        </div>

        <article className="price-card">
          <div className="price-card-heading">
            <div><span className="card-kicker">Referência regional</span><h2>Ilhéus, Bahia</h2></div>
            <span aria-hidden="true" className="pod-symbol">◒</span>
          </div>
          <div className="main-price">
            <span className="currency">R$</span>
            <strong>{number(ilheus?.price ?? null)}</strong>
            <span className="unit">por arroba de 15 kg</span>
          </div>
          <div className="price-date"><span aria-hidden="true">◷</span> Cotação de {dateLabel(referenceDate)}</div>
          {(errors.length > 0 || isStale) && (
            <div role="status" className="data-warning">
              <strong>{errors.length > 0 ? "Dados parcialmente indisponíveis." : "Atenção: cotação antiga."}</strong>
              <span>{errors.length > 0 ? "Consulte a página de fontes antes de usar a referência." : `A publicação tem ${age ?? "vários"} dias. Confirme o preço atual antes de negociar.`}</span>
            </div>
          )}
        </article>
      </section>

      <section className="market-grid" aria-label="Comparação de mercado">
        <article className="metric-card">
          <span className="metric-label"><i aria-hidden="true">◎</i> Paridade internacional</span>
          <strong>{money(parity)}</strong>
          <small>{parity == null ? "Sem uma data comum" : `por arroba • ICCO e PTAX de ${dateLabel(international?.observation_date ?? null)}`}</small>
        </article>
        <article className="metric-card">
          <span className="metric-label"><i aria-hidden="true">↔</i> Diferença local</span>
          <strong className={basis != null && basis < 0 ? "negative" : "positive"}>{money(basis)}</strong>
          <small>Ilhéus menos paridade; não inclui frete nem qualidade</small>
        </article>
        <article className="metric-card">
          <span className="metric-label"><i aria-hidden="true">$</i> Dólar PTAX</span>
          <strong>{ptax ? `R$ ${number(ptax.sell_rate, 4)}` : "—"}</strong>
          <small>Banco Central • {dateLabel(ptax?.observation_date ?? null)}</small>
        </article>
      </section>

      <section className="trend-section">
        <div className="section-heading">
          <div><span className="section-kicker">Histórico recente</span><h2>Tendência das últimas cotações</h2></div>
          <Link href="/historico">Ver histórico completo <span aria-hidden="true">→</span></Link>
        </div>
        {history.errors.length > 0 ? <p className="empty-state">O histórico está temporariamente indisponível.</p> : <HistoryChart rows={history.rows.slice(-30)} />}
      </section>

      <section className="value-factors">
        <div className="section-heading"><div><span className="section-kicker">Além da cotação</span><h2>O que pode mudar o valor recebido?</h2></div></div>
        <div className="factor-grid">
          <article><span className="factor-icon" aria-hidden="true">✿</span><h3>Qualidade e fermentação</h3><p>Amêndoas bem fermentadas e classificadas podem ter condições diferentes.</p></article>
          <article><span className="factor-icon" aria-hidden="true">◌</span><h3>Umidade</h3><p>O teor de umidade afeta peso, conservação e aceitação do lote.</p></article>
          <article><span className="factor-icon" aria-hidden="true">▱</span><h3>Frete</h3><p>Distância, acesso à propriedade e volume alteram o custo de transporte.</p></article>
          <article><span className="factor-icon" aria-hidden="true">◉</span><h3>Comprador e pagamento</h3><p>Prazo, volume e negociação determinam a oferta efetivamente recebida.</p></article>
        </div>
      </section>

      <section className="source-band" aria-labelledby="source-band-title">
        <div><span className="section-kicker">Transparência</span><h2 id="source-band-title">Saúde das fontes</h2></div>
        <div className="source-band-list">
          {publicSources.length === 0 ? <span>Status temporariamente indisponível</span> : publicSources.map((source) => (
            <span key={source.source}><i className={`source-dot source-dot-${source.status}`} />{sourceLabels[source.source]} <small>{source.status === "healthy" ? "coleta concluída" : "verifique"}</small></span>
          ))}
        </div>
        <Link href="/fontes">Ver detalhes</Link>
      </section>

      <aside className="informative-note"><strong>Referência informativa</strong><span>O valor efetivamente pago pode variar. Esta plataforma não recomenda venda, compra ou retenção de cacau.</span></aside>
    </main>
  );
}
