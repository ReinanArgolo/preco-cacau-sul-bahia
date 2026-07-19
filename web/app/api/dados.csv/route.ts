import { getHistory } from "@/lib/data/cocoa";

export const dynamic = "force-dynamic";

export async function GET() {
  const { rows } = await getHistory(5000);
  const header = "data,ilheus_brl_arroba,paridade_brl_arroba,base_brl_arroba";
  const lines = rows.map((row) => [row.date, row.ilheus ?? "", row.parity?.toFixed(4) ?? "", row.basis?.toFixed(4) ?? ""].join(","));
  return new Response([header, ...lines].join("\n"), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": "attachment; filename=preco-cacau-sul-bahia.csv",
      "Cache-Control": "public, max-age=900",
    },
  });
}
