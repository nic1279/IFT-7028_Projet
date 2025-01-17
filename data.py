import pandas as pd
import numpy as np
import random

# Permet de lire tout les feuilles d'un fichier Excel et de les mettre dans un dictionnaire
file = pd.ExcelFile(r'DataSet.xlsx')
dict_project = {sheet_name: file.parse(sheet_name) for sheet_name in file.sheet_names}


def assignation_palette(df_palettisation):

    liste_mur = df_palettisation[['Type']].to_numpy()
    liste_palette = []
    compteur_palette = 0
    compteur_palette_actuelle_mur = 0
    compteur_palette_actuelle_plafond = 0
    compteur_palette_mur = 0
    compteur_palette_plafond = 0

    for panneau in liste_mur:

        if panneau == 'Mur' or panneau == 'Coin' or panneau == 'Retour':
            if compteur_palette_mur == 0:
                compteur_palette_actuelle_mur = compteur_palette + 1
                compteur_palette += 1
            if compteur_palette_mur < 7:
                liste_palette.append(compteur_palette_actuelle_mur)
                compteur_palette_mur += 1
            else:
                compteur_palette_mur = 1
                compteur_palette_actuelle_mur = compteur_palette + 1
                liste_palette.append(compteur_palette_actuelle_mur)
                compteur_palette += 1

        if panneau == 'Plafond':
            if compteur_palette_plafond == 0:
                compteur_palette_actuelle_plafond = compteur_palette + 1
                compteur_palette += 1
            if compteur_palette_plafond < 7:
                liste_palette.append(compteur_palette_actuelle_plafond)
                compteur_palette_plafond += 1
            else:
                compteur_palette_plafond = 1
                compteur_palette_actuelle_plafond = compteur_palette + 1
                liste_palette.append(compteur_palette_actuelle_plafond)
                compteur_palette += 1

    df_palettisation['Palette'] = liste_palette
    return df_palettisation


def capacite_palette(df_palette):
    df_capacite_palette = df_palette['Palette'].value_counts().to_frame()
    df_capacite_palette.columns = ['Capacite']
    df_capacite_palette['Palette'] = df_capacite_palette.index
    test = df_capacite_palette.sort_values(by='Palette')
    return test[['Palette', 'Capacite']]


# Pour tout les classements de sous-type : mur, retour, coin, plafond
# 1. En ordre (panneau 1, 2, 3, ... ,n-1, n)
def heuristic_ordre(df):
    df_ordered = df.sort_values('Id')
    df_palette = assignation_palette(df_ordered)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2


# 2. Par type (plafonds, murs, murs retours ...)
def heuristic_type(df):
    df['Type'] = pd.Categorical(df['Type'], ['Mur', 'Retour', 'Coin', 'Plafond'])
    df_ordered = df.sort_values(['Type', 'Secteur'])
    df_palette = assignation_palette(df_ordered)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2


# 3. Par secteur aléatoire
def heuristic_sector_random(df):
    list_int = list(range(1, df.shape[0] + 1))
    random.Random(17).shuffle(list_int)
    df['random'] = list_int
    df_ordered = df.sort_values(['Secteur', 'random'])
    df_palette = assignation_palette(df_ordered)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2


# 4. Par secteur en ordre
def heuristic_sector(df):
    df_ordered = df.sort_values(['Secteur', 'Id'])
    df_palette = assignation_palette(df_ordered)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2


# 5. Par secteur par type (classé par type au sein d'un même secteur)
def heuristic_sector_type(df):
    df['Type'] = pd.Categorical(df['Type'], ['Mur', 'Retour', 'Coin', 'Plafond'])
    df_ordered = df.sort_values(['Secteur', 'Type'])
    df_palette = assignation_palette(df_ordered)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2


# 6. Par secteur par temps (ordre décroissant par 7 panneaux, plus long au plus court)
def heuristic_sector_time(df):
    df_1 = heuristic_sector_random(df)
    df_2 = df_1.reset_index()
    df_2['index_reset'] = df_2.index
    df_2['group'] = df_2['index_reset'].apply(lambda x: int(x/7) + 1)
    df_ordered = df_2.sort_values(['Secteur', 'group', 'Soudure'], ascending=[True, True, False])
    df_palette = assignation_palette(df_ordered)
    # df_ordered2 = df_ordered.drop(['group', 'index_reset'], axis=1)
    df_ordered2 = df_palette[['No', 'Id', 'Type', 'Secteur', 'Largeur', 'Hauteur', 'Soudure', 'Peinture', 'Finition', 'Setup', 'Finition_Long', 'Palette']]
    return df_ordered2

