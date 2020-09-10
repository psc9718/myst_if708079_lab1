"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: psc9718                                                                    -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/psc9718/myst_if708079_lab1                                                                   -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
from os import listdir, path
from os.path import isfile, join
import numpy as np
import yfinance as yf
import time as time
import functions as fn
import data as dt

print (dt.archivos[0:4])
print (dt.data_archivos.keys().to_list()[0:4])


fechas = fn.f_fechas(archivos=dt.archivos)
# tickers
global_tickers = fn.f_ticker(archivos=dt.archivos, data_archivos=dt.data_archivos)


inicio = time.time()
data = yf.download(global_tickers, start="2018-01-31", end="2020-08-21", actions=False, group_by="close", interval='1d',
                   auto_adjust=False, prepost=False, threads=False)

print('se tardo', time.time() - inicio, 'segundos')

# convertir columna de fechas
data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

# tomar solo las fechas de interes (utilizando conjuntos)
i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in dt.archivos])]

ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(fechas['i_fechas'])))

# localizar todos los precios
precios = data_close.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas]]

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
df_pasiva = {'timestamp': ['05-01-2018'], 'capital': [k]}
#
pos_datos = dt.data_archivos[dt.archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

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

match = 0
precios.index.to_list()[match]
# precios necesarios para la posicion
m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
m2 = [precios.iloc[match, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]

pos_datos['Precio'] = m1
pos_datos['Precio_m2'] = m2

# capital destinado por accion = proporcion de capital - comisiones por la posicion
pos_datos['Capital'] = pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c

# pos_datos ['Titulos']
# Calcular los titulos a comprar de cada activo
# capital de titulos por accion
pos_datos['Titulos'] = pos_datos['Capital'] // pos_datos['Precio']

# pos_datos ['Postura']
# multiplicar los titulos a comprar de cada activo
pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']

# pos_datos ['Comision']
# calcular la comision que pagas por ejecutar la "postura"
pos_datos['Comision'] = pos_datos['Postura'] * c
pos_comision = pos_datos['Comision'].sum()

# efectivo libre en la posición
# capital-postura-comision
pos_cas = k - pos_datos['Postura'].sum() - pos_comision

# pos_value
# la suma de las posturas(es decir, las posturas de cada activo)
pos_value = pos_datos['Postura'].sum()

# guardar en una lista el timestamp
# guardar en una lista capital(valor de la postura total(suma de las posturas + cash)
# pos_cash

# for para todos los meses

for match in range(1, (len(dt.archivos))-1):

    precios.index.to_list()[match]

    m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
    pos_datos['Precio'] = m1

    # Postura x accion
    pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']

    # Valor postura
    pos_value = pos_datos['Postura'].sum()

    # Lista de valores
    df_pasiva['timestamp'].append(fechas['t_fechas'][match])
    df_pasiva['capital'].append(pos_value + pos_cas)



# Dataframe resultados
df_pasiva = pd.DataFrame(df_pasiva)
