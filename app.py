import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import streamlit as st

# Layout
st.set_page_config(page_title='Elasticidade de Preço',
                   page_icon=':moneybag:',
                   layout='wide',
                   menu_items={
                       'Get Help': 'https://github.com/matheusventurads',
                       'Report a bug': 'mailto:matheusventura15@gmail.com',
                       'About': '# Developed by [Matheus Ventura](https://www.linkedin.com/in/matheus-ventura/), powered by [Comunidade DS](https://www.comunidadeds.com/)'
                   })

st.title(':dollar: Elasticidade de Preço')


@st.cache_data
def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://images.unsplash.com/photo-1557683304-673a23048d34?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1482&q=80");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


@st.cache_data
def load_data():
    df1 = pd.read_csv('data/processed/business_performance.csv')
    df2 = pd.read_csv('data/processed/crossprice.csv')
    df3 = pd.read_csv('data/processed/elasticity.csv')

    return df1, df2, df3


@st.cache_data
def discount_calculation(df_elasticity, promotion, radio_button):
    #dicionario para armazenar resultados
    performance = {
            'name': [],
            'current_revenue': [],
            # 'current_demand': [],
            # 'new_demand': [],
            'worstcase_revenue':[],
            'risked_revenue':[],
            'expected_revenue':[],
            'variance':[],
            'variance_perc':[]
    }


    if radio_button == 'Acréscimo':
        pc_promo = -1*promotion/100
    else:
        pc_promo = promotion/100


    for i in range(len(df_elasticity)):
        mean_price = df_elasticity['price_mean'][i]
        demand = df_elasticity['quantity_total'][i]

        # preço promocional
        new_price = mean_price*(1-pc_promo)

        # elasticidade com base na variação do preço
        percent_elasticity = pc_promo*df_elasticity['price_elasticity'][i]

        # cálculo da nova demanda considerando a variação
        new_demand = demand-(percent_elasticity*demand)

        # faturamento atual
        revenue = round(mean_price*demand, 2)

        # faturamento com novo preço e nova demanda
        new_revenue = round(new_price*new_demand, 2) if round(new_price*new_demand, 2) > 0 else 0

        # caso a demanda não altere, o quanto custa essa redução
        loss_revenue = round(revenue*(1-pc_promo), 2)

        # risco de aplicar promoção e não houver aumento
        risked_revenue = round(revenue-loss_revenue, 2)

        # variação entre faturamento atual e previsto
        variance = round(new_revenue-revenue ,2)

        # variação percentual
        variance_perc = round(((new_revenue-revenue)/revenue)*100,2)

        # agrupando valores
        performance['name'].append(df_elasticity['name'][i])
        performance['current_revenue'].append(revenue)
        # performance['current_demand'].append(demand)
        # performance['new_demand'].append(new_demand)
        performance['worstcase_revenue'].append(loss_revenue)
        performance['risked_revenue'].append(risked_revenue)
        performance['expected_revenue'].append(new_revenue)
        performance['variance'].append(variance)
        performance['variance_perc'].append(variance_perc)

    resultado = pd.DataFrame(performance)
    return resultado



def _applycolor(val):
    return f'color: {"#FF6B6B" if val < 0 else "lightgreen"}'


def _format_arrow(val):
    return f"{'↑' if val > 0 else '↓'} {val}%"


# Set background
set_bg_hack_url()

# Loading datasets
df_bp, df_cp, df_e = load_data()

tab1, tab2, tab3 = st.tabs(['Business Performance', 'Elasticidade de Preço dos Produtos', 'Elasticidade Cruzada'])


