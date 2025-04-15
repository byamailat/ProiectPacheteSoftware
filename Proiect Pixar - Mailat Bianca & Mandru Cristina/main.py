import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt



# === Încărcare date ===
file_path = "Netflix.csv"
df = pd.read_csv(file_path)

def extrage_minute(durata):
    if pd.isnull(durata):
        return np.nan
    if 'min' in durata:
        try:
            return int(durata.split()[0])
        except:
            return np.nan
    return np.nan  # dacă nu e în minute, ignorăm

df['durata_min'] = df['durata'].apply(extrage_minute)


# === Tratare valori lipsă ===
df.replace("None", np.nan, inplace=True)
df['tara'].fillna("Necunoscuta", inplace=True)
df['rating'].fillna("Necunoscut", inplace=True)
df['tip'].fillna("Necunoscut", inplace=True)
df['director'].fillna("Necunoscut", inplace=True)
df['actori'].fillna("Necunoscut", inplace=True)
media_durata = df['durata_min'].mean()
df['durata_min'].fillna(media_durata, inplace=True)
df['categorie'].fillna("Fara categorie", inplace=True)


df_filme = df[df['tip'] == 'Movie'].copy()
df_seriale = df[df['tip'] == 'TV Show'].copy()


# === Convertire dată ===
df['date_adaugarii'] = pd.to_datetime(df['date_adaugarii'], errors='coerce')

# === Codificare categorii ===
le_tip = LabelEncoder()
le_rating = LabelEncoder()
le_tara = LabelEncoder()

df['tip_cod'] = le_tip.fit_transform(df['tip'])
df['rating_cod'] = le_rating.fit_transform(df['rating'])
df['tara_cod'] = le_tara.fit_transform(df['tara'])

# ===========Scalare======
scaler = StandardScaler()

coloane_scalabile = ['anul_lansarii', 'rating_cod', 'tara_cod', 'tip_cod']
scalate = scaler.fit_transform(df[coloane_scalabile])

df_scalate = pd.DataFrame(scalate, columns=[col + '_scalat' for col in coloane_scalabile])
df = pd.concat([df, df_scalate], axis=1)

# MINMAX
scaler_mm = MinMaxScaler()
scalate_mm = scaler_mm.fit_transform(df[coloane_scalabile])
df_scalate_mm = pd.DataFrame(scalate_mm, columns=[col + '_minmax' for col in coloane_scalabile])
df = pd.concat([df, df_scalate_mm], axis=1)

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
    "Metode de scalare",
    "Funcții de grupare si prelucrari statistice"
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
    st.markdown("<h2 style='color: white;'>Durata filmelor în 2017 (doar cele în minute)</h2>", unsafe_allow_html=True)

    df_2017 = df.dropna(subset=['date_adaugarii', 'durata_min'])
    df_2017 = df_2017[df_2017['date_adaugarii'].dt.year == 2017]

    if df_2017.empty:
        st.warning("Nu există filme adăugate în 2017 cu durată în minute.")
    else:
        fig = px.scatter(
            df_2017,
            x='date_adaugarii',
            y='durata_min',
            labels={'durata_min': 'Durata (minute)', 'date_adaugarii': 'Data adăugării'},
            title='Durata filmelor adăugate în 2017 (numai cele cu minute)',
            hover_data=['titlu']
        )
        fig.update_layout(template='plotly', plot_bgcolor='rgba(0, 0, 0, 0)')
        st.plotly_chart(fig)

    df_2017 = df[(df["date_adaugarii"].dt.year == 2017) & (df["durata"].str.contains("min", na=False))]

    # Extrage numărul de minute din textul gen "95 min"
    df_2017["durata_min"] = df_2017["durata"].str.extract(r'(\d+)').astype(float)

    # Desenăm histograma
    plt.figure(figsize=(10, 6))
    plt.hist(df_2017["durata_min"], bins=20, color="skyblue", edgecolor="black")
    plt.title("Distribuția duratei filmelor adăugate în 2017")
    plt.xlabel("Durata (minute)")
    plt.ylabel("Număr de filme")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_2017["durata_min"], bins=20, color="skyblue", edgecolor="black")
    ax.set_title("Distribuția duratei filmelor adăugate în 2017")
    ax.set_xlabel("Durata (minute)")
    ax.set_ylabel("Număr de filme")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)


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


