import streamlit as st
import yfinance as yf
import os
import requests
import pandas as pd
import hashlib
import random
import datetime
import altair as alt
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
from yahooquery import search

if "last_tab" not in st.session_state:
    st.session_state.last_tab = None
def search_ticker(query):
    """Recherche dynamique d'entreprise/ticker via Yahoo Finance."""
    try:
        results = search(query)
        companies = []
        for r in results.get('quotes', []):
            if 'symbol' in r and 'shortname' in r:
                companies.append(f"{r['symbol']} - {r['shortname']}")
        return companies
    except Exception:
        return []
# Liste des principaux indices boursiers mondiaux
MARKET_INDEXES = {
    "S&P 500 (USA)": "^GSPC",
    "NASDAQ (USA)": "^IXIC",
    "Dow Jones (USA)": "^DJI",
    "Russell 2000 (USA)": "^RUT",
    "CAC 40 (France)": "^FCHI",
    "DAX (Allemagne)": "^GDAXI",
    "FTSE 100 (UK)": "^FTSE",
    "IBEX 35 (Espagne)": "^IBEX",
    "AEX (Pays-Bas)": "^AEX",
    "BEL 20 (Belgique)": "^BFX",
    "SMI (Suisse)": "^SSMI",
    "FTSE MIB (Italie)": "FTSEMIB.MI",
    "OMX Stockholm 30 (Suède)": "^OMXS30",
    "Nikkei 225 (Japon)": "^N225",
    "TOPIX (Japon)": "^TOPX",
    "Hang Seng (Hong Kong)": "^HSI",
    "SSE Composite (Chine)": "000001.SS",
    "Shenzhen (Chine)": "399001.SZ",
    "Kospi (Corée du Sud)": "^KS11",
    "ASX 200 (Australie)": "^AXJO",
    "BSE Sensex (Inde)": "^BSESN",
    "Nifty 50 (Inde)": "^NSEI",
    "TSX (Canada)": "^GSPTSE",
    "IPC (Mexique)": "^MXX",
    "Bovespa (Brésil)": "^BVSP",
    "MERVAL (Argentine)": "^MERV",
    "TA-35 (Israël)": "TA35.TA",
    "JSE Top 40 (Afrique du Sud)": "J200.JO",
    "EGX 30 (Égypte)": "EGX30.CA",
    "ADX (Abu Dhabi)": "ADXI.AD",
    "Tadawul (Arabie Saoudite)": "TASI.SR",
    "RTS (Russie)": "RTSI.ME"
}

def get_market_data(tickers):
    data = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            last_close = hist["Close"][-1] if not hist.empty else None
            perf_1m = ((hist["Close"][-1] / hist["Close"][-22]) - 1) * 100 if len(hist) > 22 else None
            perf_6m = ((hist["Close"][-1] / hist["Close"][0]) - 1) * 100 if len(hist) > 1 else None
            data.append({
                "Marché": name,
                "Symbole": symbol,
                "Dernière clôture": f"{last_close:.2f}" if last_close else "N/A",
                "Perf. 1 mois (%)": f"{perf_1m:.2f}" if perf_1m else "N/A",
                "Perf. 6 mois (%)": f"{perf_6m:.2f}" if perf_6m else "N/A"
            })
        except Exception as e:
            data.append({
                "Marché": name,
                "Symbole": symbol,
                "Dernière clôture": "N/A",
                "Perf. 1 mois (%)": "N/A",
                "Perf. 6 mois (%)": "N/A"
            })
    return pd.DataFrame(data)

