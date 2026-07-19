-- Contrato temporal: separa a data do evento da data em que a informação
-- realmente poderia ser usada por um sistema de previsão.
alter table market_prices_daily
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'historical_observation';

alter table exchange_rates_daily
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'historical_observation';

alter table weather_daily
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'reanalysis';

alter table producer_prices_monthly
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'publication_date_unknown';

alter table production_costs
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'publication_date_unknown';

alter table municipal_production_annual
  add column if not exists published_at timestamptz,
  add column if not exists available_at timestamptz,
  add column if not exists revision integer not null default 1,
  add column if not exists information_set text not null default 'publication_date_unknown';

-- Sem horário oficial comprovado, preço diário fica disponível de modo
-- conservador no começo do dia seguinte em Salvador.
update market_prices_daily
set available_at = (observation_date + 1)::timestamp at time zone 'America/Bahia'
where available_at is null;

-- A PTAX possui horário oficial no payload. Para registros antigos sem ele,
-- aplica-se a mesma regra conservadora do dia seguinte.
update exchange_rates_daily
set published_at = quoted_at,
    available_at = coalesce(quoted_at, (observation_date + 1)::timestamp at time zone 'America/Bahia')
where available_at is null or published_at is null;

-- Reanálise e publicações de baixa frequência coletadas agora não podem fingir
-- que estavam historicamente disponíveis.
update weather_daily
set available_at = first_collected_at,
    information_set = 'reanalysis'
where available_at is null;

update producer_prices_monthly
set available_at = first_collected_at,
    information_set = 'publication_date_unknown'
where available_at is null;

update production_costs
set available_at = first_collected_at,
    information_set = 'publication_date_unknown'
where available_at is null;

update municipal_production_annual
set available_at = first_collected_at,
    information_set = 'publication_date_unknown'
where available_at is null;

create table if not exists source_status (
  source text primary key,
  display_name text not null,
  status text not null check (status in ('healthy','degraded','failed','stale','unknown')),
  essential boolean not null default false,
  last_run_at timestamptz,
  last_success_at timestamptz,
  latest_observation_date date,
  row_count integer not null default 0,
  message text,
  updated_at timestamptz not null default now()
);

create index if not exists idx_source_status_updated on source_status (updated_at desc);

alter table source_status enable row level security;
revoke all on source_status from anon, authenticated;
grant select on source_status to anon, authenticated;

drop policy if exists "public read source status" on source_status;
create policy "public read source status" on source_status
  for select to anon, authenticated using (true);

revoke insert, update, delete, truncate, references, trigger
  on source_status from anon, authenticated;
