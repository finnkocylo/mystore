from encodings import utf_8
from pprint import pprint
from glob import glob

import re
import pandas as pd
import numpy as np
import xlrd
from xlrd import open_workbook
import datetime
import os






pd.options.display.float_format = '{:,.1f}'.format
# pd.set_option('max_columns', 100)
pd.set_option('display.max_rows', 40)
#
# stock_file = sorted(glob('data/*.xlsx'))
# df = pd.concat((pd.read_excel(file)) for file in stock_file).fillna(0)
#
#
# names = {'Количество возврата': 'Возвраты', 'Услуги по доставке товара покупателю': 'Service (₽)',
# 'Дата заказа покупателем': 'Дата заказа',
#          'К перечислению Продавцу за реализованный Товар': 'Выручка', 'Артикул поставщика': 'Артикул', 'Цена розничная с учетом согласованной скидки': 'РЦ (₽)'}
# df.rename(columns=names, inplace=True)
#
#
#
# df['Дата продажи'] = pd.to_datetime(df['Дата продажи'])
# df['Дата заказа'] = pd.to_datetime(df['Дата заказа'])
#
# df['Месяц продажи'] = pd.DatetimeIndex(df['Дата продажи']).month_name()[0]
# df['Неделя продажи'] = df['Дата продажи'].apply(lambda x: x.weekofyear)
# df['День продажи'] = df['Дата продажи'].apply(lambda x: x.dayofyear)
#
#
# df['Месяц заказа'] = pd.DatetimeIndex(df['Дата заказа']).month_name()[0]
# df['Неделя заказа'] = df['Дата заказа'].apply(lambda x: x.weekofyear)
# df['День заказа'] = df['Дата заказа'].apply(lambda x: x.dayofyear)
#
#
#
# df.to_csv('data/actual.csv', encoding='utf_8')
#




df = pd.read_csv('data/actual.csv').drop('Unnamed: 0', axis=1)
col = list(df.columns)
# usefull = [
# 'Месяц продажи',
# 'Неделя продажи',
# 'День продажи',
# 'Месяц заказа',
# 'Неделя заказа',
# 'День заказа', 'Артикул', 'Размер', 'Дата заказа покупателем', 'Дата продажи', 'РЦ (₽)', 'Выручка', 'Возвраты', 'Service (₽)', 'Номер', 'Обоснование для оплаты']
# df = df[usefull]

# dft = pd.pivot_table(df, values=['РЦ (₽)', 'Выручка', 'Возвраты', 'Service (₽)'],
#                      index=['Артикул', 'Обоснование для оплаты'],
#                      aggfunc={
#                          'Выручка': 'sum',
#                          'РЦ (₽)': ['sum'],
#                          'Возвраты': 'sum',
#                          'Service (₽)': ['sum']}).reset_index()
# dft.to_csv('data/actual.csv', encoding='utf_8')
# agg({'РЦ (₽)': 'sum', 'Service (₽)': 'sum'}
code = '1532Graphite_N'
def charge_per_code(code):

    dx = df[df['Артикул'] == code].groupby(['Артикул', 'Размер', 'Номер'])['День заказа', 'День продажи',  'Service (₽)', 'РЦ (₽)', 'Выручка'].sum()
    # dx['Номер qty'] = df['Номер'].nunique()
    dx['Период'] = dx['День продажи'] - dx['День заказа']
    dx['Income'] =  dx['Выручка'] - dx['Service (₽)']
    dx = dx.reset_index()

    dx = dx.groupby(['Артикул', 'Размер'])['Income', 'Выручка', 'РЦ (₽)','Service (₽)', 'Период'].agg({'Income': 'sum', 'Выручка': 'sum', 'РЦ (₽)' :'sum',  'Service (₽)': ['sum'], 'Период': 'mean'})



    # for num in dx['Номер'].unique():


    return dx



pprint(charge_per_code(code))
# pprint(df.groupby(['Артикул', 'Номер'])['Неделя заказа', 'Неделя продажи'].sum())
# pprint(df.columns)




