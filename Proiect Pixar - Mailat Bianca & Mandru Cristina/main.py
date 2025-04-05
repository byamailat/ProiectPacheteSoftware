import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import LabelEncoder, StandardScaler

# === Încărcare date ===
file_path = "Netflix.csv"
df = pd.read_csv(file_path)

# === Tratare valori lipsă ===
df['tara'].fillna("Necunoscuta", inplace=True)
df['rating'].fillna("Necunoscut", inplace=True)
df['tip'].fillna("Necunoscut", inplace=True)
df['director'].fillna("Necunoscut", inplace=True)
df['actori'].fillna("Necunoscut", inplace=True)
df['categorie'].fillna("Fara categorie", inplace=True)



df_filme = df[df['tip'] == 'Movie'].copy()
df_seriale = df[df['tip'] == 'TV Show'].copy()

# === Convertire durată în minute ===
df['durata_min'] = df['durata'].str.extract(r'(\d+)').astype(float)

# === Convertire dată ===
df['date_adaugarii'] = pd.to_datetime(df['date_adaugarii'], errors='coerce')

# === Metoda de scalare ===
coloane_scalabile = ['durata_min', 'anul_lansarii']
df = df.dropna(subset=['durata_min', 'anul_lansarii'])
scaler = StandardScaler()
valori_scalate = scaler.fit_transform(df[coloane_scalabile])
df_scalat = pd.DataFrame(valori_scalate, columns=[f"{col}_scalat" for col in coloane_scalabile])
df = pd.concat([df, df_scalat], axis=1)


# === Codificare categorii ===
le_tip = LabelEncoder()
le_rating = LabelEncoder()
le_tara = LabelEncoder()

df['tip_cod'] = le_tip.fit_transform(df['tip'])
df['rating_cod'] = le_rating.fit_transform(df['rating'])
df['tara_cod'] = le_tara.fit_transform(df['tara'])

# === Eliminare outlieri pentru 'durata_min' ===
def elimina_outlieri_iqr(df, coloana):
    Q1 = df[coloana].quantile(0.25)
    Q3 = df[coloana].quantile(0.75)
    IQR = Q3 - Q1
    limita_jos = Q1 - 1.5 * IQR
    limita_sus = Q3 + 1.5 * IQR
    return df[(df[coloana] >= limita_jos) & (df[coloana] <= limita_sus)]

df = elimina_outlieri_iqr(df, 'durata_min')

