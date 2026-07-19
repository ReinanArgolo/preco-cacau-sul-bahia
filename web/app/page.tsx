import { getCocoaSnapshot } from "@/lib/data/cocoa";

export const dynamic = "force-dynamic";

function money(value: string | number | null) {
  if (value == null) return "—";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
}

export default async function Page() {
  const { ilheus, international, ptax, parity, basis, errors, isStale, referenceDate } = await getCocoaSnapshot();

  return (
    <main>
      <p className="eyebrow">Mercado físico • Sul da Bahia</p>
      <h1>Referência do cacau</h1>
      <p className="lead">Dados públicos para ajudar o produtor a comparar a cotação local com o mercado internacional.</p>
      {(errors.length > 0 || isStale) && (
        <p role="status" className="data-warning">
          {errors.length > 0
            ? "Parte dos dados está temporariamente indisponível."
            : `A última cotação local publicada é de ${referenceDate}. Confirme o valor atual antes de negociar.`}
        </p>
      )}
      <section className="grid">
        <article><span>Ilhéus</span><strong>{money(ilheus?.price ?? null)}</strong><small>por arroba de 15 kg • {ilheus?.observation_date ?? "sem dado"}</small></article>
        <article><span>Paridade internacional</span><strong>{money(parity)}</strong><small>{parity == null ? "Dados sem uma data comum" : `ICCO e PTAX de ${international?.observation_date}`}</small></article>
        <article><span>Ágio/deságio aparente</span><strong className={basis != null && basis < 0 ? "negative" : "positive"}>{money(basis)}</strong><small>Não inclui qualidade, frete ou condição de pagamento</small></article>
      </section>
      <p className="source-note">Datas usadas: Ilhéus {ilheus?.observation_date ?? "sem dado"}; ICCO {international?.observation_date ?? "sem dado"}; PTAX {ptax?.observation_date ?? "sem dado"}.</p>
      <aside>Esta é uma referência informativa, não uma recomendação de venda. O valor efetivamente pago pode variar por qualidade, umidade, fermentação, frete e comprador.</aside>
    </main>
  );
}
