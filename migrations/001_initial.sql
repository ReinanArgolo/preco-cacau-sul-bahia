create table if not exists ingestion_runs (
  id uuid primary key,
  source text not null,
  requested_start date not null,
  requested_end date not null,
  status text not null check (status in ('running','success','degraded','failed','skipped')),
  row_count integer not null default 0,
  coverage_start date,
  coverage_end date,
  checksum text,
  warnings jsonb not null default '[]'::jsonb,
  error text,
  started_at timestamptz not null default now(),
  finished_at timestamptz
);

create table if not exists market_prices_daily (
  source text not null,
  series text not null,
  market text not null,
  observation_date date not null,
  price numeric not null check (price > 0),
  currency text not null,
  unit text not null,
  quality_type text,
  london_futures_gbp_tonne numeric,
  new_york_futures_usd_tonne numeric,
  icco_eur_tonne numeric,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, series, market, observation_date)
);

create table if not exists exchange_rates_daily (
  source text not null,
  currency_pair text not null,
  observation_date date not null,
  buy_rate numeric not null,
  sell_rate numeric not null,
  bulletin_type text,
  quoted_at timestamptz,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, currency_pair, observation_date)
);

create table if not exists weather_daily (
  source text not null,
  location_id text not null,
  observation_date date not null,
  latitude numeric not null,
  longitude numeric not null,
  timezone text not null,
  model text not null,
  temperature_2m_max numeric,
  temperature_2m_min numeric,
  precipitation_sum numeric,
  et0_fao_evapotranspiration numeric,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, location_id, observation_date)
);

create table if not exists producer_prices_monthly (
  source text not null,
  state text not null,
  product text not null,
  reference_month date not null,
  price_brl_kg numeric not null,
  commercial_level text,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, state, product, reference_month)
);

create table if not exists production_costs (
  source text not null,
  location text not null,
  reference_year integer not null,
  cost_item text not null,
  value_brl numeric not null,
  unit text,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, location, reference_year, cost_item)
);

create table if not exists municipal_production_annual (
  source text not null,
  municipality_code text not null,
  year integer not null,
  product text not null,
  municipality_name text,
  planted_area_ha numeric,
  harvested_area_ha numeric,
  production_tonne numeric,
  yield_kg_ha numeric,
  production_value_thousand_brl numeric,
  source_url text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_checksum text not null,
  previous_checksum text,
  first_collected_at timestamptz not null default now(),
  last_collected_at timestamptz not null default now(),
  primary key (source, municipality_code, year, product)
);

create table if not exists data_quality_events (
  id bigint generated always as identity primary key,
  source text not null,
  check_name text not null,
  severity text not null check (severity in ('info','warning','error')),
  message text not null,
  observation_date date,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_market_prices_date on market_prices_daily (observation_date);
create index if not exists idx_market_prices_source_date
  on market_prices_daily (source, observation_date desc);
create index if not exists idx_exchange_rates_source_date
  on exchange_rates_daily (source, observation_date desc);
create index if not exists idx_weather_date on weather_daily (observation_date);
create index if not exists idx_weather_location_date
  on weather_daily (location_id, observation_date desc);
create index if not exists idx_ingestion_runs_source_started
  on ingestion_runs (source, started_at desc);
create index if not exists idx_quality_created on data_quality_events (created_at desc);

alter table ingestion_runs enable row level security;
alter table market_prices_daily enable row level security;
alter table exchange_rates_daily enable row level security;
alter table weather_daily enable row level security;
alter table producer_prices_monthly enable row level security;
alter table production_costs enable row level security;
alter table municipal_production_annual enable row level security;
alter table data_quality_events enable row level security;

revoke all on ingestion_runs, data_quality_events from anon, authenticated;
grant select on market_prices_daily, exchange_rates_daily, weather_daily,
  producer_prices_monthly, production_costs, municipal_production_annual
  to anon, authenticated;

drop policy if exists "public read market prices" on market_prices_daily;
create policy "public read market prices" on market_prices_daily
  for select to anon, authenticated using (true);
drop policy if exists "public read exchange rates" on exchange_rates_daily;
create policy "public read exchange rates" on exchange_rates_daily
  for select to anon, authenticated using (true);
drop policy if exists "public read weather" on weather_daily;
create policy "public read weather" on weather_daily
  for select to anon, authenticated using (true);
drop policy if exists "public read producer prices" on producer_prices_monthly;
create policy "public read producer prices" on producer_prices_monthly
  for select to anon, authenticated using (true);
drop policy if exists "public read production costs" on production_costs;
create policy "public read production costs" on production_costs
  for select to anon, authenticated using (true);
drop policy if exists "public read municipal production" on municipal_production_annual;
create policy "public read municipal production" on municipal_production_annual
  for select to anon, authenticated using (true);
