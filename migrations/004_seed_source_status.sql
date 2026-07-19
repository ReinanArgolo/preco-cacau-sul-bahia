insert into source_status (source, display_name, status, essential, latest_observation_date, row_count, message)
values
  ('seagri', 'Cotação de Ilhéus — Seagri-BA', 'unknown', true, null, 0, null),
  ('bcb', 'Dólar PTAX — Banco Central', 'unknown', true, null, 0, null),
  ('icco', 'Preço internacional — ICCO', 'unknown', true, null, 0, null),
  ('weather', 'Clima — Open-Meteo ERA5-Land', 'unknown', false, null, 0, null),
  ('conab', 'Preço e custos — Conab', 'unknown', false, null, 0, null),
  ('ibge', 'Produção municipal — IBGE/SIDRA', 'unknown', false, null, 0, null)
on conflict (source) do nothing;

update source_status
set latest_observation_date = (select max(observation_date) from market_prices_daily where source = 'seagri'),
    row_count = (select count(*) from market_prices_daily where source = 'seagri'),
    status = case
      when (select max(observation_date) from market_prices_daily where source = 'seagri') >= current_date - 5 then 'healthy'
      else 'stale'
    end,
    updated_at = now()
where source = 'seagri' and last_run_at is null;

update source_status
set latest_observation_date = (select max(observation_date) from market_prices_daily where source = 'icco'),
    row_count = (select count(*) from market_prices_daily where source = 'icco'),
    status = case
      when (select max(observation_date) from market_prices_daily where source = 'icco') >= current_date - 5 then 'healthy'
      else 'stale'
    end,
    updated_at = now()
where source = 'icco' and last_run_at is null;

update source_status
set latest_observation_date = (select max(observation_date) from exchange_rates_daily where source = 'bcb'),
    row_count = (select count(*) from exchange_rates_daily where source = 'bcb'),
    status = case
      when (select max(observation_date) from exchange_rates_daily where source = 'bcb') >= current_date - 5 then 'healthy'
      else 'stale'
    end,
    updated_at = now()
where source = 'bcb' and last_run_at is null;

update source_status
set latest_observation_date = (select max(observation_date) from weather_daily where source = 'open_meteo'),
    row_count = (select count(*) from weather_daily where source = 'open_meteo'),
    status = case when exists (select 1 from weather_daily where source = 'open_meteo') then 'stale' else 'unknown' end,
    updated_at = now()
where source = 'weather' and last_run_at is null;

update source_status
set row_count = (select count(*) from producer_prices_monthly where source = 'conab')
              + (select count(*) from production_costs where source = 'conab'),
    status = case
      when exists (select 1 from producer_prices_monthly where source = 'conab')
        or exists (select 1 from production_costs where source = 'conab') then 'stale'
      else 'unknown'
    end,
    updated_at = now()
where source = 'conab' and last_run_at is null;

update source_status
set latest_observation_date = (select make_date(max(year), 12, 31) from municipal_production_annual where source = 'ibge_sidra'),
    row_count = (select count(*) from municipal_production_annual where source = 'ibge_sidra'),
    status = case when exists (select 1 from municipal_production_annual where source = 'ibge_sidra') then 'stale' else 'unknown' end,
    updated_at = now()
where source = 'ibge' and last_run_at is null;
