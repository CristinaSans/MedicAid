import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Seguiment Glucosa", page_icon="📈")
st.sidebar.header("Seguiment glucosa")

st.title("Anàlisi de glucosa per pacient")

# Carregar el CSV
uploaded_file = st.file_uploader("Carrega el fitxer CSV", type=["csv"])

if uploaded_file is not None:
    # Llegir CSV amb separador ;
    df = pd.read_csv(uploaded_file, sep=";")

    st.write("Dades carregades:")
    st.dataframe(df, hide_index= True)

    # Crear columna display
    df["display"] = df["id_pacient"] + " - " + df["nom"]

    # Llista de pacients (id_pacient únics)
    pacients = df["id_pacient"].unique()

    # Selector de pacient amb id + nom
    pacient_seleccionat = st.selectbox(
        "Selecciona un pacient",
        options=pacients,
        format_func=lambda x: df.loc[df["id_pacient"] == x, "display"].iloc[0]
    )

    # Filtrar dades del pacient
    df_pacient = df[df["id_pacient"] == pacient_seleccionat].copy()

    # Crear columna datetime per ordenar correctament
    df_pacient["datetime"] = pd.to_datetime(df_pacient["data"] + " " + df_pacient["hora"])
    df_pacient = df_pacient.sort_values("datetime")

    # ------------------------------
    # ESTADÍSTIQUES GLOBALS (TOTES LES DATES)
    # ------------------------------
    st.subheader(f"Resultats globals per al pacient {pacient_seleccionat}")

    max_glucosa = df_pacient["valor_glucosa"].max()
    min_glucosa = df_pacient["valor_glucosa"].min()
    mitjana_glucosa = df_pacient["valor_glucosa"].mean()

    st.metric("Glucosa màxima", f"{max_glucosa}")
    st.metric("Glucosa mínima", f"{min_glucosa}")
    st.metric("Glucosa mitjana", f"{mitjana_glucosa:.2f}")

    # ------------------------------
    # RESUM PER DIES
    # ------------------------------
    st.subheader("Resum per dies")

    resum_dies = df_pacient.groupby("data")["valor_glucosa"].agg(
        ["min", "max", "mean"]
    ).reset_index()

    resum_dies.rename(columns={
        "min": "Glucosa mínima",
        "max": "Glucosa màxima",
        "mean": "Glucosa mitjana"
    }, inplace=True)

    # Arrodonir la mitjana a 2 decimals
    resum_dies["Glucosa mitjana"] = resum_dies["Glucosa mitjana"].round(2)

    st.dataframe(resum_dies, hide_index=True)


    # ------------------------------
    # SELECCIÓ DE DATA PER AL GRÀFIC
    # ------------------------------
    dates_disponibles = sorted(df_pacient["datetime"].dt.date.unique())
    data_seleccionada = st.selectbox("Selecciona una data per al gràfic", dates_disponibles)

    # Filtrar només per la data seleccionada
    df_filtrat = df_pacient[df_pacient["datetime"].dt.date == data_seleccionada]

   # ------------------------------
    # GRÀFIC DE LÍNIA AMB COLORS PER RANGS
    # ------------------------------
    st.subheader(f"Evolució de la glucosa el dia {data_seleccionada}")

    fig2, ax2 = plt.subplots(figsize=(10, 4))

    # Llindars (pots modificar-los)
    hipo = 89
    hiper = 170

    # Assignar colors segons el valor
    colors = df_filtrat["valor_glucosa"].apply(
        lambda x: "red" if x < hipo else ("orange" if x > hiper else "green")
    )

    # Dibuixar línia base
    ax2.plot(df_filtrat["datetime"], df_filtrat["valor_glucosa"],
             linestyle="-", color="gray", alpha=0.4)

    # Dibuixar punts amb colors
    ax2.scatter(df_filtrat["datetime"], df_filtrat["valor_glucosa"],
                color=colors, s=80)

    # Línies de referència
    ax2.axhline(hipo, color="red", linestyle="--", alpha=0.5)
    ax2.axhline(hiper, color="orange", linestyle="--", alpha=0.5)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax2.set_xlabel("Hora")
    ax2.set_ylabel("Glucosa (mg/dL)")
    ax2.set_title(f"Evolució temporal de la glucosa - {pacient_seleccionat} ({data_seleccionada})")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig2)


else:
    st.info("Carrega un fitxer CSV per començar.")