def get_ai_market_advice(market_df):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Clé API Groq non trouvée."
    # Conversion du DataFrame en markdown ou texte simple si tabulate n'est pas dispo
    try:
        table_str = market_df.to_markdown(index=False)
    except ImportError:
        table_str = market_df.to_string(index=False)
    prompt = (
        "Tu es un expert en marchés financiers. Voici les performances récentes de plusieurs indices boursiers :\n"
        f"{table_str}\n"
        "En te basant sur ces données, conseille sur quel marché il serait le plus intéressant d'investir actuellement et explique pourquoi, en français, de façon concise et professionnelle."
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 500
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Erreur Groq : {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erreur : {e}"
COMPANIES_BY_COUNTRY = {
    "États-Unis": [
        {"ticker": "AAPL", "name": "Apple Inc."},
        {"ticker": "MSFT", "name": "Microsoft Corporation"},
        {"ticker": "GOOGL", "name": "Alphabet Inc."},
        {"ticker": "AMZN", "name": "Amazon.com Inc."},
        {"ticker": "TSLA", "name": "Tesla Inc."},
        {"ticker": "META", "name": "Meta Platforms Inc."},
        {"ticker": "BRK-B", "name": "Berkshire Hathaway Inc."},
        {"ticker": "NVDA", "name": "NVIDIA Corporation"},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
        {"ticker": "V", "name": "Visa Inc."},
        {"ticker": "UNH", "name": "UnitedHealth Group"},
        {"ticker": "JNJ", "name": "Johnson & Johnson"},
        {"ticker": "WMT", "name": "Walmart Inc."},
        {"ticker": "PG", "name": "Procter & Gamble"},
        {"ticker": "MA", "name": "Mastercard Inc."},
        {"ticker": "HD", "name": "Home Depot Inc."},
        {"ticker": "BAC", "name": "Bank of America"},
        {"ticker": "DIS", "name": "Walt Disney Co."},
        {"ticker": "PFE", "name": "Pfizer Inc."},
        {"ticker": "KO", "name": "Coca-Cola Co."},
    ],
    "Chine": [
        {"ticker": "BABA", "name": "Alibaba Group"},
        {"ticker": "TCEHY", "name": "Tencent Holdings"},
        {"ticker": "JD", "name": "JD.com"},
        {"ticker": "BIDU", "name": "Baidu Inc."},
        {"ticker": "PDD", "name": "Pinduoduo Inc."},
        {"ticker": "601318.SS", "name": "Ping An Insurance"},
        {"ticker": "601857.SS", "name": "PetroChina"},
        {"ticker": "601398.SS", "name": "ICBC"},
        {"ticker": "601988.SS", "name": "Bank of China"},
        {"ticker": "601939.SS", "name": "China Construction Bank"},
        {"ticker": "600028.SS", "name": "Sinopec"},
        {"ticker": "600519.SS", "name": "Kweichow Moutai"},
        {"ticker": "000001.SZ", "name": "Ping An Bank"},
        {"ticker": "000333.SZ", "name": "Midea Group"},
        {"ticker": "000651.SZ", "name": "Gree Electric"},
        {"ticker": "002594.SZ", "name": "BYD Company"},
        {"ticker": "00700.HK", "name": "Tencent Holdings (HK)"},
        {"ticker": "02318.HK", "name": "Ping An Insurance (HK)"},
        {"ticker": "00941.HK", "name": "China Mobile"},
        {"ticker": "03988.HK", "name": "Bank of China (HK)"},
    ],
    "Japon": [
        {"ticker": "7203.T", "name": "Toyota Motor"},
        {"ticker": "6758.T", "name": "Sony Group"},
        {"ticker": "9984.T", "name": "SoftBank Group"},
        {"ticker": "8306.T", "name": "Mitsubishi UFJ Financial"},
        {"ticker": "7267.T", "name": "Honda Motor"},
        {"ticker": "9432.T", "name": "NTT"},
        {"ticker": "8035.T", "name": "Tokyo Electron"},
        {"ticker": "6861.T", "name": "Keyence"},
        {"ticker": "7974.T", "name": "Nintendo"},
        {"ticker": "6902.T", "name": "Denso"},
        {"ticker": "8766.T", "name": "Tokio Marine"},
        {"ticker": "4502.T", "name": "Takeda Pharmaceutical"},
        {"ticker": "8411.T", "name": "Mizuho Financial"},
        {"ticker": "6098.T", "name": "Recruit Holdings"},
        {"ticker": "7751.T", "name": "Canon Inc."},
        {"ticker": "8058.T", "name": "Mitsubishi Corporation"},
        {"ticker": "9433.T", "name": "KDDI Corporation"},
        {"ticker": "4661.T", "name": "Oriental Land"},
        {"ticker": "5108.T", "name": "Bridgestone"},
        {"ticker": "6501.T", "name": "Hitachi"},
    ],
    "Allemagne": [
        {"ticker": "SAP.DE", "name": "SAP SE"},
        {"ticker": "ALV.DE", "name": "Allianz SE"},
        {"ticker": "BAS.DE", "name": "BASF SE"},
        {"ticker": "BAYN.DE", "name": "Bayer AG"},
        {"ticker": "BMW.DE", "name": "BMW AG"},
        {"ticker": "DAI.DE", "name": "Mercedes-Benz Group"},
        {"ticker": "DBK.DE", "name": "Deutsche Bank"},
        {"ticker": "DTE.DE", "name": "Deutsche Telekom"},
        {"ticker": "FRE.DE", "name": "Fresenius SE"},
        {"ticker": "HEI.DE", "name": "HeidelbergCement"},
        {"ticker": "HEN3.DE", "name": "Henkel AG"},
        {"ticker": "IFX.DE", "name": "Infineon Technologies"},
        {"ticker": "LHA.DE", "name": "Lufthansa"},
        {"ticker": "LIN.DE", "name": "Linde plc"},
        {"ticker": "MRK.DE", "name": "Merck KGaA"},
        {"ticker": "MUV2.DE", "name": "Munich Re"},
        {"ticker": "RWE.DE", "name": "RWE AG"},
        {"ticker": "SIE.DE", "name": "Siemens AG"},
        {"ticker": "VOW3.DE", "name": "Volkswagen AG"},
        {"ticker": "ZAL.DE", "name": "Zalando SE"},
    ],
    "Inde": [
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries"},
        {"ticker": "TCS.NS", "name": "Tata Consultancy Services"},
        {"ticker": "HDFCBANK.NS", "name": "HDFC Bank"},
        {"ticker": "INFY.NS", "name": "Infosys"},
        {"ticker": "ICICIBANK.NS", "name": "ICICI Bank"},
        {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
        {"ticker": "SBIN.NS", "name": "State Bank of India"},
        {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel"},
        {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
        {"ticker": "ITC.NS", "name": "ITC Limited"},
        {"ticker": "LT.NS", "name": "Larsen & Toubro"},
        {"ticker": "AXISBANK.NS", "name": "Axis Bank"},
        {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance"},
        {"ticker": "MARUTI.NS", "name": "Maruti Suzuki"},
        {"ticker": "SUNPHARMA.NS", "name": "Sun Pharma"},
        {"ticker": "ASIANPAINT.NS", "name": "Asian Paints"},
        {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement"},
        {"ticker": "TITAN.NS", "name": "Titan Company"},
        {"ticker": "WIPRO.NS", "name": "Wipro"},
        {"ticker": "ONGC.NS", "name": "ONGC"},
    ],
    "Royaume-Uni": [
        {"ticker": "HSBA.L", "name": "HSBC Holdings"},
        {"ticker": "AZN.L", "name": "AstraZeneca"},
        {"ticker": "SHEL.L", "name": "Shell plc"},
        {"ticker": "GSK.L", "name": "GSK plc"},
        {"ticker": "ULVR.L", "name": "Unilever"},
        {"ticker": "BP.L", "name": "BP plc"},
        {"ticker": "RIO.L", "name": "Rio Tinto"},
        {"ticker": "BATS.L", "name": "British American Tobacco"},
        {"ticker": "DGE.L", "name": "Diageo"},
        {"ticker": "LSEG.L", "name": "London Stock Exchange"},
        {"ticker": "BARC.L", "name": "Barclays"},
        {"ticker": "VOD.L", "name": "Vodafone Group"},
        {"ticker": "NG.L", "name": "National Grid"},
        {"ticker": "PRU.L", "name": "Prudential"},
        {"ticker": "LLOY.L", "name": "Lloyds Banking Group"},
        {"ticker": "SMIN.L", "name": "Smiths Group"},
        {"ticker": "AAL.L", "name": "Anglo American"},
        {"ticker": "TSCO.L", "name": "Tesco"},
        {"ticker": "IMB.L", "name": "Imperial Brands"},
        {"ticker": "SGE.L", "name": "Sage Group"},
    ],
    "France": [
        {"ticker": "MC.PA", "name": "LVMH Moët Hennessy Louis Vuitton"},
        {"ticker": "OR.PA", "name": "L'Oréal"},
        {"ticker": "SAN.PA", "name": "Sanofi"},
        {"ticker": "AIR.PA", "name": "Airbus"},
        {"ticker": "BNP.PA", "name": "BNP Paribas"},
        {"ticker": "ENGI.PA", "name": "Engie"},
        {"ticker": "CAP.PA", "name": "Capgemini"},
        {"ticker": "RMS.PA", "name": "Hermès International"},
        {"ticker": "TTE.PA", "name": "TotalEnergies SE"},
        {"ticker": "DG.PA", "name": "Danone"},
        {"ticker": "VIE.PA", "name": "Veolia Environnement"},
        {"ticker": "GLE.PA", "name": "Société Générale"},
        {"ticker": "AC.PA", "name": "Accor SA"},
        {"ticker": "KER.PA", "name": "Kering SA"},
        {"ticker": "EDF.PA", "name": "Électricité de France (EDF)"},
        {"ticker": "SU.PA", "name": "Schneider Electric SE"},
        {"ticker": "VIV.PA", "name": "Vivendi SE"},
        {"ticker": "STLA.PA", "name": "Stellantis NV"},
        {"ticker": "PUB.PA", "name": "Publicis Groupe SA"},
    ],
    "Italie": [
        {"ticker": "ENI.MI", "name": "Eni S.p.A."},
        {"ticker": "ISP.MI", "name": "Intesa Sanpaolo"},
        {"ticker": "UCG.MI", "name": "UniCredit S.p.A."},
        {"ticker": "FCA.MI", "name": "Fiat Chrysler Automobiles"},
        {"ticker": "LUX.MI", "name": "Luxottica Group"},
        {"ticker": "SPM.MI", "name": "Salvatore Ferragamo"},
        {"ticker": "ATL.MI", "name": "Atlantia S.p.A."},
        {"ticker": "G.MI", "name": "Generali Group"},
        {"ticker": "ENEL.MI", "name": "Enel S.p.A."},
        {"ticker": "STLA.MI", "name": "Stellantis NV (Italian listing)"},
    ],
    "Canada": [
        {"ticker": "RY.TO", "name": "Royal Bank of Canada"},
        {"ticker": "TD.TO", "name": "Toronto-Dominion Bank"},
        {"ticker": "BNS.TO", "name": "Bank of Nova Scotia"},
        {"ticker": "CM.TO", "name": "Canadian Imperial Bank of Commerce"},
        {"ticker": "ENB.TO", "name": "Enbridge Inc."},
        {"ticker": "TRP.TO", "name": "TC Energy Corporation"},
        {"ticker": "BMO.TO", "name": "Bank of Montreal"},
        {"ticker": "SU.TO", "name": "Suncor Energy Inc."},
        {"ticker": "CNQ.TO", "name": "Canadian Natural Resources Limited"},
        {"ticker": "CP.TO", "name": "Canadian Pacific Railway Limited"},
        {"ticker": "SHOP.TO", "name": "Shopify Inc."},
        {"ticker": "BAM-A.TO", "name": "Brookfield Asset Management Inc."},
        {"ticker": "ABX.TO", "name": "Barrick Gold Corporation"},
        {"ticker": "CNR.TO", "name": "Canadian National Railway Company"},
        {"ticker": "ATD-B.TO", "name": "Alimentation Couche-Tard Inc."},
    ],
    "Corée du Sud": [
        {"ticker": "005930.KS", "name": "Samsung Electronics"},
        {"ticker": "000660.KS", "name": "SK Hynix"},
        {"ticker": "051910.KS", "name": "LG Chem"},
        {"ticker": "005380.KS", "name": "Hyundai Motor"},
        {"ticker": "035420.KS", "name": "Naver Corporation"},
        {"ticker": "005490.KS", "name": "POSCO Holdings"},
        {"ticker": "068270.KS", "name": "Celltrion"},
        {"ticker": "017670.KS", "name": "KT Corporation"},
        {"ticker": "012330.KS", "name": "Samsung Biologics"},
        {"ticker": "096770.KS", "name": "Kakao Corp."},
    ]
}
def get_alpha_vantage_overview(symbol):
    """Récupère les données fondamentales Alpha Vantage pour un symbole donné."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "Symbol" in data:
                return data
    except Exception:
        pass
    return None

def compare_field(yf_info, av_info, field_yf, field_av, tolerance=0.15):
    """Compare un champ entre Yahoo Finance et Alpha Vantage, True si cohérent ou non comparable."""
    try:
        v1 = float(yf_info.get(field_yf, 0))
        v2 = float(av_info.get(field_av, 0))
        if v1 == 0 or v2 == 0:
            return True  # Non comparable
        return abs(v1 - v2) / max(abs(v1), abs(v2)) < tolerance
    except Exception:
        return True
def company_header(info, av_info, color):
    """
    Affiche un en-tête résumé pour une entreprise avec une couleur d'accent.
    Affiche aussi une alerte si les données divergent entre Yahoo et Alpha Vantage.
    """
    company_name = info.get('shortName', info.get('symbol', 'Entreprise'))
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:8px;color:white;font-size:20px;font-weight:bold;'>{company_name}</div>",
        unsafe_allow_html=True
    )
    # Vérification de la fiabilité des données
    show_comparison_alerts(info, av_info, company_name)
    
def show_comparison_alerts(info, av_info, label):
    """Affiche une alerte si les données divergent entre Yahoo et Alpha Vantage."""
    if not av_info:
        st.info(f"Pas de données Alpha Vantage pour {label}.")
        return
    # Capitalisation boursière
    if not compare_field(info, av_info, "marketCap", "MarketCapitalization"):
        st.warning(f"⚠️ Divergence sur la capitalisation boursière de {label} entre Yahoo et Alpha Vantage : "
                   f"{info.get('marketCap', 'N/A')} vs {av_info.get('MarketCapitalization', 'N/A')}")
    # Chiffre d'affaires
    if not compare_field(info, av_info, "totalRevenue", "RevenueTTM"):
        st.warning(f"⚠️ Divergence sur le chiffre d'affaires de {label} entre Yahoo et Alpha Vantage : "
                   f"{info.get('totalRevenue', 'N/A')} vs {av_info.get('RevenueTTM', 'N/A')}")
    # Bénéfice net
    if not compare_field(info, av_info, "netIncomeToCommon", "NetIncomeTTM"):
        st.warning(f"⚠️ Divergence sur le bénéfice net de {label} entre Yahoo et Alpha Vantage : "
                   f"{info.get('netIncomeToCommon', 'N/A')} vs {av_info.get('NetIncomeTTM', 'N/A')}")

# Configuration de la page Streamlit
st.set_page_config(page_title="Comparateur finance avancé", page_icon="📊", layout="wide")

# Titre et description de l'application
st.title("📊 Comparateur avancé en finance pour investissement")
st.markdown("""
Compare entreprises et marchés en détail avec notes, graphiques et analyse IA en français pour t'aider à investir intelligemment.
""")

st.divider()


# ... (code précédent)

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    selected_tab = st.radio(
        "Choisir une section",
        [
            "Comparaison d'entreprises",
            "Analyse IA",
            "Comparaison Globale",
            "Le Cas du Jour",
            "Comparateur de marchés",
            "Comparateur de marchés (2 marchés)"
        ],
        key="selected_tab"
    )
    st.markdown("---")
    st.markdown("Développé par [The Finalyst]")  # Replace with your name or organization

# Réinitialisation de l'état à chaque changement de tab
if "last_tab" not in st.session_state:
    st.session_state.last_tab = selected_tab

if st.session_state.last_tab != selected_tab:
    # Réinitialiser tous les états spécifiques à chaque onglet
    for key in list(st.session_state.keys()):
        if key not in ["selected_tab", "last_tab"]:
            del st.session_state[key]
    st.session_state.last_tab = selected_tab
    st.rerun()


# Recherche dynamique pour entreprise 1
query1 = st.text_input("🔎 Recherche d'entreprise ou ticker 1")
options1 = search_ticker(query1) if query1 and len(query1) > 2 else []
ticker1_full = st.selectbox("Résultats 1", options1, key="ticker1_select")
ticker1 = ticker1_full.split(" - ")[0] if ticker1_full else ""

# Recherche dynamique pour entreprise 2
query2 = st.text_input("🔍 Recherche d'entreprise ou ticker 2")
options2 = search_ticker(query2) if query2 and len(query2) > 2 else []
ticker2_full = st.selectbox("Résultats 2", options2, key="ticker2_select")
ticker2 = ticker2_full.split(" - ")[0] if ticker2_full else ""
# Fonctions utilitaires
def format_currency(value):
    """Formate les valeurs numériques en format monétaire lisible."""
    if value is None:
        return "N/A"
    try:
        v = float(value)
        if abs(v) > 1e9:
            return f"{v/1e9:.2f} Md"
        elif abs(v) > 1e6:
            return f"{v/1e6:.2f} M"
        elif abs(v) > 1e3:
            return f"{v:.2f} K"
        else:
            return f"{v:.2f}"
    except ValueError:
        return "N/A"

def score_financier(info):
    """Attribue une note financière basée sur divers indicateurs."""
    score = 0
    try:
        revenue = float(info.get("totalRevenue", 0))
        net_income = float(info.get("netIncomeToCommon", 0))
        marge_nette = net_income / revenue if revenue > 0 else 0
        if marge_nette > 0.1:
            score += 3
        elif marge_nette > 0.05:
            score += 2
        else:
            score += 1
    except (TypeError, ValueError):
        st.warning("Impossible de calculer la marge nette.")

    try:
        roe = float(info.get("returnOnEquity", 0))
        if roe > 0.15:
            score += 3
        elif roe > 0.07:
            score += 2
        else:
            score += 1
    except (TypeError, ValueError):
        st.warning("Impossible de calculer le ROE.")

    try:
        total_debt = float(info.get("totalDebt", 0))
        equity = float(info.get("totalStockholdersEquity", 1))
        leverage = total_debt / equity if equity != 0 else 10
        if leverage < 0.5:
            score += 2
        elif leverage < 1.0:
            score += 1
    except (TypeError, ValueError):
        st.warning("Impossible de calculer le ROE.")

    try:
        fcf = float(info.get("freeCashflow", 0))
        if fcf > 0:
            score += 2
    except (TypeError, ValueError):
        st.warning("Impossible de calculer le flux de trésorerie disponible.")

    return min(score, 10)

def afficher_infos(info, titre):
    """Affiche les informations financières de l'entreprise."""
    st.subheader(f"📈 {titre}")
    if not info:
        st.error("Informations non disponibles pour cette entreprise.")
        return

    st.write(f"- **Secteur** : {info.get('sector', 'N/A')}")
    st.write(f"- **Industrie** : {info.get('industry', 'N/A')}")
    st.write(f"- **Prix actuel** : {info.get('currentPrice', 'N/A')} USD")
    st.write(f"- **Capitalisation boursière** : {format_currency(info.get('marketCap'))} USD")
    st.write(f"- **Chiffre d'affaires annuel** : {format_currency(info.get('totalRevenue'))} USD")
    st.write(f"- **Bénéfice net** : {format_currency(info.get('netIncomeToCommon'))} USD")
    st.write(f"- **Bénéfice par action (EPS)** : {info.get('trailingEps', 'N/A')}")
    st.write(f"- **Ratio P/E** : {info.get('trailingPE', 'N/A')}")
    st.write(f"- **ROE** : {info.get('returnOnEquity', 'N/A')}")
    st.write(f"- **Dette totale** : {format_currency(info.get('totalDebt'))} USD")
    st.write(f"- **Flux de trésorerie libre** : {format_currency(info.get('freeCashflow'))} USD")

    try:
        totalRevenue = info.get('totalRevenue') or 1
        netIncomeToCommon = info.get('netIncomeToCommon') or 0
        totalDebt = info.get('totalDebt') or 0
        totalStockholdersEquity = info.get('totalStockholdersEquity') or 1

        marge = netIncomeToCommon / totalRevenue
        leverage = totalDebt / max(totalStockholdersEquity, 1)

        st.write(f"- **Marge nette estimée** : {marge:.2%}")
        st.write(f"- **Dette / Capitaux propres estimé** : {leverage:.2f}")
    except (TypeError, ValueError, ZeroDivisionError):
        st.write("- Ratios estimés indisponibles")

def radar_scores(info, av_info, label, color):
    # Exemples d'indicateurs (à adapter selon dispo)
    axes = ["Rentabilité", "Croissance", "Solidité", "Valorisation", "Dividende"]
    values = [
        float(info.get("returnOnEquity", 0) or 0) * 10,  # Rentabilité
        float(info.get("revenueGrowth", 0) or 0) * 100,  # Croissance
        100 - float(info.get("debtToEquity", 0) or 0),   # Solidité
        100 / float(info.get("trailingPE", 1) or 1),     # Valorisation
        float(info.get("dividendYield", 0) or 0) * 100   # Dividende
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=axes,
        fill='toself',
        name=label,
        line_color=color
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

def bar_compare(info1, info2, label1, label2):
    indicateurs = ["currentPrice", "marketCap", "totalRevenue", "netIncomeToCommon", "returnOnEquity"]
    noms = ["Prix actuel", "Capitalisation", "Chiffre d'affaires", "Bénéfice net", "ROE"]
    valeurs1 = [info1.get(x) or 0 for x in indicateurs]
    valeurs2 = [info2.get(x) or 0 for x in indicateurs]
    df = pd.DataFrame({
        "Indicateur": noms * 2,
        "Entreprise": [label1]*5 + [label2]*5,
        "Valeur": valeurs1 + valeurs2
    })
    fig = px.bar(df, x="Valeur", y="Indicateur", color="Entreprise", barmode="group", orientation="h",
                 color_discrete_sequence=["#00b4d8", "#ff006e"])
    st.plotly_chart(fig, use_container_width=True)

def show_price_timeline(ticker1, ticker2, label1, label2):
    hist1 = yf.Ticker(ticker1).history(period="1y")["Close"]
    hist2 = yf.Ticker(ticker2).history(period="1y")["Close"]
    df = pd.DataFrame({
        "Date": hist1.index.append(hist2.index).unique(),
        label1: hist1.reindex(hist1.index.append(hist2.index).unique()),
        label2: hist2.reindex(hist1.index.append(hist2.index).unique())
    }).fillna(method="ffill")
    fig = px.line(df, x="Date", y=[label1, label2], labels={"value": "Cours de clôture"})
    st.plotly_chart(fig, use_container_width=True)

# Initialisation des états de session
if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = ""
if "infos1" not in st.session_state:
    st.session_state.infos1 = {}
if "infos2" not in st.session_state:
    st.session_state.infos2 = {}

# List of 10 largest countries by GDP (replace with actual data)
TOP_10_COUNTRIES = [
    "United States", "China", "Japan", "Germany", "India",
    "United Kingdom", "France", "Italy", "Canada", "South Korea"
]

# Mapping of country to a list of major companies (replace with actual data)
COUNTRY_TO_COMPANIES = {
    "United States": ["AAPL", "MSFT", "AMZN", "GOOGL", "BRK.B", "JPM", "V", "UNH", "JNJ", "XOM"],
    "China": ["BABA", "TCEHY", "JD", "BIDU", "PDD", "0941.HK", "601398.SS", "601288.SS", "601939.SS", "00700.HK"],
    "Japan": ["7203.T", "6758.T", "9984.T", "8306.T", "6954.T", "8316.T", "8031.T", "8766.T", "8604.T", "6501.T"],
    "Germany": ["VOW.DE", "SAP.DE", "SIE.DE", "BMW.DE", "ALV.DE", "DTE.DE", "BAYN.DE", "MBG.DE", "BAS.DE", "ADS.DE"],
    "India": ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS", "HDFC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS", "KOTAKBANK.NS"],
    "United Kingdom": ["SHEL.L", "HSBA.L", "AZN.L", "BP.L", "ULVR.L", "RIO.L", "GSK.L", "BATS.L", "DGE.L", "LSEG.L"],
    "France": ["LVMH.PA", "OR.PA", "SAN.PA", "RMS.PA", "TTE.PA", "MC.PA", "KER.PA", "CAP.PA", "BNP.PA", "GLE.PA"],
    "Italy": ["ENI.MI", "UCG.MI", "ISP.MI", "STM.MI", "G.MI", "ATL.MI", "SRG.MI", "RACE.MI", "PRY.MI", "MB.MI"],
    "Canada": ["RY.TO", "TD.TO", "CM.TO", "BMO.TO", "ENB.TO", "BNS.TO", "CP.TO", "CNR.TO", "TRP.TO", "BCE.TO"],
    "South Korea": ["005930.KS", "000660.KS", "051910.KS", "005380.KS", "035420.KS", "005490.KS", "068270.KS", "017670.KS", "012330.KS", "096770.KS"]
}

# Mapping of country to flag emoji
COUNTRY_FLAGS = {
    "United States": "🇺🇸",
    "China": "🇨🇳",
    "Japan": "🇯🇵",
    "Germany": "🇩🇪",
    "India": "🇮🇳",
    "United Kingdom": "🇬🇧",
    "France": "🇫🇷",
    "Italy": "🇮🇹",
    "Canada": "🇨🇦",
    "South Korea": "🇰🇷"
}

def assess_investment_potential(info):
    """Assess investment potential based on financial data."""
    potential = 0

    if info.get("returnOnEquity", 0) > 0.15:
        potential += 3
    elif info.get("returnOnEquity", 0) > 0.07:
        potential += 2
    else:
        potential += 1

    try:
        total_debt = float(info.get("totalDebt", 0))
        equity = float(info.get("totalStockholdersEquity", 1))
        leverage = total_debt / equity if equity != 0 else 10
        if leverage < 0.5:
            potential += 2
        elif leverage < 1.0:
            potential += 1
    except (TypeError, ValueError):
        st.warning("Impossible de calculer l'effet de levier.")

    if info.get("profitMargins", 0) > 0.1:
        potential += 2
    elif info.get("profitMargins", 0) > 0.05:
        potential += 1

    return min(potential, 10)

# Dictionary to store AI analysis results
AI_ANALYSIS_CACHE = {}

def get_ai_analysis(company_name, info, ranking_type):
    """Gets an AI analysis for a given company and ranking type, using a cache for consistency."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.info("Clé API Groq non trouvée. Ajoute-la dans Settings > Secrets sous le nom GROQ_API_KEY.")
        return "Clé API Groq non trouvée."

    # Create a hash of the company name, financial info, and ranking type to use as a cache key
    cache_key = hashlib.md5((company_name + str(info) + ranking_type).encode()).hexdigest()

    if cache_key in AI_ANALYSIS_CACHE:
        return AI_ANALYSIS_CACHE[cache_key]

    prompt = f"""Tu es un expert financier. Analyse les entreprises suivantes pour le classement "{ranking_type}".
Entreprise : {company_name}
Secteur : {info.get('sector', 'N/A')}
Industrie : {info.get('industry', 'N/A')}
Prix actuel : {info.get('currentPrice', 'N/A')} USD
Capitalisation boursière : {format_currency(info.get('marketCap'))} USD
Chiffre d'affaires annuel : {format_currency(info.get('totalRevenue'))} USD
Bénéfice net : {format_currency(info.get('netIncomeToCommon'))} USD
Bénéfice par action (EPS) : {info.get('trailingEps', 'N/A')}
Ratio P/E : {info.get('trailingPE', 'N/A')}
ROE : {info.get('returnOnEquity', 'N/A')}
Dette totale : {format_currency(info.get('totalDebt'))} USD
Flux de trésorerie libre : {format_currency(info.get('freeCashflow'))} USD

Explique pourquoi cette entreprise est bien classée pour "{ranking_type}" en français, de façon concise et professionnelle."""

    headers = {
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,  # Set temperature to 0 for consistent results
        "max_tokens": 500
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
            AI_ANALYSIS_CACHE[cache_key] = ai_response  # Store in cache
            return ai_response
        else:
            return f"Erreur Groq : {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erreur : {e}"

def perform_country_analysis(country):
    """Analyzes the companies for a given country and provides multiple rankings."""
    all_companies = []
    if country == "Monde":
        for companies in COUNTRY_TO_COMPANIES.values():
            all_companies.extend(companies)
    else:
        all_companies = COUNTRY_TO_COMPANIES.get(country)
    if not all_companies:
        st.warning(f"No companies found for {country}")
        return

    company_data = []
    for ticker in all_companies:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('shortName', ticker)
            financial_score = score_financier(info)

            # Get relevant financial data
            revenue_growth = info.get('revenueGrowth', 0)
            profit_margins = info.get('profitMargins', 0)
            debt_equity_ratio = info.get('totalDebt', 0) / (info.get('totalStockholdersEquity', 1) or 1)
            dividend_yield = info.get('dividendYield', 0)
            pe_ratio = info.get('trailingPE', 0)

            company_data.append({
                "Entreprise": company_name,
                "Symbole": ticker,
                "Secteur": info.get("sector", "N/A"),
                "Industrie": info.get("industry", "N/A"),
                "Capitalisation Boursière": format_currency(info.get("marketCap")),
                "ROE": info.get("returnOnEquity", "N/A"),
                "Marge Bénéficiaire": profit_margins,
                "Note (sur 10)": financial_score,
                "Potentiel d'Investissement": assess_investment_potential(info),
                "Croissance du Chiffre d'Affaires": revenue_growth,
                "Ratio Dette/Capitaux Propres": debt_equity_ratio,
                "Rendement des Dividendes": dividend_yield,
                "Ratio P/E": pe_ratio
            })
        except Exception as e:
            st.error(f"Error fetching data for {ticker} in {country}: {e}")

    df = pd.DataFrame(company_data)

    # Ensure at least 5 companies are available
    if len(df) < 5:
        st.warning(f"Insufficient data for {country} to generate all rankings.  At least 5 companies are needed.")
        return

    # Define ranking options
    ranking_options = {
        "Entreprises les plus stables": ("Ratio Dette/Capitaux Propres", "Marge Bénéficiaire"),
        "Entreprises avec le plus de potentiel": ("Potentiel d'Investissement", "Croissance du Chiffre d'Affaires"),
        "Entreprises les plus rentables pour les actionnaires": ("Rendement des Dividendes", "ROE"),
        "Entreprises les plus sous-évaluées": ("Ratio P/E",)  # Single criterion
    }

    # Add "Entreprises les plus innovantes" as a ranking option
    ranking_options["Entreprises les plus innovantes"] = None

    # Ranking selection dropdown
    selected_ranking = st.selectbox("Sélectionner un classement", list(ranking_options.keys()))

    # Perform ranking based on selection
    if selected_ranking != "Entreprises les plus innovantes":
        sort_criteria = ranking_options[selected_ranking]
        ascending = [True, False] if len(sort_criteria) == 2 and selected_ranking == "Entreprises les plus stables" else [False] * len(sort_criteria)  # Sort stable ascending, others descending
        df_ranked = df.sort_values(by=list(sort_criteria), ascending=ascending).head(5).copy()  # Make a copy to avoid SettingWithCopyWarning
        df_ranked.loc[:, "Classement"] = range(1, len(df_ranked) + 1)  # Assign ranks
        st.subheader(f"{selected_ranking} en {country}")
        st.dataframe(df_ranked[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"] + list(sort_criteria)])

        # AI Analysis for the selected ranking
        st.subheader("🤖 Analyse IA")
        for index, row in df_ranked.iterrows():
            company_name = row['Entreprise']
            ticker = row['Symbole']
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                av_info = get_alpha_vantage_overview(ticker)
                show_comparison_alerts(info, av_info, ticker)
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"#### {company_name} ({ticker}) - Classement: {row['Classement']}")
                st.write(ai_analysis)
                st.divider()
            except Exception as e:
                st.error(f"Error fetching data for {ticker} in {country}: {e}")
    else:
        # Most Innovative Company (Requires Manual Review and Adjustment)
        st.subheader(f"Entreprises les plus innovantes en {country} (Nécessite une évaluation manuelle)")
        st.write("L'innovation est difficile à quantifier automatiquement. Veuillez examiner manuellement les entreprises des secteurs et industries suivants :")
        innovative_sectors = ["Technology", "Healthcare", "Communication Services"]
        df_innovative = df[df["Secteur"].isin(innovative_sectors)].head(5).copy()  # Make a copy
        df_innovative.loc[:, "Classement"] = range(1, len(df_innovative) + 1)  # Assign ranks
        st.dataframe(df_innovative[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"]])

        # AI Analysis for Innovative Companies
        st.subheader("🤖 Analyse IA")
        for index, row in df_innovative.iterrows():
            company_name = row['Entreprise']
            ticker = row['Symbole']
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"#### {company_name} ({ticker}) - Classement: {row['Classement']}")
                st.write(ai_analysis)
                st.divider()
            except Exception as e:
                st.error(f"Error fetching data for {ticker} in {country}: {e}")
    if selected_ranking != "Entreprises les plus innovantes":
        sort_criteria = ranking_options[selected_ranking]
        ascending = [True, False] if len(sort_criteria) == 2 and selected_ranking == "Entreprises les plus stables" else [False] * len(sort_criteria)  # Sort stable ascending, others descending
        df_ranked = df.sort_values(by=list(sort_criteria), ascending=ascending).head(5).copy()  # Make a copy to avoid SettingWithCopyWarning
        df_ranked.loc[:, "Classement"] = range(1, len(df_ranked) + 1)  # Assign ranks
        st.subheader(f"{selected_ranking} en {country}")
        st.dataframe(df_ranked[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"] + list(sort_criteria)])

        # AI Analysis for the selected ranking
        st.subheader("🤖 Analyse IA")
        for index, row in df_ranked.iterrows():
            company_name = row['Entreprise']
            ticker = row['Symbole']
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                av_info = get_alpha_vantage_overview(ticker)
                show_comparison_alerts(info, av_info, ticker)
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"#### {company_name} ({ticker}) - Classement: {row['Classement']}")
                st.write(ai_analysis)
                st.divider()
            except Exception as e:
                st.error(f"Error fetching data for {ticker} in {country}: {e}")
    else:
        # Most Innovative Company (Requires Manual Review and Adjustment)
        st.subheader(f"Entreprises les plus innovantes en {country} (Nécessite une évaluation manuelle)")
        st.write("L'innovation est difficile à quantifier automatiquement. Veuillez examiner manuellement les entreprises des secteurs et industries suivants :")
        innovative_sectors = ["Technology", "Healthcare", "Communication Services"]
        df_innovative = df[df["Secteur"].isin(innovative_sectors)].head(5).copy()  # Make a copy
        df_innovative.loc[:, "Classement"] = range(1, len(df_innovative) + 1)  # Assign ranks
        st.dataframe(df_innovative[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"]])

        # AI Analysis for Innovative Companies
        st.subheader("🤖 Analyse IA")
        for index, row in df_innovative.iterrows():
            company_name = row['Entreprise']
            ticker = row['Symbole']
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"#### {company_name} ({ticker}) - Classement: {row['Classement']}")
                st.write(ai_analysis)
                st.divider()
            except Exception as e:
                st.error(f"Error fetching data for {ticker} in {country}: {e}")

def get_case_of_the_day():
    """Gets a random company for the case of the day, changing every 24 hours."""
    today = datetime.date.today()
    seed = int(today.strftime("%Y%m%d"))  # Use date as seed for daily change
    random.seed(seed)

    all_companies = []
    for companies in COUNTRY_TO_COMPANIES.values():
        all_companies.extend(companies)

    random_ticker = random.choice(all_companies)
    try:
        stock = yf.Ticker(random_ticker)
        info = stock.info
        company_name = info.get('shortName', random_ticker)
        return company_name, random_ticker, info
    except Exception as e:
        st.error(f"Error fetching data for {random_ticker}: {e}")
        return None, None, None

def analyze_case_of_the_day(company_name, ticker, info):
    """Analyzes the case of the day company in detail using AI."""
    st.header("Le Cas du Jour: Analyse Approfondie")
    if not company_name or not ticker or not info:
        st.error("Impossible de récupérer les informations de l'entreprise pour aujourd'hui.")
        return

    st.subheader(f"Entreprise: {company_name} ({ticker})")
    afficher_infos(info, company_name)

    # AI Analysis
    st.subheader("🤖 Analyse IA Détaillée")
    prompt = f"""Tu es un expert financier. Analyse en détail l'entreprise suivante pour déterminer si c'est un bon investissement aujourd'hui.
Entreprise : {company_name}
Symbole : {ticker}
Secteur : {info.get('sector', 'N/A')}
Industrie : {info.get('industry', 'N/A')}
Prix actuel : {info.get('currentPrice', 'N/A')} USD
Capitalisation boursière : {format_currency(info.get('marketCap'))} USD
Chiffre d'affaires annuel : {format_currency(info.get('totalRevenue'))} USD
Bénéfice net : {format_currency(info.get('netIncomeToCommon'))} USD
Bénéfice par action (EPS) : {info.get('trailingEps', 'N/A')}
Ratio P/E : {info.get('trailingPE', 'N/A')}
ROE : {info.get('returnOnEquity', 'N/A')}
Dette totale : {format_currency(info.get('totalDebt'))} USD
Flux de trésorerie libre : {format_currency(info.get('freeCashflow'))} USD

Analyse les points forts et les points faibles de l'entreprise, et donne une conclusion claire sur si c'est une bonne entreprise pour investir aujourd'hui, en français, de façon concise et professionnelle."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.info("Clé API Groq non trouvée. Ajoute-la dans Settings > Secrets sous le nom GROQ_API_KEY.")
        return

    headers = {
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1500  # Augmente la longueur de la réponse IA
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
            st.write(ai_response)
        else:
            st.error(f"Erreur Groq : {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"Erreur : {e}")

# Define main content based on selected tab
if selected_tab == "Comparaison d'entreprises":
    st.header("Comparaison d'entreprises")
    # Téléchargement des données financières
    if st.button("📊 Comparer les entreprises"):
        try:
            stock1 = yf.Ticker(ticker1)
            stock2 = yf.Ticker(ticker2)

            info1 = stock1.info
            info2 = stock2.info

            av_info1 = get_alpha_vantage_overview(ticker1)
            av_info2 = get_alpha_vantage_overview(ticker2)

            st.session_state.infos1 = info1
            st.session_state.infos2 = info2

            # Création des onglets pour chaque entreprise
            tab1_1, tab1_2 = st.tabs([info1.get('shortName', ticker1), info2.get('shortName', ticker2)])

            with tab1_1:
                afficher_infos(info1, info1.get('shortName', ticker1))
                score1 = score_financier(info1)
                st.markdown(f"### 🔢 Note financière globale : **{score1}/10**")

            with tab1_2:
                afficher_infos(info2, info2.get('shortName', ticker2))
                score2 = score_financier(info2)
                st.markdown(f"### 🔢 Note financière globale : **{score2}/10**")

            # Graphiques comparatifs
            st.markdown("## ⚡️ Comparaison Visuelle des Entreprises")

            colA, colB = st.columns(2)
            with colA:
                company_header(info1, av_info1, "#00b4d8")
                radar_scores(info1, av_info1, info1.get('shortName', ticker1), "#00b4d8")
            with colB:
                company_header(info2, av_info2, "#ff006e")
                radar_scores(info2, av_info2, info2.get('shortName', ticker2), "#ff006e")

            st.markdown("## 📊 Indicateurs clés")
            bar_compare(info1, info2, info1.get('shortName', ticker1), info2.get('shortName', ticker2))

            st.markdown("## 📈 Performance boursière sur 1 an")
            show_price_timeline(ticker1, ticker2, info1.get('shortName', ticker1), info2.get('shortName', ticker2))

            # AI Analysis for Company Comparison
            st.markdown("## 🤖 Analyse IA détaillée")
            prompt = f"""Tu es un expert financier. Compare ces deux entreprises afin d'aider un investisseur à choisir la plus intéressante aujourd'hui. Analyse les points suivants : secteur, industrie, prix actuel, capitalisation boursière, chiffre d'affaires annuel, bénéfice net, bénéfice par action (EPS), ratio P/E, retour sur fonds propres (ROE), dette totale, flux de trésorerie libre. Donne aussi ton avis sur leur santé financière globale en utilisant des notes sur 10 que tu imagines.
Entreprise 1 : {info1.get('shortName', ticker1)} :
- Secteur : {info1.get('sector')}
- Industrie : {info1.get('industry')}
- Prix actuel : {info1.get('currentPrice')} USD
- Capitalisation boursière : {format_currency(info1.get('marketCap'))} USD
- Chiffre d'affaires annuel : {format_currency(info1.get('totalRevenue'))} USD
- Bénéfice net : {format_currency(info1.get('netIncomeToCommon'))} USD
- EPS : {info1.get('trailingEps')}
- Ratio P/E : {info1.get('trailingPE')}
- ROE : {info1.get('returnOnEquity')}
- Dette totale : {format_currency(info1.get('totalDebt'))} USD
- Flux de trésorerie libre : {format_currency(info1.get('freeCashflow'))} USD
Entreprise 2 : {info2.get('shortName', ticker2)} :
- Secteur : {info2.get('industry')}
- Prix actuel : {info2.get('currentPrice')} USD
- Capitalisation boursière : {format_currency(info2.get('marketCap'))} USD
- Chiffre d'affaires annuel : {format_currency(info2.get('totalRevenue'))} USD
- Bénéfice net : {format_currency(info2.get('netIncomeToCommon'))} USD
- EPS : {info2.get('trailingEps')}
- Ratio P/E : {info2.get('trailingPE')}
- ROE : {info2.get('returnOnEquity')}
- Dette totale : {format_currency(info2.get('totalDebt'))} USD
- Flux de trésorerie libre : {format_currency(info2.get('freeCashflow'))} USD
En te basant sur ces données, indique laquelle des deux entreprises semble la plus prometteuse pour un investissement aujourd'hui et explique pourquoi, en français, de façon claire, concise et professionnelle."""

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                st.info("Clé API Groq non trouvée. Ajoute-la dans Settings > Secrets sous le nom GROQ_API_KEY.")
                st.stop()

            headers = {
                "Authorization": "Bearer {}".format(api_key),
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1500  # Augmente la longueur de la réponse IA
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                st.session_state.ai_answer = ai_response
                st.write(ai_response)
            else:
                st.error(f"Erreur Groq : {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"Erreur : {e}")

elif selected_tab == "Analyse IA":
    st.header("Analyse IA")
    # Section question personnalisée
    st.divider()
    st.markdown("## 💬 Pose une question à l’IA sur les entreprises comparées")
    question = st.text_input("Ta question (en français)")

    if st.button("🧠 Poser la question") and question.strip():
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                prompt_q = f"""Tu es un expert financier. Voici les données et l'analyse précédente : {st.session_state.ai_answer} Question : {question} Réponds de façon claire, concise, professionnelle en français."""
                headers = {
                    "Authorization": "Bearer {}".format(api_key),
                    "Content-Type": "application/json"
                }
                payload_q = {
                    "model": "llama3-70b-8192",
                    "messages": [{"role": "user", "content": prompt_q}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
                response_q = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload_q
                )
                if response_q.status_code == 200:
                    ai_answer_q = response_q.json()["choices"][0]["message"]["content"]
                    st.markdown("### 🤖 Réponse à ta question :")
                    st.write(ai_answer_q)
                else:
                    st.error(f"Erreur Groq : {response_q.status_code} - {response_q.text}")
            else:
                st.info("Clé API Groq non trouvée.")
        except Exception as e:
            st.error(f"Erreur : {e}")

elif selected_tab == "Comparaison Globale":
    st.header("Comparaison Globale des Entreprises")
    # Sélection du pays
    country_options = list(COMPANIES_BY_COUNTRY.keys())
    selected_country = st.selectbox("Sélectionne un pays", country_options, key="global_country_select")

    # Choix de la catégorie de classement
    ranking_options = {
        "Entreprises les plus stables": ("Ratio Dette/Capitaux Propres", "Marge Bénéficiaire"),
        "Entreprises avec le plus de potentiel": ("Potentiel d'Investissement", "Croissance du Chiffre d'Affaires"),
        "Entreprises les plus rentables pour les actionnaires": ("Rendement des Dividendes", "ROE"),
        "Entreprises les plus sous-évaluées": ("Ratio P/E",),
        "Entreprises les plus innovantes": None
    }
    selected_ranking = st.selectbox("Sélectionner un classement", list(ranking_options.keys()), key="global_ranking_select")

    # Récupération des tickers du pays sélectionné
    tickers = [c['ticker'] for c in COMPANIES_BY_COUNTRY[selected_country]]

    # Construction du tableau des entreprises
    company_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('shortName', ticker)
            financial_score = score_financier(info)
            revenue_growth = info.get('revenueGrowth', 0)
            profit_margins = info.get('profitMargins', 0)
            debt_equity_ratio = info.get('totalDebt', 0) / (info.get('totalStockholdersEquity', 1) or 1)
            dividend_yield = info.get('dividendYield', 0)
            pe_ratio = info.get('trailingPE', 0)
            company_data.append({
                "Entreprise": company_name,
                "Symbole": ticker,
                "Secteur": info.get("sector", "N/A"),
                "Industrie": info.get("industry", "N/A"),
                "Capitalisation Boursière": format_currency(info.get("marketCap")),
                "ROE": info.get("returnOnEquity", "N/A"),
                "Marge Bénéficiaire": profit_margins,
                "Note (sur 10)": financial_score,
                "Potentiel d'Investissement": assess_investment_potential(info),
                "Croissance du Chiffre d'Affaires": revenue_growth,
                "Ratio Dette/Capitaux Propres": debt_equity_ratio,
                "Rendement des Dividendes": dividend_yield,
                "Ratio P/E": pe_ratio,
                "info_obj": info  # Pour l'analyse IA et radar
            })
        except Exception as e:
            st.error(f"Erreur sur {ticker}: {e}")

    df = pd.DataFrame(company_data)
    if len(df) >= 2:
        if selected_ranking != "Entreprises les plus innovantes":
            sort_criteria = ranking_options[selected_ranking]
            ascending = [True, False] if len(sort_criteria) == 2 and selected_ranking == "Entreprises les plus stables" else [False] * len(sort_criteria)
            df_ranked = df.sort_values(by=list(sort_criteria), ascending=ascending).head(5).copy()
            df_ranked.loc[:, "Classement"] = range(1, len(df_ranked) + 1)
            st.subheader(f"{selected_ranking} ({selected_country})")
            st.dataframe(df_ranked[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"] + list(sort_criteria)])
             # AJOUTE ICI LE CODE SUIVANT :
            st.subheader("Diagramme comparatif (barres)")
            import plotly.express as px
            main_metric = list(sort_criteria)[0]
            df_ranked[main_metric] = pd.to_numeric(df_ranked[main_metric], errors="coerce")
            fig = px.bar(
            df_ranked,
            x="Entreprise",
            y=main_metric,
            color="Entreprise",
            text=main_metric,
            title=f"Comparaison sur {main_metric}",
            color_discrete_sequence=px.colors.qualitative.Plotly
    )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(yaxis_title=main_metric, xaxis_title="Entreprise", showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Diagramme radar comparatif
            st.subheader("Diagramme comparatif (radar)")
            import plotly.graph_objects as go
            radar_axes = ["ROE", "Marge Bénéficiaire", "Potentiel d'Investissement", "Croissance du Chiffre d'Affaires", "Ratio Dette/Capitaux Propres", "Rendement des Dividendes", "Ratio P/E"]
            fig = go.Figure()
            colors = ["#00b4d8", "#ff006e", "#8338ec", "#fb5607", "#43aa8b", "#f9c74f", "#3a86ff", "#ffbe0b", "#b5179e", "#6a4c93"]
            for i, (_, row) in enumerate(df_ranked.iterrows()):
                values = [
                    float(row["ROE"] or 0) * 10,
                    float(row["Marge Bénéficiaire"] or 0) * 100,
                    float(row["Potentiel d'Investissement"] or 0) * 10,
                    float(row["Croissance du Chiffre d'Affaires"] or 0) * 100,
                    100 - float(row["Ratio Dette/Capitaux Propres"] or 0) * 100,
                    float(row["Rendement des Dividendes"] or 0) * 100,
                    100 / float(row["Ratio P/E"] or 1)
                ]
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_axes,
                    fill='toself',
                    name=row["Entreprise"],
                    line_color=colors[i % len(colors)]
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            # Analyse IA pour chaque entreprise du classement
            st.subheader("🤖 Analyse IA pour chaque entreprise du classement")
            for idx, row in df_ranked.iterrows():
                company_name = row["Entreprise"]
                ticker = row["Symbole"]
                info = row["info_obj"]
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"**{company_name} ({ticker})**")
                st.write(ai_analysis)
                st.divider()
        else:
            # Classement "innovantes" = filtrage manuel sur secteurs typiques
            innovative_sectors = ["Technology", "Healthcare", "Communication Services"]
            df_innovative = df[df["Secteur"].isin(innovative_sectors)].head(5).copy()
            df_innovative.loc[:, "Classement"] = range(1, len(df_innovative) + 1)
            st.subheader(f"Entreprises les plus innovantes ({selected_country})")
            st.dataframe(df_innovative[["Classement", "Entreprise", "Symbole", "Secteur", "Industrie"]])
            
            # Diagramme comparatif en barres
            st.subheader("Diagramme comparatif (barres)")
            import plotly.express as px
            main_metric = list(sort_criteria)[0]  # Prend le premier critère de tri
            df_ranked[main_metric] = pd.to_numeric(df_ranked[main_metric], errors="coerce")
            fig = px.bar(
                df_ranked,
                x="Entreprise",
                y=main_metric,
                color="Entreprise",
                text=main_metric,
                title=f"Comparaison sur {main_metric}",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(yaxis_title=main_metric, xaxis_title="Entreprise", showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
            # Diagramme radar comparatif
            st.subheader("Diagramme comparatif (radar)")
            import plotly.graph_objects as go
            radar_axes = ["ROE", "Marge Bénéficiaire", "Potentiel d'Investissement", "Croissance du Chiffre d'Affaires", "Ratio Dette/Capitaux Propres", "Rendement des Dividendes", "Ratio P/E"]
            fig = go.Figure()
            colors = ["#00b4d8", "#ff006e", "#8338ec", "#fb5607", "#43aa8b"]
            for i, (_, row) in enumerate(df_innovative.iterrows()):
                values = [
                    float(row["ROE"] or 0) * 10,
                    float(row["Marge Bénéficiaire"] or 0) * 100,
                    float(row["Potentiel d'Investissement"] or 0) * 10,
                    float(row["Croissance du Chiffre d'Affaires"] or 0) * 100,
                    100 - float(row["Ratio Dette/Capitaux Propres"] or 0) * 100,
                    float(row["Rendement des Dividendes"] or 0) * 100,
                    100 / float(row["Ratio P/E"] or 1)
                ]
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_axes,
                    fill='toself',
                    name=row["Entreprise"],
                    line_color=colors[i % len(colors)]
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Analyse IA pour chaque entreprise du classement
            st.subheader("🤖 Analyse IA pour chaque entreprise du classement")
            for idx, row in df_innovative.iterrows():
                company_name = row["Entreprise"]
                ticker = row["Symbole"]
                info = row["info_obj"]
                ai_analysis = get_ai_analysis(company_name, info, selected_ranking)
                st.markdown(f"**{company_name} ({ticker})**")
                st.write(ai_analysis)
                st.divider()
    else:
        st.warning("Pas assez d'entreprises pour établir un classement.")
elif selected_tab == "Le Cas du Jour":
    company_name, ticker, info = get_case_of_the_day()
    analyze_case_of_the_day(company_name, ticker, info)
elif selected_tab == "Comparaison Globale":
    st.header("Comparaison Globale des Entreprises")

    # Create a list of country options with flags
    country_options = [f"{COUNTRY_FLAGS.get(country, '')} {country}" for country in TOP_10_COUNTRIES]
    country_options = ["Monde"] + country_options  # Add "Monde" to the list

    # Country selection dropdown
    selected_country_with_flag = st.selectbox("Sélectionne un pays", country_options)

    # Extract the country name from the selected option
    selected_country = selected_country_with_flag.split(" ", 1)[1] if " " in selected_country_with_flag else selected_country_with_flag

    # Perform analysis for the selected country
    if selected_country:
        perform_country_analysis(selected_country)
elif selected_tab == "Comparateur de marchés":
    st.header("Comparateur de marchés financiers")
    st.markdown("Compare les principaux indices boursiers mondiaux et obtiens un conseil IA sur le marché le plus attractif.")
    df_markets = get_market_data(MARKET_INDEXES)
    st.dataframe(df_markets)
    st.markdown("### 🤖 Conseil IA sur le marché à privilégier")
    with st.spinner("Analyse de l'IA en cours..."):
        ai_market_advice = get_ai_market_advice(df_markets)
        st.write(ai_market_advice)

elif selected_tab == "Comparateur de marchés (2 marchés)":
    st.header("Comparateur de 2 marchés financiers")
    st.markdown("Compare deux indices boursiers mondiaux, visualise leurs courbes et obtiens une analyse IA détaillée.")

    # Sélection des deux marchés
    market_names = list(MARKET_INDEXES.keys())
    col1, col2 = st.columns(2)
    with col1:
        market1 = st.selectbox("Marché 1", market_names, key="market1")
    with col2:
        market2 = st.selectbox("Marché 2", market_names, key="market2", index=1)

    if market1 and market2 and market1 != market2:
        ticker1 = MARKET_INDEXES[market1]
        ticker2 = MARKET_INDEXES[market2]

        # Récupération des historiques
        hist1 = yf.Ticker(ticker1).history(period="6mo")["Close"]
        hist2 = yf.Ticker(ticker2).history(period="6mo")["Close"]

        # Trouver les dates communes
        common_dates = hist1.index.intersection(hist2.index)

        # Réindexer sur les dates communes
        hist1_common = hist1.loc[common_dates]
        hist2_common = hist2.loc[common_dates]

        # Créer le DataFrame de comparaison
        df_compare = pd.DataFrame({
            market1: hist1_common,
            market2: hist2_common
        })

        if df_compare.empty:
            st.warning("Pas de dates communes entre les deux marchés sélectionnés.")
        else:
            df_compare = df_compare / df_compare.iloc[0] * 100  # Normalisation

            df_compare = df_compare.reset_index()  # Pour avoir la colonne 'Date'
            df_melt = df_compare.melt('Date', var_name='Marché', value_name='Performance')

            chart = alt.Chart(df_melt).mark_line().encode(
                x='Date:T',
                y='Performance:Q',
                color=alt.Color('Marché:N', scale=alt.Scale(scheme='category10')),
                tooltip=['Date:T', 'Marché:N', 'Performance:Q']
            ).properties(height=400, width=700)

            st.altair_chart(chart, use_container_width=True)
        # Analyse IA détaillée
        st.markdown("### 🤖 Analyse IA détaillée")
        # Préparation du prompt
        perf1m_1 = ((hist1.iloc[-1] / hist1.iloc[-22]) - 1) * 100 if len(hist1) > 22 else None
        perf6m_1 = ((hist1.iloc[-1] / hist1.iloc[0]) - 1) * 100 if len(hist1) > 1 else None
        perf1m_2 = ((hist2.iloc[-1] / hist2.iloc[-22]) - 1) * 100 if len(hist2) > 22 else None
        perf6m_2 = ((hist2.iloc[-1] / hist2.iloc[0]) - 1) * 100 if len(hist2) > 1 else None

        # Récupération d'indicateurs avancés pour chaque marché
        def market_stats(hist):
            if hist.empty:
                return {}
            return {
                "Dernière clôture": f"{hist.iloc[-1]:.2f}",
                "Perf. 1 mois (%)": f"{((hist.iloc[-1] / hist.iloc[-22] - 1) * 100):.2f}" if len(hist) > 22 else "N/A",
                "Perf. 6 mois (%)": f"{((hist.iloc[-1] / hist.iloc[0] - 1) * 100):.2f}" if len(hist) > 1 else "N/A",
                "Volatilité (écart-type)": f"{hist.pct_change().std() * 100:.2f}%",
                "Plus haut 6 mois": f"{hist.max():.2f}",
                "Plus bas 6 mois": f"{hist.min():.2f}",
                "Volume moyen": "N/A"
            }

        stats1 = market_stats(hist1)
        stats2 = market_stats(hist2)

        # Construction du prompt détaillé
        prompt = (
            f"Tu es un expert en marchés financiers. Voici les données de deux indices boursiers sur 6 mois :\n"
            f"{market1} ({ticker1}) :\n"
            + "\n".join([f"- {k} : {v}" for k, v in stats1.items()]) + "\n"
            f"{market2} ({ticker2}) :\n"
            + "\n".join([f"- {k} : {v}" for k, v in stats2.items()]) + "\n"
            "Analyse en détail les deux marchés en t'appuyant sur ces chiffres (performance, volatilité, plus haut/bas, etc.), compare leurs dynamiques, contexte économique, et donne un avis argumenté et professionnel sur lequel investir aujourd'hui, en français, de façon claire et détaillée."
        )

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.info("Clé API Groq non trouvée. Ajoute-la dans Settings > Secrets sous le nom GROQ_API_KEY.")
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            with st.spinner("Analyse IA en cours..."):
                try:
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if response.status_code == 200:
                        ai_response = response.json()["choices"][0]["message"]["content"]
                        st.write(ai_response)
                    else:
                        st.error(f"Erreur Groq : {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Erreur : {e}")
    else:
        st.info("Sélectionne deux marchés différents pour comparer.")
