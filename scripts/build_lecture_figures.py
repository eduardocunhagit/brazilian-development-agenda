from pathlib import Path
from datetime import date
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "brazilian_development_agenda_assets"
DATA = OUT / "data"
API = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
SESSION = requests.Session()
SESSION.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
)))

NAVY = "#17324D"
GREEN = "#1B7F5A"
GOLD = "#E3A72F"
BRICK = "#B84A4A"
GRAY = "#66717A"
LIGHT = "#EAF2F6"


def bcb(code, start, end, name):
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    parts = []
    cursor = start
    while cursor <= end:
        stop = min(cursor + pd.DateOffset(years=4), end)
        params = {
            "formato": "json",
            "dataInicial": cursor.strftime("%d/%m/%Y"),
            "dataFinal": stop.strftime("%d/%m/%Y"),
        }
        response = SESSION.get(API.format(code=code), params=params, timeout=60)
        response.raise_for_status()
        payload = response.json()
        if payload:
            parts.append(pd.DataFrame(payload))
        cursor = stop + pd.Timedelta(days=1)
    frame = pd.concat(parts, ignore_index=True)
    frame["date"] = pd.to_datetime(frame["data"], dayfirst=True)
    frame["value"] = pd.to_numeric(frame["valor"], errors="coerce")
    frame = frame[["date", "value"]].dropna().drop_duplicates("date").sort_values("date")
    frame.to_csv(DATA / f"bcb_sgs_{code}_{name}.csv", index=False)
    return frame


def base_axis(ax, ylabel):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#AAB2B8")
    ax.grid(axis="y", color="#DCE3E7", linewidth=.7)
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_ylabel(ylabel, color=NAVY, fontsize=10)
    ax.margins(x=.01)


