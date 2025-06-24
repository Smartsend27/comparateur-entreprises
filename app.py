import streamlit as st
import yfinance as yf
import os
import requests
import pandas as pd

st.set_page_config(page_title="Comparateur d'entreprises avancé", page_icon="📊", layout="wide")

st.title("📊 Comparateur avancé d'entreprises pour investissement")
st.markdown("""
Compare deux entreprises en détail avec notes, graphiques et analyse IA en français pour t'aider à investir intelligemment.
""")

st.divider()

# Entrée utilisateur
ticker1 = st.text_input("🔎 Symbole boursier de l'entreprise 1", value="AAPL")
ticker2 = st.text_input("🔍 Symbole boursier de l'entreprise 2", value="TSLA")

# Fonctions utilitaires
def format_currency(value):
    if value is None:
        return "N/A"
    try:
        v = float(value)
        if abs(v) > 1e9:
            return f"{v/1e9:.2f} Md"
        elif abs(v) > 1e6:
            return f"{v/1e6:.2f} M"
        elif abs(v) > 1e3:
            return f"{v/1e3:.2f} K"
        else:
            return f"{v:.2f}"
    except:
        return str(value)

def score_financier(info):
    score = 0
    try:
        revenue = float(info.get("totalRevenue") or 0)
        net_income = float(info.get("netIncomeToCommon") or 0)
        marge_nette = net_income / revenue if revenue > 0 else 0
        if marge_nette > 0.1:
            score += 3
        elif marge_nette > 0.05:
            score += 2
        else:
            score += 1
    except:
        score += 1
    try:
        roe = float(info.get("returnOnEquity") or 0)
        if roe > 0.15:
            score += 3
        elif roe > 0.07:
            score += 2
        else:
            score += 1
    except:
        score += 1
    try:
        total_debt = float(info.get("totalDebt") or 0)
        equity = float(info.get("totalStockholdersEquity") or 1)
        leverage = total_debt / equity if equity != 0 else 10
        if leverage < 0.5:
            score += 2
        elif leverage < 1.0:
            score += 1
    except:
        score += 1
    try:
        fcf = float(info.get("freeCashflow") or 0)
        if fcf > 0:
            score += 2
    except:
        score += 1
    return min(score, 10)

def afficher_infos(info, titre):
    st.subheader(f"📈 {titre}")
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
        marge = ((info.get('netIncomeToCommon') or 0) / (info.get('totalRevenue') or 1))
        leverage = ((info.get('totalDebt') or 0) / max(info.get('totalStockholdersEquity') or 1,1))
        st.write(f"- **Marge nette estimée** : {marge:.2%}")
        st.write(f"- **Dette / Capitaux propres estimé** : {leverage:.2f}")
    except:
        st.write("- Ratios estimés indisponibles")

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = ""
if "infos1" not in st.session_state:
    st.session_state.infos1 = {}
if "infos2" not in st.session_state:
    st.session_state.infos2 = {}

# Comparaison
if st.button("📊 Comparer les entreprises"):

    try:
        stock1 = yf.Ticker(ticker1)
        stock2 = yf.Ticker(ticker2)

        info1 = stock1.info
        info2 = stock2.info

        st.session_state.infos1 = info1
        st.session_state.infos2 = info2

        col1, col2 = st.columns(2)
        with col1:
            afficher_infos(info1, info1.get('shortName', ticker1))
            score1 = score_financier(info1)
            st.markdown(f"### 🔢 Note financière globale : **{score1}/10**")
        with col2:
            afficher_infos(info2, info2.get('shortName', ticker2))
            score2 = score_financier(info2)
            st.markdown(f"### 🔢 Note financière globale : **{score2}/10**")

        # Graphiques
        st.markdown("## 📊 Visualisation des indicateurs clés")

        indicateurs = ["currentPrice", "marketCap", "totalRevenue", "netIncomeToCommon", "returnOnEquity"]
        noms = ["Prix actuel", "Capitalisation", "Chiffre d'affaires", "Bénéfice net", "ROE"]

        valeurs1 = [info1.get(x) or 0 for x in indicateurs]
        valeurs2 = [info2.get(x) or 0 for x in indicateurs]

        df = pd.DataFrame({
            info1.get('shortName', ticker1): valeurs1,
            info2.get('shortName', ticker2): valeurs2
        }, index=noms)

        st.bar_chart(df)

        # Analyse IA complète
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            prompt = f"""Tu es un expert financier. Compare ces deux entreprises afin d'aider un investisseur à choisir la plus intéressante aujourd'hui. Analyse les points suivants : secteur, industrie, prix actuel, capitalisation boursière, chiffre d'affaires annuel, bénéfice net, bénéfice par action (EPS), ratio P/E, retour sur fonds propres (ROE), dette totale, flux de trésorerie libre. Donne aussi ton avis sur leur santé financière globale en utilisant des notes sur 10 que tu imagines.
Entreprise 1 : {info1.get('shortName')} :
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

Entreprise 2 : {info2.get('shortName')} :
- Secteur : {info2.get('sector')}
- Industrie : {info2.get('industry')}
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

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 800
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                st.session_state.ai_answer = ai_response
                st.markdown("## 🤖 Analyse IA détaillée")
                st.write(ai_response)
            else:
                st.error(f"Erreur Groq : {response.status_code} - {response.text}")
        else:
            st.info("Clé API Groq non trouvée. Ajoute-la dans Settings > Secrets sous le nom GROQ_API_KEY.")

    except Exception as e:
        st.error(f"Erreur : {e}")

# Section question personnalisée
st.divider()
st.markdown("## 💬 Pose une question à l’IA sur les entreprises comparées")
question = st.text_input("Ta question (en français)")

if st.button("🧠 Poser la question") and question.strip():
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            prompt_q = f"""Tu es un expert financier. Voici les données et l'analyse précédente :

{st.session_state.ai_answer}

Question : {question}

Réponds de façon claire, concise, professionnelle en français."""
            headers = {
                "Authorization": f"Bearer {api_key}",
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
