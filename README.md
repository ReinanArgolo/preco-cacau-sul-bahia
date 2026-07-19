# Preço do cacau no Sul da Bahia

Pipeline reproduzível para integrar a cotação de cacau comum em Ilhéus com PTAX, referência internacional, preços e custos da Conab, clima e produção municipal. Os dados são persistidos no Supabase/PostgreSQL e analisados em um notebook executável com relatório HTML.

O primeiro produto é um painel público para pequenos produtores. A modelagem fica
automaticamente bloqueada até a série local possuir ao menos 750 datas válidas,
aproximadamente três anos e disponibilidade temporal auditável.

## Arquitetura

```text
Seagri ─┐
BCB ────┤
ICCO ───┤
Conab ──┼─> coletores -> validação -> PostgreSQL/Supabase
Clima ──┤                              │
IBGE ───┘                              ├─> dataset Parquet -> notebook -> HTML
                                       └─> dashboard Next.js somente leitura
```

A ICE possui um adaptador explícito, mas permanece desativada até existir licença. O projeto não contorna paywalls nem inventa uma cotação de Gandu.

## Instalação

Requer Python 3.12–3.14 e PostgreSQL/Supabase.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[analysis,dev]'
cp .env.example .env
```

Preencha `SUPABASE_DB_URL` com a conexão Pooler do projeto Supabase. Para o frontend, copie `web/.env.example` para `web/.env.local`. Arquivos `.env*` reais não devem ser commitados.

O frontend usa os pacotes recomendados pelo Supabase:

```bash
cd web
npm install
npm run dev
```

Opcionalmente, ferramentas de programação assistida podem instalar as instruções oficiais do Supabase com `npx skills add supabase/agent-skills`. Isso não é necessário para executar o projeto.

## Uso

```bash
python -m cocoa_data migrate
python -m cocoa_data supabase-check
python -m cocoa_data backfill --source all
python -m cocoa_data collect --source all
python -m cocoa_data quality-check
python -m cocoa_data build-analysis-dataset
python -m cocoa_data render-report
python -m cocoa_data model-readiness
```

Também é possível limitar uma fonte e período:

```bash
python -m cocoa_data collect --source seagri --start 2026-01-01 --end 2026-07-18
```

O relatório final é salvo em `data/reports/analise_integrada_cacau.html`.
A síntese de prontidão para modelagem fica em
[`data/reports/analise_inicial.md`](data/reports/analise_inicial.md).

`model-readiness` retorna código `2` enquanto o gate estiver bloqueado. Isso é
intencional: nenhum treinamento deve ser incluído no pipeline antes de o comando
retornar `ready: true`.

## Painel público

O aplicativo Next.js possui:

- `/`: cotação de Ilhéus, paridade, base, datas usadas e alerta de defasagem;
- `/historico`: séries alinhadas somente por data exata;
- `/fontes`: cobertura e saúde sanitizada das coletas;
- `/metodologia`: interpretação, limitações e aviso de uso informativo;
- `/api/dados.csv`: exportação dos dados públicos;
- `/api/health`: smoke test da conexão de leitura.

Em telas pequenas, navegação, cartões, gráfico e tabelas se adaptam sem esconder a
data de referência. Ausência de dados é mostrada explicitamente; não há interpolação
silenciosa entre fontes incompatíveis.

## Supabase e segurança

- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` é usada apenas para leitura no navegador e é protegida por políticas RLS.
- O pipeline Python grava diretamente pelo `SUPABASE_DB_URL`, mantido em secrets locais e do GitHub.
- Não use uma chave `secret` ou `service_role` em variável `NEXT_PUBLIC_*`.
- A migração concede ao papel anônimo somente `SELECT` nas tabelas analíticas; execuções e eventos internos não são públicos.
- Todas as tabelas do schema `public`, inclusive as internas, têm RLS habilitada.
- `GET /api/health` valida a conexão de leitura usada pelo dashboard sem expor dados ou credenciais.

### Ativação do banco remoto

1. Aplique `migrations/001_initial.sql` no projeto Supabase pelo MCP autenticado.
2. Obtenha a conexão **Transaction Pooler** em `Connect > ORMs` no painel do projeto e grave-a apenas em `SUPABASE_DB_URL`.
3. Execute `python -m cocoa_data supabase-check` para confirmar conexão e schema.
4. Execute `python -m cocoa_data backfill --source all` para carregar o histórico inicial.
5. Verifique `http://localhost:3000/api/health` e então abra o dashboard.

## Operação no GitHub

Os workflows são separados por responsabilidade:

- `CI`: Ruff, Pytest, migrations em PostgreSQL isolado e build TypeScript;
- `Coleta diária`: dias úteis às 18h30 de Brasília, qualidade e issues deduplicadas;
- `Dataset e relatório`: execução após coleta saudável ou manual, com artefatos por 30 dias.

Configure somente `SUPABASE_DB_URL` em **Settings > Secrets and variables > Actions**.
Falhas de uma fonte criam ou atualizam uma única issue `Falha de coleta: <fonte>`;
a issue é fechada quando a fonte se recupera.

## Publicação na Vercel

Ao importar o repositório, escolha `web` como **Root Directory** e configure:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
```

Essas duas variáveis são públicas por definição. Não configure `SUPABASE_DB_URL`,
`service_role` ou qualquer chave secreta no frontend. Após o primeiro deploy, confirme
que `/api/health` retorna HTTP 200 e mantenha deploy automático da branch `main`.

## Contrato temporal

Todas as tabelas analíticas possuem `published_at`, `available_at`, `revision` e
`information_set`. Sem horário oficial, o dado diário é considerado disponível apenas
no dia seguinte. Reanálise recebe `information_set = reanalysis`; Conab e IBGE sem data
histórica comprovada recebem `publication_date_unknown` e ficam fora de backtests.

`source_status` é a única tabela operacional de leitura pública. Ela contém apenas
estado sanitizado, sem URL interna, credencial ou stack trace. Execuções completas e
eventos de qualidade permanecem privados.

O `SUPABASE_DB_URL` é uma credencial de servidor. Ele nunca deve usar o prefixo
`NEXT_PUBLIC_`, entrar no Git ou ser enviado ao navegador.

## Limitações conhecidas

- A Seagri é HTML e pode mudar a estrutura sem aviso.
- A cobertura pública atual da ICCO é respeitada; histórico pago não é contornado.
- O portal mensal da Conab pode exigir parâmetros de sessão. Uma falha nessa fonte é marcada como degradada e não elimina os dados anteriores.
- ERA5-Land é reanálise climática e não representa a previsão disponível na data histórica.
- A cotação de Ilhéus é referência de mercado, não garantia do preço efetivamente pago ao produtor em Gandu.

## Próximos marcos

1. Recuperar ou documentar a indisponibilidade do histórico Seagri/ICCO de 2026.
2. Executar backfill reproduzível de Open-Meteo, IBGE/SIDRA e Conab.
3. Conferir manualmente os três movimentos locais extremos e registrar o resultado.
4. Observar cinco coletas úteis consecutivas sem falha silenciosa.
5. Só após o gate de 750 datas: implementar naive, drift e média móvel com walk-forward.