def save(fig, name):
    fig.tight_layout(pad=.8)
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_ipca(ipca):
    monthly = ipca.set_index("date")["value"].sort_index()
    annual = ((1 + monthly / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
    annual = annual.loc["1996":]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(annual.index, annual, color=BRICK, linewidth=2)
    ax.axhline(3, color=GREEN, linewidth=1.2, linestyle="--")
    ax.text(pd.Timestamp("2025-11-01"), 3.6, "3% target", color=GREEN, fontsize=8, ha="right")
    base_axis(ax, "12-month inflation (%)")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_ipca_12m.pdf")
    return annual


def plot_ipca_pre_post_real(ipca):
    monthly = ipca.set_index("date")["value"].sort_index()
    annual = ((1 + monthly / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
    before = annual.loc["1981-01-01":"1994-06-01"]
    after = annual.loc["1995-07-01":]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.65), gridspec_kw={"width_ratios": [1, 1.45]})
    axes[0].plot(before.index, before, color=BRICK, linewidth=1.8)
    axes[0].set_title("Before the Real", color=NAVY, fontsize=11, fontweight="bold")
    axes[0].xaxis.set_major_locator(mdates.YearLocator(4))
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    base_axis(axes[0], "12-month inflation (%)")

    axes[1].plot(after.index, after, color=GREEN, linewidth=1.8)
    axes[1].axhline(3, color=NAVY, linewidth=1.1, linestyle="--")
    axes[1].text(pd.Timestamp("2025-10-01"), 3.55, "3% target", color=NAVY, fontsize=8, ha="right")
    axes[1].set_title("Twelve months fully under the Real", color=NAVY, fontsize=11, fontweight="bold")
    axes[1].xaxis.set_major_locator(mdates.YearLocator(5))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    base_axis(axes[1], "12-month inflation (%)")
    save(fig, "fig_ipca_pre_post_real.pdf")


def plot_fx(fx):
    annual = fx.set_index("date")["value"].loc["1995":]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.axvspan(pd.Timestamp("1995-03-01"), pd.Timestamp("1999-01-15"), color=GOLD, alpha=.18)
    ax.text(pd.Timestamp("1997-01-01"), annual.max() * .94, "bands", color=GRAY, fontsize=9, ha="center")
    ax.plot(annual.index, annual, color=NAVY, linewidth=1.8, marker="o", markersize=3)
    ax.axvline(pd.Timestamp("1999-01-15"), color=BRICK, linewidth=1, linestyle="--")
    base_axis(ax, "BRL per US dollar")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_brl_usd.pdf")


def plot_selic_ipca(selic, annual_ipca):
    policy = selic.set_index("date")["value"].resample("MS").last().loc["2000":]
    inflation = annual_ipca.loc["2000":]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(policy.index, policy, color=NAVY, linewidth=1.7, label="Selic target")
    ax.plot(inflation.index, inflation, color=BRICK, linewidth=1.7, label="IPCA, 12 months")
    base_axis(ax, "% per year")
    ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_selic_ipca.pdf")


def plot_gdp(gdp):
    gdp = gdp.assign(year=gdp["date"].dt.year).query("year >= 1995")
    colors = np.where(gdp["value"] >= 0, GREEN, BRICK)
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.bar(gdp["year"], gdp["value"], color=colors, width=.78)
    ax.axhline(0, color=GRAY, linewidth=.8)
    base_axis(ax, "real GDP growth (%)")
    ax.set_xticks(np.arange(1995, gdp["year"].max() + 1, 5))
    save(fig, "fig_real_gdp_growth.pdf")


def plot_reserves(reserves):
    monthly = reserves.set_index("date")["value"].resample("MS").last() / 1000
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.fill_between(monthly.index, monthly, color=LIGHT)
    ax.plot(monthly.index, monthly, color=GREEN, linewidth=2)
    base_axis(ax, "US$ billion")
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_reserves.pdf")


def plot_debt(debt):
    series = debt.set_index("date")["value"]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(series.index, series, color=BRICK, linewidth=2)
    ax.fill_between(series.index, series, series.min() - 3, color="#F6E6E6")
    base_axis(ax, "% of GDP")
    ax.xaxis.set_major_locator(mdates.YearLocator(3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_gross_debt.pdf")


def plot_unemployment(unemployment):
    series = unemployment.set_index("date")["value"]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(series.index, series, color=NAVY, linewidth=2)
    base_axis(ax, "unemployment rate (%)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_unemployment.pdf")


def plot_spread(spread):
    series = spread.set_index("date")["value"]
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(series.index, series, color=GOLD, linewidth=2)
    base_axis(ax, "percentage points")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "fig_credit_spread.pdf")


def plot_static():
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    names = ["Agriculture", "Industry", "Services"]
    values = [5.8, -0.4, 0.1]
    ax.barh(names, values, color=[GREEN, BRICK, GOLD])
    ax.axvline(0, color=GRAY, linewidth=.8)
    for i, value in enumerate(values):
        if value < 0:
            ax.text(value / 2, i, f"{value:.1f}", va="center", ha="center",
                    color="white", fontsize=10, fontweight="bold")
        else:
            ax.text(value + .12, i, f"{value:.1f}", va="center", ha="left",
                    color=NAVY, fontsize=10, fontweight="bold")
    base_axis(ax, "annual labor-productivity growth, 1996–2020 (%)")
    save(fig, "fig_sector_productivity.pdf")

    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    labels = ["Brazil", "OECD average"]
    values = [27, 69]
    ax.bar(labels, values, color=[BRICK, GREEN], width=.5)
    for i, value in enumerate(values):
        ax.text(i, value + 2, f"{value}%", ha="center", color=NAVY, fontsize=13, fontweight="bold")
    ax.set_ylim(0, 80)
    base_axis(ax, "students reaching basic mathematics proficiency")
    save(fig, "fig_pisa_math.pdf")

    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    years = [2000, 2023, 2070]
    values = [8.7, 15.6, 37.8]
    ax.plot(years, values, color=GREEN, linewidth=2, marker="o", markersize=7)
    for x, y in zip(years, values):
        ax.text(x, y + 1.4, f"{y:.1f}%", ha="center", color=NAVY, fontsize=10, fontweight="bold")
    ax.set_xlim(1996, 2074)
    ax.set_ylim(0, 43)
    base_axis(ax, "population aged 60 or older (%)")
    save(fig, "fig_ageing.pdf")

    years = np.arange(2014, 2025)
    registered = [30.2, 29.3, 30.8, 32.1, 28.2, 22.0, 23.9, 22.8, 22.1, 21.7, 20.1]
    estimated = [32.0, 31.1, 32.7, 33.8, 30.7, 25.5, 26.6, 25.3, 24.9, 23.5, 23.4]
    crime = pd.DataFrame({"year": years, "registered": registered, "ipea_estimated": estimated})
    crime.to_csv(DATA / "atlas_violence_2026_homicide_rates.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    ax.plot(years, registered, color=GRAY, linewidth=1.8, marker="o", label="Registered")
    ax.plot(years, estimated, color=BRICK, linewidth=2.2, marker="o", label="Ipea estimate")
    base_axis(ax, "homicides per 100,000 inhabitants")
    ax.set_xticks(years[::2])
    ax.legend(frameon=False, ncol=2, fontsize=9)
    save(fig, "fig_homicide_rates.pdf")

    labels = ["Population", "Urbanized inhabited area"]
    control = np.array([29.7, 14.0])
    influence = np.array([5.3, 4.1])
    neither = np.array([65.0, 81.9])
    territorial = pd.DataFrame({"domain": labels, "control": control,
                                "influence": influence, "neither": neither})
    territorial.to_csv(DATA / "geni_fogo_cruzado_territorial_control_2024.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.5, 3.55))
    y = np.arange(len(labels))
    ax.barh(y, control, color=BRICK, label="Control")
    ax.barh(y, influence, left=control, color=GOLD, label="Influence")
    ax.barh(y, neither, left=control + influence, color=LIGHT, label="Neither")
    for i in range(len(labels)):
        ax.text(control[i] / 2, i, f"{control[i]:.1f}%", ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
        ax.text(control[i] + influence[i] / 2, i, f"{influence[i]:.1f}%", ha="center",
                va="center", color=NAVY, fontsize=9, fontweight="bold")
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 100)
    base_axis(ax, "share (%)")
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(.5, 1.0), fontsize=9)
    save(fig, "fig_rio_territorial_control.pdf")


def write_sources():
    text = """# Data sources for the lecture figures

Data were retrieved on {today}. Raw API responses, after date and numeric parsing, are stored as CSV files in `data/`.

| Figure | Source |
|---|---|
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
""".format(today=date.today().isoformat())
    (OUT / "SOURCES.md").write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    ipca = bcb(433, "1980-01-01", today, "ipca_monthly")
    fx = bcb(3692, "1995-01-01", "2025-12-31", "brl_usd_year_end")
    selic = bcb(432, "1999-03-05", today, "selic_target_daily")
    gdp = bcb(7326, "1995-01-01", "2025-12-31", "real_gdp_growth_annual")
    reserves = bcb(13621, "1998-09-01", today, "reserves_cash_daily")
    debt = bcb(13762, "2006-12-01", today, "gross_debt_pct_gdp")
    unemployment = bcb(24369, "2012-03-01", today, "unemployment")
    spread = bcb(20783, "2011-03-01", today, "credit_spread")

    annual_ipca = plot_ipca(ipca)
    plot_ipca_pre_post_real(ipca)
    plot_fx(fx)
    plot_selic_ipca(selic, annual_ipca)
    plot_gdp(gdp)
    plot_reserves(reserves)
    plot_debt(debt)
    plot_unemployment(unemployment)
    plot_spread(spread)
    plot_static()
    write_sources()
    print(f"figures={len(list(OUT.glob('*.pdf')))} csv={len(list(DATA.glob('*.csv')))}")


if __name__ == "__main__":
    if "--ipca-only" in sys.argv:
        ipca = pd.read_csv(DATA / "bcb_sgs_433_ipca_monthly.csv", parse_dates=["date"])
        plot_ipca(ipca)
        plot_ipca_pre_post_real(ipca)
        write_sources()
        print(f"ipca_rows={len(ipca)}")
    else:
        main()
