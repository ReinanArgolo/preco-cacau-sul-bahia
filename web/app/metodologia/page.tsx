export default function MethodologyPage() {
  return (
    <main>
      <p className="eyebrow">Como interpretar</p>
      <h1 className="page-title">Metodologia</h1>
      <div className="prose">
        <section><h2>Cotação local</h2><p>Usamos a cotação pública de cacau comum em Ilhéus como referência regional. Ela não é uma garantia de oferta em Gandu ou na propriedade.</p></section>
        <section><h2>Paridade internacional</h2><p>Convertemos o preço ICCO em dólar por tonelada para reais por arroba de 15 kg: ICCO × PTAX de venda × 0,015. A comparação só é calculada quando as três fontes têm exatamente a mesma data.</p></section>
        <section><h2>Por que o preço recebido muda?</h2><p>Frete, distância, umidade, fermentação, classificação, volume, prazo de pagamento e negociação com o comprador podem aumentar ou reduzir o valor efetivo.</p></section>
        <section><h2>Clima e dados históricos</h2><p>ERA5-Land é reanálise: uma reconstrução do clima passado. Ela é marcada dessa forma e não será usada como se fosse uma previsão que o produtor conhecia naquele dia.</p></section>
        <section><h2>Previsões</h2><p>Modelos permanecem bloqueados até existirem pelo menos 750 datas locais válidas, aproximadamente três anos, com disponibilidade temporal auditável. Qualquer previsão futura será informativa, nunca recomendação de negociação.</p></section>
      </div>
    </main>
  );
}
