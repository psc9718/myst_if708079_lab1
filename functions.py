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


def f_fechas (archivos):

    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

    # lista con fechas ordenadas (para usarse como  indexadores de archivos)

    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

    r_f_fechas = {'i_fechas': i_fechas, 't_fechas':t_fechas}

    return r_f_fechas
# Descargar y acomodar datos

def f_ticker(archivos, data_archivos):
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
    return global_tickers
f_ticker(archivos,data_archivos)