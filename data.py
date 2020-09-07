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

### Construir el vector de fechas a partir del vector de nombres

# estas serviran como etiquetas en dataframe y para yfinance
t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# lista con fechas ordenadas (para usarse como  indexadores de archivos)

i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# Descargar y acomodar datos

tickers = []
for i in archivos:
    # i = archivos[1]
    l_tickers = list(data_archivos[i]['Ticker'])
    print(l_tickers)
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()
# Obtener posiciones historicas


global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

# eliminar MXN, USD, KOFL
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX','KOFUBL.MX' ,'BSMXB.MX']]

# Descargar y acomodar los precios historticos

inicio = time.time()
data = yf.download(global_tickers, start="2017-08-21", end="2020-08-21", actions=False, group_by="close", interval='1d',
                   auto_adjust=False, prepost=False, threads=False)
print('se tardo', time.time() - inicio, 'segundos')

# convertir columna de fechas
data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

# tomar solo las fechas de interes (utilizando conjuntos)
ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))

# localizar todos los precios
precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == ic_fechas[1])[0]) for i in ic_fechas]]

# ordenar columnas lexicograficamente
precios = precios.reindex(sorted(precios.columns), axis=1)

# POSICION INICIAL

# capital inicial·

k = 1000000

# comisiones por transaccion
c = 0.00125

# vector de comisiones historicas
comisiones = []

# Obtener posicion inicial
# los % para KOFL, KOFUBL, BMSMXB, USD asignarlos a CASH
c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
# diccionario para resultado final
inv = {'timestamp': ['05-01-2018'], 'capital': [k]}
#
pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

# extraer la lista de activos a eliminar
i_activos = list(pos_datos[list(pos_datos['Ticker'].isin(c_activos))].index)

# eliminar los activos del dataframe
pos_datos.drop(i_activos, inplace=True)

# resetar el index
pos_datos.reset_index(inplace=True, drop=True)

# agregar .MX para empatar precios

pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'

# Corregir tickers en datos
pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.1.MX', 'RA.MX')

##Desglose

match = 7
precios.index.to_list ()[match]
# precios necesarios para la posicion
m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
m2 =[precios.iloc[match, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]

pos_datos ['Precio']=m1
pos_datos ['Precio_m2']=m2

# capital destinado por accion = proporcion de capital - comisiones por la posicion
pos_datos['Capital'] = pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c

# capital de titulos por accion
pos_datos['Titulos'] = pos_datos['Capital'] // pos_datos['Precio']

# pos_datos ['Titulos']
# Calcular los titulos a comprar de cada activo
# pos_datos ['Postura']
# multiplicar los titulos a comprar de cada activo
# pos_datos ['Comision']
# calcular la comision que pagas por ejecutar la "postura"

# efectivo libre en la posición
# capital-postura-comision

# pos_value
# la suma de las posturas(es decir, las posturas de cada activo)

# guardar en una lista el timestamp
# guardar en una lista capital(valor de la postura total(suma de las posturas + cash)
# pos_cash


