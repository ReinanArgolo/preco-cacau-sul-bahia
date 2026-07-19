import { createBrowserClient } from "@supabase/ssr";
import { supabaseConfig } from "@/lib/supabase/config";
import type { Database } from "@/lib/supabase/database.types";

export function createClient() {
  const { url, publishableKey } = supabaseConfig();
  return createBrowserClient<Database>(
    url,
    publishableKey,
  );
}
