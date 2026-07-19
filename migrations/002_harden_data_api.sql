-- O dashboard é somente leitura. Grants de escrita implícitos devem ser removidos
-- mesmo quando o RLS já impediria a operação.
revoke insert, update, delete, truncate, references, trigger
  on market_prices_daily, exchange_rates_daily, weather_daily,
     producer_prices_monthly, production_costs, municipal_production_annual
  from anon, authenticated;

revoke usage, select on sequence data_quality_events_id_seq from anon, authenticated;

-- Tabelas operacionais permanecem invisíveis na Data API. As políticas negativas
-- tornam a intenção explícita e mantêm o Security Advisor sem ambiguidades.
drop policy if exists "deny public ingestion runs" on ingestion_runs;
create policy "deny public ingestion runs" on ingestion_runs
  as restrictive for all to anon, authenticated
  using (false) with check (false);

drop policy if exists "deny public quality events" on data_quality_events;
create policy "deny public quality events" on data_quality_events
  as restrictive for all to anon, authenticated
  using (false) with check (false);

-- Novos objetos do schema public passam a exigir grants deliberados na migration.
alter default privileges for role postgres in schema public
  revoke select, insert, update, delete, truncate, references, trigger
  on tables from anon, authenticated;

alter default privileges for role postgres in schema public
  revoke usage, select on sequences from anon, authenticated;

alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated, public;
