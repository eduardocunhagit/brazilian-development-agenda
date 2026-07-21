# Data sources for the lecture figures

Data were retrieved on 2026-07-21. Raw API responses, after date and numeric parsing, are stored as CSV files in `data/`.

| Figure | Source |
|---|---|
| Income convergence | World Bank, WDI indicator NY.GDP.PCAP.KD (GDP per capita, constant 2015 US$); Brazil as a share of the United States |
| Brazil-Europe scale overlay | Image supplied in the lecture revision document; territorial area from IBGE, Territorial Areas 2025 |
| National scale and inequality | IBGE 2024 Population Estimates and PNAD Continuous 2024; World Bank WDI 2024 GDP |
| IPCA, 12 months | BCB SGS 433; monthly IPCA variation, compounded over 12 months |
| IPCA before and after the Real | BCB SGS 433; separate vertical scales for the pre- and post-Real periods |
| BRL per US dollar | BCB SGS 3692; selling rate at year-end |
| Selic and IPCA | BCB SGS 432 and 433 |
| Real GDP growth | BCB SGS 7326; IBGE source series |
| International reserves | BCB SGS 13621; cash concept, daily, monthly last observation |
| Gross general government debt | BCB SGS 13762; methodology used since 2008 |
| Unemployment | BCB SGS 24369; IBGE PNAD Continua source series |
| Credit spread | BCB SGS 20783; average spread on outstanding credit |
| Sector productivity | World Bank, *The Brazil of the Future*, 1996–2020 |
| PISA mathematics | OECD, PISA 2022 country note for Brazil |
| Population aged 60+ | IBGE Population Projections 2024 |
| Homicide rates | Ipea and FBSP, Atlas da Violencia 2026, based on SIM/Ministry of Health |
| Armed territorial control | GENI/UFF and Instituto Fogo Cruzado, Mapa Historico dos Grupos Armados 2025 |

BCB API endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.CODE/dados`.
World Bank API endpoint: `https://api.worldbank.org/v2/country/BRA;USA/indicator/NY.GDP.PCAP.KD`.

Data cutoff: 2026-07-21.