# === Configurare aplicație Streamlit ===
st.set_page_config(page_title="Filme Netflix", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #FFFFFF;'>FILME NETFLIX</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #831010;
    }
    .sidebar .sidebar-content {
        background-color: #004B87;
    }
    .sidebar .sidebar-content .element-container {
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === Navigare în aplicație ===
st.sidebar.title("Navigați la:")
option = st.sidebar.radio("Selectați o opțiune", [
    "Set de date",
    "Statistici descriptive",
    "Durata filmelor în 2017",
    "Codificare categorii",
    "Prelucrări statistice"
])

# === Pagina: Set de date ===
if option == "Set de date":
    st.markdown("<h2 style='color: white;'>Set de date</h2>", unsafe_allow_html=True)
    coloane_de_exclus = [col for col in df.columns if '_scalat' in col]
    df_fara_scalate = df.drop(columns=coloane_de_exclus)
    st.dataframe(df_fara_scalate)

# === Pagina: Statistici descriptive ===
elif option == "Statistici descriptive":
    st.markdown("<h2 style='color: white;'>Statistici descriptive</h2>", unsafe_allow_html=True)
    st.dataframe(df.describe())

    st.markdown("---")
    st.markdown("<h2 style='color: white;'>Tabel cu valori scalate </h2>", unsafe_allow_html=True)
    coloane_scalate = [col for col in df.columns if '_scalat' in col]
    df_scalare = df[coloane_scalate]
    st.dataframe(df_scalare)

# === Pagina: Durata filmelor în 2017 ===
elif option == "Durata filmelor în 2017":
    st.markdown("<h2 style='color: white;'>Durata filmelor în 2017</h2>", unsafe_allow_html=True)
    df_2017 = df.dropna(subset=['date_adaugarii', 'durata_min'])
    df_2017 = df_2017[df_2017['date_adaugarii'].dt.year == 2017]
    if df_2017.empty:
        st.warning("Nu există filme adăugate în 2017.")
    else:
        fig = px.scatter(df_2017, x='date_adaugarii', y='durata_min',
                         labels={'durata_min': 'Durata (minute)', 'date_adaugarii': 'Data adăugării'},
                         title='Durata filmelor adăugate în 2017',
                         hover_data=['titlu'])
        fig.update_layout(template='plotly', plot_bgcolor='rgba(0, 0, 0, 0)')
        st.plotly_chart(fig)

# === Pagina: Codificare categorii ===
elif option == "Codificare categorii":
    st.markdown("<h2 style='color: white;'>Codificare categorii</h2>", unsafe_allow_html=True)

    st.markdown("#### Tip")
    tip_df = pd.DataFrame({
        "Valoare originală": le_tip.classes_,
        "Cod": le_tip.transform(le_tip.classes_)
    })
    st.dataframe(tip_df)

    st.markdown("#### Rating")
    rating_df = pd.DataFrame({
        "Valoare originală": le_rating.classes_,
        "Cod": le_rating.transform(le_rating.classes_)
    })
    st.dataframe(rating_df)

    st.markdown("#### Țară")
    tara_df = pd.DataFrame({
        "Valoare originală": le_tara.classes_,
        "Cod": le_tara.transform(le_tara.classes_)
    })
    st.dataframe(tara_df)

# === Pagina: Prelucrări statistice ===
elif option == "Prelucrări statistice":
    st.markdown("<h2 style='color: white;'>Prelucrări statistice</h2>", unsafe_allow_html=True)

    st.markdown("<h2 style='color: white;'>Număr de filme/seriale pe an</h2>", unsafe_allow_html=True)
    productie_an = df.groupby(['anul_lansarii', 'tip']).size().reset_index(name='numar_productii')
    st.dataframe(productie_an)

    fig = px.bar(
        productie_an,
        x='anul_lansarii',
        y='numar_productii',
        color='tip',
        barmode='group',
        labels={'anul_lansarii': 'Anul Lansării', 'numar_productii': 'Număr Producții'},
        title='Număr de filme și seriale pe ani'
    )
    fig.update_layout(template='plotly', xaxis_tickangle=-45, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig)

    st.markdown("<h2 style='color: white;'>Durata medie per rating</h2>", unsafe_allow_html=True)
    grup_rating = df.groupby("rating")["durata_min"].mean().reset_index()
    st.dataframe(grup_rating)

    st.markdown("<h2 style='color: white;'>Număr de producții per țară (Top 10)</h2>", unsafe_allow_html=True)
    grup_tara = df.groupby("tara").size().reset_index(name="numar_productii").sort_values(
        by="numar_productii", ascending=False).head(10)
    st.dataframe(grup_tara)

    st.markdown("<h2 style='color: white;'>Durata medie pe an și tip</h2>", unsafe_allow_html=True)
    grup_an_tip = df.groupby(["anul_lansarii", "tip"])["durata_min"].mean().reset_index()
    st.dataframe(grup_an_tip)

    st.markdown("<h2 style='color: white;'>Agregare multiplă: durată medie și maximă per rating</h2>", unsafe_allow_html=True)
    grup_multi = df.groupby("rating")["durata_min"].agg(['mean', 'max']).reset_index()
    st.dataframe(grup_multi)

    st.markdown("<h2 style='color: white;'>Funcții de grup aplicate pe durata_min per tip</h2>", unsafe_allow_html=True)
    grup_functii = df.groupby("tip")["durata_min"].agg(['count', 'mean', 'min', 'max']).reset_index()
    grup_functii.columns = ['Tip', 'Nr. titluri', 'Durată medie', 'Durată minimă', 'Durată maximă']
    st.dataframe(grup_functii)
