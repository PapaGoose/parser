import streamlit as st
import pandas as pd

import re


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def local_html(file_name):
    with open(file_name) as f:
        st.markdown(f'{f.read()}', unsafe_allow_html=True)


regex_dict = {
    "ГОСТ":r'(?P<doc>(?:ГОСТ|ТУ|гост|ту|Гост|Ту)\b\s(\d+\w*[-.])*\d+)', 
    "Размер":r'(\d{2,4}[,]{0,1}\d{0,2}[ ]{0,1}(?:x|х)[ ]{0,1}\d{1,2}[,]{0,1}\d{0,2})',
    "Тип трубы" : r'(?:\bнасосно-компрессорная\b|\bпрямошовная\b|\bбесшовная\b|\bэлектросварная\b|\bсэ\b|\bэс\b|\bсваи\b| \
                    \bпрофиль\b|\bэп\b|\bводогазопроводная\b|\bметаллическая для сваи\b|\bобсадная\b)',
                    
    "Тип резьбы" : r'\b[Г-РТ]{4}|\b[В-М]{3}-\d|\b[A-Z]{3}\s[A-Z]{5}|\b[Б][ТС]{2}|\b[Н][КТ]{2}\s[Г]{0,1}|\b[В][С]|\b[NU]{2}',
    "Группа прочности" : r'\bP110|\bJ55|\bК[сc]{1}\d{0,2}|\bЕ[сc]{1}|\bR95|\bС95|\bN80 ?-?[тип]{0,3} ?Q|\bЛ[сc]{1}|\bL80|\bД[сc]{1}|\bМ[сc]{1}|\bE\b|\bЛ\b|\bМ\b|\bК\b|К\d{2}|N\-{0,1}80',
    "Марка стали" : r'[0][.]+[АБ]\/?0?Х?-?\d?Х?|(?<=К\d{2}\s)[12340]{1,2}|[1234(20)]{1,2}(?=\s{1,2}К\d{1,2})|(?<=К\d\d-)[1234(20]{1,2}|(?<=К\d\d\s)[1234(20]{1,2}|(?<= В )[1234(20)]{1,2}|(?<=марки )[1234(20)]{1,2}|(?<=ст.)[1234(20)]{1,2}|(?<=ст. )[1234(20)]{1,2}|20А|09Г2С-?\d{0,2}|09ГСФ[А]?|13ХФА|17Г1С\S?\w?\S?|20КСХ[0][.]+[АБ]\/?0?Х?-?\d?Х?|(?<=К\d{2}\s)[12340]{1,2}|[1234(20)]{1,2}(?=\s{1,2}К\d{1,2})|(?<=К\d\d-)[1234(20]{1,2}|(?<=К\d\d\s)[1234(20]{1,2}|(?<= В )[1234(20)]{1,2}|(?<=марки )[1234(20)]{1,2}|(?<=ст.)[1234(20)]{1,2}|(?<=ст. )[1234(20)]{1,2}|20А|09Г2С-?\d{0,2}|09ГСФ[А]?|13ХФА|17Г1С\S?\w?\S?|20КСХ|05ХГБ',
    "Класс прочности" : r'(?<=прочности )\w?\d{1,3}|не ниже \w\d{1,3}|не ниже K\d{1,3}',
    "Изоляция" : r'внутренним|наружным|трехслойный|полиэтиленовый|трехслойного|НВП|1ЭП-Т|ППУ'
}
st.set_page_config(layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
local_css("test.css")
# local_html("input.html")
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image('logo.png')

with col3:
    st.write(' ')

st.header('Кабинет администратора: Отладка алгоритма парсинга')
flag = False
text = ""
www = st.empty()
text = www.text_input("", value="", placeholder='Text', key="1")
result_dict = {}

if text:
    for key, value in regex_dict.items():
        result = re.findall(value, text)

        if result:
            if key == 'ГОСТ':
                result_dict[key] = ', '.join([i[0] for i in result])

            elif key == 'Размер':
                result = result[0].replace(' ', '').split('х')
                result_dict['Диаметр (мм)'] = result[0]
                result_dict['Толщина стенки (мм)'] = result[1]

            elif key == 'Изоляция':
                if result[0] in ['внутренним', 'наружным', 'трехслойный', 'полиэтиленовый']:
                    result_dict[key] = (result[0][:-2] + 'ая').capitalize()
                elif result[0] == 'трехслойного':
                    result_dict[key] = (result[0][:-3] + 'ая').capitalize()
                else:
                    result_dict[key] = result
                result_dict[key] = result[0].replace(' изоляция', '').capitalize()

            elif key == 'Марка стали' and len(result) >= 2:
                result_dict[key] = f'{result[0]}/{result[1]}'
            elif key in ['Тип трубы', 'Класс прочности']:
                result_dict[key] = result[0].capitalize()

            else:
                result_dict[key] = result[0]

        elif not result and key == 'Изоляция':
            result_dict[key] = 'Без изоляции'
        else:
            if key != 'Размер':
                result_dict[key] = None
 

if result_dict: 
    result_dict['indexs'] = text
    df_1 = pd.read_csv('test.csv')
    df = df_1.append(result_dict, ignore_index=True)

    df = df.astype(str)
    style = {text: [{'selector' : '', 'props' : [('border','2px solid green')]}]}
    show_df = df.set_index(pd.Index(df['indexs'].values)).iloc[-3:].drop('indexs', axis=1)

    if st.button('Очистить таблицу', key='1'):
        df = pd.read_csv('test.csv')
        df.iloc[0:0].to_csv('test.csv', index=False)
    else:
        st.markdown(show_df.transpose().style.set_table_styles(style).to_html(), unsafe_allow_html=True)
        df.to_csv('test.csv', index=False)
    st.markdown('')

    
