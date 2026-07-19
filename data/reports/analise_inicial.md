# Análise inicial dos dados — antes da modelagem

Data de geração: 19/07/2026. Esta análise é descritiva e não constitui recomendação
de venda, compra ou retenção de cacau.

## Cobertura

| Conjunto | Linhas na origem | Período disponível |
|---|---:|---|
| Cotação Seagri/Ilhéus | 215 | 02/01/2025 a 15/12/2025 |
| Referência ICCO | 257 | 02/01/2025 a 31/12/2025 |
| PTAX/BCB | 284 | 02/01/2025 a 17/07/2026 |
| Clima | 0 | não carregado |
| Preço ao produtor/Conab | 0 | não carregado |
| Produção municipal/IBGE | 0 | não carregado |
| Custos de produção | 0 | não carregado |

A base analítica possui 290 datas, mas somente 215 datas têm simultaneamente preço
local, ICCO e PTAX. O período comum vai de 02/01/2025 a 15/12/2025.

## Estatísticas do período comum

| Indicador | Média | Mediana | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| Ilhéus (R$/arroba) | 646,12 | 723,00 | 260,00 | 943,95 |
| ICCO (US$/t) | 7.935,57 | 7.892,74 | 5.077,20 | 11.352,54 |
| PTAX (R$/US$) | 5,601 | 5,574 | 5,273 | 6,209 |
| Paridade bruta (R$/arroba) | 671,02 | 669,30 | 410,04 | 1.014,64 |
| Base local (R$/arroba) | -24,89 | -10,03 | -226,34 | 172,34 |
| Base local (%) | -5,59% | -1,72% | -42,22% | 24,20% |

Na última data local disponível, 15/12/2025, Ilhéus estava em R$ 410,00 por
arroba, a paridade bruta em R$ 472,17 e a base em -R$ 62,17 (-13,17%). Isso é uma
referência histórica, não uma cotação atual.

## Relações observadas

- A correlação contemporânea entre os retornos de Ilhéus e da paridade foi 0,363.
- O sinal dos movimentos coincidiu em aproximadamente 60,3% das datas comparáveis.
- A correlação absoluta mais alta entre defasagens de -10 a +10 ocorreu na
  defasagem zero, também em 0,363.
- A volatilidade anualizada descritiva foi 78,9% para Ilhéus e 47,7% para a paridade.
- Foram encontrados 3 retornos locais acima de três desvios-padrão em magnitude;
  esses pontos precisam de validação contra a publicação original.

Essas estatísticas não demonstram causalidade. A base local pode incorporar qualidade,
umidade, fermentação, prazo de pagamento, frete, comprador, liquidez e condições
regionais que ainda não estão representadas.

## Sazonalidade

Os resultados mensais não devem ser tratados como sazonalidade estrutural, pois existe
apenas um ano de preço local. Setembro possui apenas 9 retornos e dezembro apenas 10,
o que torna as médias especialmente instáveis.

## Decisão de prontidão

**Modelagem preditiva ainda não liberada.** Antes de treinar modelos, o projeto deve:

1. ampliar o histórico local para mais anos ou documentar formalmente que a Seagri não
   os fornece;
2. carregar e validar clima, produção municipal, preços da Conab e custos;
3. confirmar os três movimentos extremos na fonte;
4. manter a auditoria de `available_at`, agora preenchido para as séries existentes;
5. definir calendário de mercado, tratamento de dias sem cotação e limite de
   carregamento para frente;
6. somente então criar baseline naive e walk-forward validation.

Com apenas 215 observações comuns, separar treino, validação e teste para seis
horizontes produziria estimativas instáveis e um risco elevado de sobreajuste.

O gate automatizado exige simultaneamente 750 datas locais válidas, intervalo de pelo
menos 1.095 dias e `information_set = historical_observation` com `available_at`
preenchido. Na data desta análise, ele permanece corretamente bloqueado.