with tab1:
    button = st.radio(
        'Escolha a opção para cálculo do preço:',
        ['Acréscimo', 'Desconto'],
        captions=['Para aplicar o aumento no preço dos produtos.', 'Para aplicar o desconto no preço dos produtos.']
    )

    promo_slider = st.slider('Promoção',
                            min_value=1,
                            max_value=30,
                            value=10,
                            help='Valor em porcentagem aplicado no preço')

    data = discount_calculation(df_e, promo_slider, button)

    st.markdown('Resultados com base na elasticidade de cada produto:', help='Passe o mouse sobre as colunas para descrição detalhada')

    st.dataframe(data.style
                .format(precision=2)
                .format('${}', subset=['current_revenue', 'worstcase_revenue', 'risked_revenue', 'expected_revenue', 'variance'])
                .format(_format_arrow, subset=['variance_perc'])
                .applymap(_applycolor, subset=['variance', 'variance_perc']),
                use_container_width=True,
                column_config={
                    'name': st.column_config.TextColumn(
                        'Produto',
                        help='Nome do produto'
                    ),
                    'current_revenue': st.column_config.NumberColumn(
                        'Receita Atual',
                        help='Receita considerando preço atual'
                    ),
                    'worstcase_revenue': st.column_config.NumberColumn(
                        'Pior Cenário',
                        help='Receita considerando que a variação no preço não apresentou efeito'
                    ),
                    'risked_revenue': st.column_config.NumberColumn(
                        'Valor Arriscado',
                        help='Diferença entre a Receita Atual e Pior Cenário'
                    ),
                    'expected_revenue': st.column_config.NumberColumn(
                        'Receita Esperada',
                        help='Valor esperado após aplicação da promoção'
                    ),
                    'variance': st.column_config.NumberColumn(
                        'Variação',
                        help='Diferença entre Valor Esperado e Receita Atual'
                    ),
                    'variance_perc': st.column_config.NumberColumn(
                        'Porcentagem',
                        help='Variação em porcentagem'
                    )
                },
                hide_index=True
    )

    st.caption('''
    :question: Note que há produtos que não seguem a Lei da Procura,
    com aplicação do desconto há redução na demanda.  
    Chamados **:violet[Bens de Veblen]** têm mais demanda quando o preço é elevado.  
    Podem ser exemplificados como bens de luxo que satisfazem o consumidor
    justamente pelo alto preço, ou seja, são *símbolo de status*.
''')


with tab2:
    st.markdown('''
    Tabela contendo as informações de elasticidade calculada
    e valores obtidos na regressão linear de cada produto.
    ''',
    help='Passe o mouse pelo nome de cada coluna para mais detalhes')

    st.dataframe(df_e[['name', 'price_elasticity', 'intercept', 'slope', 'rsquared', 'p_value']],
                 use_container_width=True,
                 column_config={
                     'name': st.column_config.TextColumn(
                         'Produto',
                         help='Nome do produto'
                     ),
                     'price_elasticity': st.column_config.NumberColumn(
                         'Elasticidade-preço',
                         help='Elasticidade-preço da demanda do produto'
                     ),
                     'intercept': st.column_config.NumberColumn(
                         'Intercepto',
                         help='Intercepto da regressão preço-demanda'
                     ),
                     'slope': st.column_config.NumberColumn(
                         'Inclinação',
                         help='Inclinação da regressão preço-demanda'
                     ),
                     'rsquared': st.column_config.NumberColumn(
                         'R²',
                         help='Coeficiente de correlação entre preço e demanda'
                     ),
                     'p_value': st.column_config.NumberColumn(
                         'p-valor',
                         help='Probabilidade da variação observada ser aleatória'
                     )
                 },
                 hide_index=True)
    

with tab3:
    st.markdown('Encontre a elasticidade cruzada entre dois produtos:')
    
    col1, col2 = st.columns((2,1))
    df_cp.set_index('name', inplace=True)

    with col1:
       
        option = st.selectbox(
            'Selecione o primeiro produto:',
            (df_cp.index)
        )
    
        option2 = st.selectbox(
        'Selecione o segundo produto:',
        (df_cp.columns)
        )

    with col2:
        st.header('Elasticidade cruzada',
                  divider='violet',
                  help='''Note que a elasticidade cruzada entre o Produto A em relação a B,  
            é diferente da elasticidade de B em relação a A'''
            )

        st.metric('Valor da elasticidade cruzada',
                  df_cp.at[option, option2],
                  label_visibility='collapsed')
    
    st.divider()

    st.markdown('Relação completa da elasticidade cruzada entre os produtos:')
    
    st.dataframe(df_cp,
                 use_container_width=True)
    

css='''
[data-testid="StyledLinkIconContainer"] {
    height: fit-content;
    width: fit-content;
    margin: auto;
}

[data-testid="metric-container"] {
    height: fit-content;
    width: fit-content;
    margin: auto;
}

[data-testid="metric-container"] > div {
    height: fit-content;
    width: fit-content;
    margin: auto;
}

[data-testid="metric-container"] label {
    height: fit-content;
    width: fit-content;
    margin: auto;
}
[data-testid="stMetricValue"] {
    font-size: 70px;
}
'''
st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)