# Par secteur par temps (minimiser moyenne mobile sur 7 panneaux)
# En attente, requiert un modèle d'optimisation


for project, df in dict_project.items():
    heuristic_ordre(df).to_csv(r'actual\ordre\heuristic_ordre_{}.csv'.format(project))
    heuristic_type(df).to_csv(r'actual\ordre\heuristic_type_{}.csv'.format(project))
    heuristic_sector_random(df).to_csv(r'actual\ordre\heuristic_sector_random_{}.csv'.format(project))
    heuristic_sector(df).to_csv(r'actual\ordre\heuristic_sector_{}.csv'.format(project))
    heuristic_sector_type(df).to_csv(r'actual\ordre\heuristic_sector_type_{}.csv'.format(project))
    heuristic_sector_time(df).to_csv(r'actual\ordre\heuristic_sector_time_{}.csv'.format(project))

    capacite_palette(heuristic_ordre(df)).to_csv(r'actual\palette\heuristic_ordre_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_type(df)).to_csv(r'actual\palette\heuristic_type_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_random(df)).to_csv(r'actual\palette\heuristic_sector_random_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector(df)).to_csv(r'actual\palette\heuristic_sector_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_type(df)).to_csv(r'actual\palette\heuristic_sector_type_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_time(df)).to_csv(r'actual\palette\heuristic_sector_time_{}.csv'.format(project), index=False)

for project, df in dict_project.items():
    df_assignation_palette1 = heuristic_sector(df)
    df_assignation_palette2 = df_assignation_palette1[['No', 'Palette']]

    heuristic_ordre_df = (heuristic_ordre(df)).drop('Palette', 1)
    heuristic_type_df = (heuristic_type(df)).drop('Palette', 1)
    heuristic_sector_random_df = (heuristic_sector_random(df)).drop('Palette', 1)
    heuristic_sector_df = (heuristic_sector(df)).drop('Palette', 1)
    heuristic_sector_type_df = (heuristic_sector_type(df)).drop('Palette', 1)
    heuristic_sector_time_df = heuristic_sector_time(df).drop('Palette', 1)

    heuristic_ordre_df2 = heuristic_ordre_df.merge(df_assignation_palette2, on='No', how='left')
    heuristic_type_df2 = heuristic_type_df.merge(df_assignation_palette2, on='No', how='left')
    heuristic_sector_random_df2 = heuristic_sector_random_df.merge(df_assignation_palette2, on='No', how='left')
    heuristic_sector_df2 = heuristic_sector_df.merge(df_assignation_palette2, on='No', how='left')
    heuristic_sector_type_df2 = heuristic_sector_type_df.merge(df_assignation_palette2, on='No', how='left')
    heuristic_sector_time_df2 = heuristic_sector_time_df.merge(df_assignation_palette2, on='No', how='left')

    heuristic_ordre_df2.to_csv(r'test\ordre\heuristic_ordre_{}.csv'.format(project))
    heuristic_type_df2.to_csv(r'test\ordre\heuristic_type_{}.csv'.format(project))
    heuristic_sector_random_df2.to_csv(r'test\ordre\heuristic_sector_random_{}.csv'.format(project))
    heuristic_sector_df2.to_csv(r'test\ordre\heuristic_sector_{}.csv'.format(project))
    heuristic_sector_type_df2.to_csv(r'test\ordre\heuristic_sector_type_{}.csv'.format(project))
    heuristic_sector_time_df2.to_csv(r'test\ordre\heuristic_sector_time_{}.csv'.format(project))

    capacite_palette(heuristic_ordre_df2).to_csv(r'test\palette\heuristic_ordre_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_type_df2).to_csv(r'test\palette\heuristic_type_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_random_df2).to_csv(r'test\palette\heuristic_sector_random_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_df2).to_csv(r'test\palette\heuristic_sector_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_type_df2).to_csv(r'test\palette\heuristic_sector_type_{}.csv'.format(project), index=False)
    capacite_palette(heuristic_sector_time_df2).to_csv(r'test\palette\heuristic_sector_time_{}.csv'.format(project), index=False)





