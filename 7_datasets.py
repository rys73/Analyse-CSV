import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

chemin_fichier = r"C:\Users\ighik\OneDrive\Escritorio\html\py-js\fichier_csv\fichiers_7\7_datasets.csv"
chemin_sauvegarde = r"C:\Users\ighik\OneDrive\Escritorio\html\py-js\fichier_csv\fichiers_7\7_datasets_sauvegarde.csv"
chemin_pdf = r"C:\Users\ighik\OneDrive\Escritorio\html\py-js\fichier_csv\fichiers_7\7_graphiques.pdf"

fichier = pd.read_csv(
 chemin_fichier,
 parse_dates=["Date"],
 encoding="latin1")

# IMPACT MOYEN DES REMISES
fichier["Remise_pct"] = fichier["Remise"] / 100
fichier["CA_sans_Remise"] = fichier["CA"] / (1- fichier["Remise_pct"])
impact_moyen = ((fichier["CA_sans_Remise"] - fichier["CA"]) / fichier["CA_sans_Remise"]).mean() * 100
print(f"Impact moyen des remises est : {impact_moyen:.2f}%")

# CALCULER CA MENSUEL ET TRACER UNE COURBE D'EVOLUTION
fichier["Annee"] = fichier["Date"].dt.year
fichier["Mois"] = fichier["Date"].dt.month

with PdfPages(chemin_pdf) as pdf:
    CA_Mensuel = (
        fichier.groupby(["Annee", "Mois"])["CA"]
        .sum()
        .reset_index())
    CA_Mensuel["Periode"] = pd.to_datetime(
        CA_Mensuel["Annee"].astype(str) + "-" + CA_Mensuel["Mois"].astype(str).str.zfill(2))
    plt.figure(figsize=(12,6))
    plt.plot(CA_Mensuel["Periode"], CA_Mensuel["CA"], marker="o", label="CA Mensuel")
    plt.title("Evolution du CA Mensuel")
    plt.xlabel("Période")
    plt.ylabel("CA (€)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# TROUVER LES VENDEURS QUI UTILISENT LE PLUS LES REMISES
    stat_vendeur = (
    fichier.assign(Avec_remise=fichier["Remise_pct"] > 0)
    .groupby("Vendeur")
    .agg(
        Nb_ventes_avec_remise=("Avec_remise","sum"),
        Nb_total_ventes=("CA","count")))
    stat_vendeur["%_ventes_avec_remise"] = (
     (stat_vendeur["Nb_ventes_avec_remise"] / stat_vendeur["Nb_total_ventes"] * 100).round(2))
    plt.figure(figsize=(12,6))
    plt.barh(stat_vendeur.index, stat_vendeur["%_ventes_avec_remise"], color="skyblue")
    plt.xlabel("% des ventes avec remise")
    plt.ylabel("Vendeur")
    plt.title("Utilisation des remises par vendeur (%)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# COMPARE LES VENTES AVEC ET SANS REMISE
    CA_sans_remise = fichier.query("Remise_pct == 0")["CA"].sum()
    CA_avec_remise = fichier.query("Remise_pct > 0")["CA"].sum()
    plt.figure(figsize=(12,6))
    plt.pie(
      [CA_sans_remise, CA_avec_remise],
      labels=["Sans Remise", "Avec Remise"],
      autopct="%1.1f%%",
      startangle=90,
      colors=["#66b3ff", "#ff9999"])
    plt.title("Répartition du CA total avec/sans remise")
    plt.axis("equal")
    plt.gca().set_position([0.15, 0.1, 0.7, 0.8])
    pdf.savefig()
    plt.close()
 
# TROUVER LES TOP 10 PRODUITS QUI GENERENT LE PLUS DE CA
top10_produits = (
    fichier.groupby("Produit")["CA"]
    .sum()
    .reset_index()
    .sort_values("CA", ascending=False)
    .head(10))

# CLASSEMENT AVEC CA TOTAL, NOMBRE DE VENTES PAR VENDEUR, CA MOYEN
top_vendeurs = (
    fichier.groupby("Vendeur")
    .agg(
        CA_total=("CA","sum"),
        Nb_ventes=("CA","count"),
        CA_moyen=("CA","mean"))
    .sort_values("CA_total", ascending=False)
    .reset_index()
)

# VILLES LES PLUS RENTABLES : CA TOTAL, CA MOYEN, NOMBRE DE VENTES PAR VILLE
top_villes = (
    fichier.groupby("Ville")
    .agg(
        CA_total=("CA","sum"),
        CA_moyen=("CA","mean"),
        Nb_ventes=("CA","count"))
    .sort_values("CA_total", ascending=False)
    .reset_index()
)

# CA TOTAL PAR CLIENT
ca_clients = ( 
    fichier.groupby("Client_ID")["CA"]
    .sum()
    .sort_values(ascending=False)
    .reset_index())


# LOI PARETO (20% DES CLIENTS QUI FONT 80% DU CA)
ca_clients["Part_Cumulee"] = ca_clients["CA"].cumsum() / ca_clients["CA"].sum()
top_clients = ca_clients[ca_clients["Part_Cumulee"] <= 0.8]
ca_clients["Part_Cumulee"] = ca_clients["Part_Cumulee"].round(2)


# CLIENTS FIDELE (QUI ONT ACHETE AU MOINS 2 FOIS AVEC LEUR CA)
clients_fideles = (
    fichier.groupby("Client_ID")
    .agg(Nb_Achats=("CA","count"), CA_total=("CA","sum"))
    .query("Nb_Achats >= 2")
    .reset_index())

# PIVOT TABLE AVEC MULTI-INDEX : VILLE x MOIS AVEC LA SOMME DU CA
pivot_table_ville_mois = (
   fichier.pivot_table(
    index=["Ville","Annee","Mois"], 
    values="CA",
    aggfunc="sum",
    fill_value=0)
    .sort_index())

# COLONNE CALCULEE DE LA MARGE DU CA
fichier["CA_marge_calculee"] = (fichier["CA"] * 0.3).round(2)

# MARGE CUMULEE PAR VENDEUR
marge_vendeur = fichier.groupby("Vendeur")["CA_marge_calculee"].sum().sort_values(ascending=False).reset_index()

# SAUVEGARDE DU PROJET
fichier.to_csv(
    chemin_sauvegarde,
    index=False,
    encoding="latin1",
    float_format="%.2f"
)