# === Pagina: Funcții de grupare ===
elif option == "Funcții de grupare si prelucrari statistice":
    st.markdown("<h2 style='color: white;'>Funcții de grupare</h2>", unsafe_allow_html=True)

    # === Număr de filme și seriale pe ani ===
    st.markdown("### Număr de filme și seriale pe ani")
    productie_an = df.groupby(['anul_lansarii', 'tip']).size().reset_index(name='numar_productii')
    st.dataframe(productie_an)

    fig1 = px.bar(productie_an, x="anul_lansarii", y="numar_productii", color="tip",
                  barmode="group", title="Număr de producții pe an (film vs serial)",
                  labels={"anul_lansarii": "An lansare", "numar_productii": "Număr producții"})
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1)

    # === Top 10 țări după număr de producții ===
    st.markdown("### Număr de producții per țară (Top 10)")
    grup_tara = df.groupby("tara").size().reset_index(name="numar_productii").sort_values(
        by="numar_productii", ascending=False).head(10)
    st.dataframe(grup_tara)

    fig2 = px.bar(grup_tara, x="tara", y="numar_productii", color="tara",
                  title="Top 10 țări după număr de producții",
                  labels={"tara": "Țară", "numar_productii": "Număr producții"})
    fig2.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2)

    # === Durată medie per an și tip ===
    st.markdown("###  Durată medie per an și tip")
    grup_an_tip = df.groupby(["anul_lansarii", "tip"])["durata_min"].mean().reset_index()
    st.dataframe(grup_an_tip)

    fig3 = px.line(grup_an_tip, x="anul_lansarii", y="durata_min", color="tip",
                   markers=True,
                   title="Evoluția duratei medii în timp (film vs serial)",
                   labels={"anul_lansarii": "An lansare", "durata_min": "Durată medie (min)"})
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3)

    # === Agregare multiplă: medie și maximă pe rating ===
    st.markdown("### Durată medie și maximă per rating")
    grup_multi = df.groupby("rating")["durata_min"].agg(['mean', 'max']).reset_index()
    st.dataframe(grup_multi)

    fig4 = px.bar(grup_multi, x="rating", y=["mean", "max"],
                  barmode="group",
                  title="Durată medie și maximă în funcție de rating",
                  labels={"value": "Durată (min)", "rating": "Rating"})
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4)

    # === Funcții de grup pe tip ===
    st.markdown("### Statistici generale pe tip (film vs serial)")
    grup_functii = df.groupby("tip")["durata_min"].agg(['count', 'mean', 'min', 'max']).reset_index()
    grup_functii.columns = ['Tip', 'Nr. titluri', 'Durată medie', 'Durată minimă', 'Durată maximă']
    st.dataframe(grup_functii)

    fig5 = px.bar(grup_functii, x="Tip", y=["Durată medie", "Durată maximă", "Durată minimă"],
                  barmode="group", title="Durate per tip de conținut",
                  labels={"value": "Durată (minute)", "Tip": "Tip"})
    fig5.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig5)
# === Pagina: Scalare variabile ===
elif option == "Metode de scalare":
    st.markdown("<h2 style='color: white;'>Scalare variabile</h2>", unsafe_allow_html=True)

    st.markdown("### Variabile selectate pentru scalare:")
    st.write("- anul_lansarii")
    st.write("- rating_cod")
    st.write("- tara_cod")
    st.write("- tip_cod")

    coloane_orig = ['anul_lansarii', 'rating_cod', 'tara_cod', 'tip_cod']
    coloane_std = [col + '_scalat' for col in coloane_orig]
    coloane_mm = [col + '_minmax' for col in coloane_orig]

    st.markdown("### Tabel cu StandardScaler (medie 0, dev. standard 1)")
    df_std = df[coloane_orig + coloane_std]
    st.dataframe(df_std.head(20))

    st.markdown("### Tabel cu MinMaxScaler (valori între 0 și 1)")
    df_mm = df[coloane_orig + coloane_mm]
    st.dataframe(df_mm.head(20))

    with st.expander(" Statistici după scalare (StandardScaler)"):
        for col in coloane_std:
            media = df[col].mean()
            std = df[col].std()
            st.write(f"{col}: medie = {media:.4f}, std = {std:.4f}")



