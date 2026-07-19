import { createClient } from "@/lib/supabase/server";

type MarketPrice = {
  observation_date: string;
  price: number | string;
  unit?: string | null;
};

type ExchangeRate = {
  observation_date: string;
  sell_rate: number | string;
};

export type CocoaSnapshot = {
  ilheus: MarketPrice | null;
  international: MarketPrice | null;
  ptax: ExchangeRate | null;
  parity: number | null;
  basis: number | null;
  referenceDate: string | null;
  isStale: boolean;
  errors: string[];
};

export type HistoryRow = {
  date: string;
  ilheus: number | null;
  parity: number | null;
  basis: number | null;
};

export type PublicSourceStatus = {
  source: string;
  display_name: string;
  status: string;
  essential: boolean;
  last_run_at: string | null;
  last_success_at: string | null;
  latest_observation_date: string | null;
  row_count: number;
  message: string | null;
};

export async function getCocoaSnapshot(): Promise<CocoaSnapshot> {
  const supabase = await createClient();
  const ilheusResult = await supabase
    .from("market_prices_daily")
    .select("observation_date,price,unit")
    .eq("source", "seagri")
    .order("observation_date", { ascending: false })
    .limit(1)
    .maybeSingle<MarketPrice>();
  const referenceDate = ilheusResult.data?.observation_date ?? null;

  const [internationalResult, ptaxResult] = await Promise.all([
    supabase
      .from("market_prices_daily")
      .select("observation_date,price,unit")
      .eq("source", "icco")
      .eq("observation_date", referenceDate ?? "9999-12-31")
      .order("observation_date", { ascending: false })
      .limit(1)
      .maybeSingle<MarketPrice>(),
    supabase
      .from("exchange_rates_daily")
      .select("observation_date,sell_rate")
      .eq("source", "bcb")
      .eq("observation_date", referenceDate ?? "9999-12-31")
      .order("observation_date", { ascending: false })
      .limit(1)
      .maybeSingle<ExchangeRate>(),
  ]);

  const errors = [ilheusResult.error, internationalResult.error, ptaxResult.error]
    .filter((error) => error != null)
    .map((error) => error.message);
  const ilheus = ilheusResult.data;
  const international = internationalResult.data;
  const ptax = ptaxResult.data;
  const parity = international && ptax
    ? Number(international.price) * Number(ptax.sell_rate) * 0.015
    : null;
  const basis = ilheus && parity != null ? Number(ilheus.price) - parity : null;
  const ageMs = referenceDate ? Date.now() - new Date(`${referenceDate}T00:00:00Z`).getTime() : 0;
  const isStale = referenceDate != null && ageMs > 14 * 24 * 60 * 60 * 1000;

  return { ilheus, international, ptax, parity, basis, referenceDate, isStale, errors };
}

export async function getHistory(limit = 750): Promise<{ rows: HistoryRow[]; errors: string[] }> {
  const supabase = await createClient();
  const [localResult, internationalResult, fxResult] = await Promise.all([
    supabase.from("market_prices_daily").select("observation_date,price").eq("source", "seagri")
      .order("observation_date", { ascending: false }).limit(limit),
    supabase.from("market_prices_daily").select("observation_date,price").eq("source", "icco")
      .order("observation_date", { ascending: false }).limit(limit),
    supabase.from("exchange_rates_daily").select("observation_date,sell_rate").eq("source", "bcb")
      .order("observation_date", { ascending: false }).limit(limit),
  ]);
  const errors = [localResult.error, internationalResult.error, fxResult.error]
    .filter((error) => error != null).map((error) => error.message);
  const international = new Map((internationalResult.data ?? []).map((row) => [row.observation_date, Number(row.price)]));
  const fx = new Map((fxResult.data ?? []).map((row) => [row.observation_date, Number(row.sell_rate)]));
  const rows = (localResult.data ?? []).map((row) => {
    const date = row.observation_date;
    const ilheus = Number(row.price);
    const global = international.get(date);
    const dollar = fx.get(date);
    const parity = global != null && dollar != null ? global * dollar * 0.015 : null;
    return { date, ilheus, parity, basis: parity == null ? null : ilheus - parity };
  }).reverse();
  return { rows, errors };
}

export async function getSourceStatus(): Promise<PublicSourceStatus[]> {
  const supabase = await createClient();
  const { data, error } = await supabase.from("source_status").select("source,display_name,status,essential,last_run_at,last_success_at,latest_observation_date,row_count,message")
    .order("essential", { ascending: false }).order("source");
  if (error) return [];
  return (data ?? []) as PublicSourceStatus[];
}
