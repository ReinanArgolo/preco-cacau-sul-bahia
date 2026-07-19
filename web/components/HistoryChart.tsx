import type { HistoryRow } from "@/lib/data/cocoa";

export function HistoryChart({ rows }: { rows: HistoryRow[] }) {
  const usable = rows.filter(
    (row): row is HistoryRow & { ilheus: number } => row.ilheus != null,
  );
  if (usable.length < 2) return <p className="empty-state">Dados insuficientes para desenhar o histórico.</p>;
  const values = usable.flatMap((row) => [row.ilheus, row.parity]).filter((value): value is number => value != null);
  const low = Math.min(...values);
  const high = Math.max(...values);
  const width = 900;
  const height = 360;
  const point = (value: number, index: number) => {
    const x = 30 + (index / Math.max(usable.length - 1, 1)) * (width - 60);
    const y = 20 + ((high - value) / Math.max(high - low, 1)) * (height - 50);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  };
  const local = usable.map((row, index) => point(row.ilheus, index)).join(" ");
  const paritySegments: string[] = [];
  let segment: string[] = [];
  usable.forEach((row, index) => {
    if (row.parity == null) {
      if (segment.length > 1) paritySegments.push(segment.join(" "));
      segment = [];
    } else segment.push(point(row.parity, index));
  });
  if (segment.length > 1) paritySegments.push(segment.join(" "));
  return (
    <figure className="chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="chart-title chart-desc">
        <title id="chart-title">Cotação de Ilhéus e paridade internacional</title>
        <desc id="chart-desc">Séries comparadas somente quando ICCO e PTAX possuem a mesma data da cotação local.</desc>
        <polyline points={local} className="line-local" />
        {paritySegments.map((points, index) => <polyline key={index} points={points} className="line-parity" />)}
      </svg>
      <figcaption><span className="legend local">Ilhéus</span><span className="legend parity">Paridade na mesma data</span></figcaption>
    </figure>
  );
}
