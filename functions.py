"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: psc9718                                                                     -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/psc9718/myst_if708079_lab1                                                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
### Construir el vector de fechas a partir del vector de nombres

# estas serviran como etiquetas en dataframe y para yfinance
import pandas as pd
from data import archivos, data_archivos
import numpy as np


def f_fechas(archivos):
    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

    # lista con fechas ordenadas (para usarse como  indexadores de archivos)

    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

    r_f_fechas = {'i_fechas': i_fechas, 't_fechas': t_fechas}

    return r_f_fechas


# Descargar y acomodar datos

def f_ticker(archivos, data_archivos):
    tickers = []
    for i in archivos:
        # i = archivos[1]
        l_tickers = list(data_archivos[i]['Ticker'])
        # print(l_tickers)
        [tickers.append(i + '.MX') for i in l_tickers]
    global_tickers = np.unique(tickers).tolist()

    # Obtener posiciones historicas

    global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
    global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
    global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

    # eliminar MXN, USD, KOFL
    [global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]
    return global_tickers


f_ticker(archivos, data_archivos)

import numpy as np
import yfinance as yf
import time as time
import data as dt


def f_precios(p_global_tickers, p_fechas):
    inicio = time.time()
    data = yf.download(p_global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close",
                       interval='1d',
                       auto_adjust=False, prepost=False, threads=False)

    print('se tardo', time.time() - inicio, 'segundos')

    # convertir columna de fechas
    data_close = pd.DataFrame({i: data[i]['Close'] for i in p_global_tickers})

    # tomar solo las fechas de interes (utilizando conjuntos)
    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in dt.archivos])]

    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(p_fechas['i_fechas'])))

    # localizar todos los precios
    precios = data_close.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas]]

    # ordenar columnas lexicograficamente
    precios = precios.reindex(sorted(precios.columns), axis=1)

    return precios


def f_posicion(v_precios, v_fechas,v_pos_cas,v_df_pasiva):
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

    df_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}
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
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')

    ##Desglose

    match = 0
    v_precios.index.to_list()[match]
    # precios necesarios para la posicion
    # m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
    m2 = [v_precios.iloc[match, v_precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]

    # pos_datos['Precio_m1'] = m1
    pos_datos['Precio'] = m2

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
    v_pos_cas = k - pos_datos['Postura'].sum() - pos_comision

    # pos_value
    # la suma de las posturas(es decir, las posturas de cada activo)
    pos_value = pos_datos['Postura'].sum()

    return pos_datos, df_pasiva


