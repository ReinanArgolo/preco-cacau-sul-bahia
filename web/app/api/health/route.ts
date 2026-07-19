import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const supabase = await createClient();
    const { error } = await supabase
      .from("market_prices_daily")
      .select("observation_date", { count: "exact", head: true });

    if (error) {
      return Response.json(
        { status: "degraded", database: "unavailable", code: error.code },
        { status: 503 },
      );
    }
    return Response.json({ status: "ok", database: "connected" });
  } catch {
    return Response.json(
      { status: "degraded", database: "configuration_error" },
      { status: 503 },
    );
  }
}
