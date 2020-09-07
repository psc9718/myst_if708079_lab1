"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: psc9718                                                                    -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository:https://github.com/psc9718/myst_if708079_lab1                                             --#
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
from os import listdir, path
from os.path import isfile, join
import numpy as np
import yfinance as yf
import time as time

### Inversión pasiva
# Lista de archivos

# Ruta absoluta de la carpeta
abspath = path.abspath('files/NAFTRAC_holdings')
archivos = [f[:-4] for f in listdir(abspath) if isfile(join(abspath, f))]

# Leer archivos
# crear un diccionario para almacenar todos los datos
data_archivos = {}

for i in archivos:
    # i = archivos[0]
    data = pd.read_csv('files/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)

    # Renombrara las columnas con lo que tiene el 1er renglon
    data.columns = list(data.iloc[0, :])

    # Columnas nan
    data = data.iloc[:, pd.notnull(data.columns)]

    #resetear el indice
    data = data.iloc[1:-1].reset_index(inplace=False, drop=True)
    #   quitar las comas en la columna de precios

    data['Precio'] = [i.replace(',', '') for i in data['Precio']]

    # quitar el asterisco de columna ticker
    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]

    # hacer conversiones de tipos de columnas a numerico
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)

    # Convertir a decimal la columna de peso (%)

    data['Peso (%)'] = data['Peso (%)'] / 100

    # guardar en diccionario
    data_archivos[i] = data

