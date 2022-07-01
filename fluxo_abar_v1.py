# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 14:02:30 2022

@author: est.gustavopietruza

MODELO DE FLUXO DE CAIXA PARA CÁLCULO DA AMORTIZAÇÃO E PAGAMENTO DE JUROS DE ATIVOS DA SANEPAR

Inputs: Nome do Ativo / VNR / Vida útil / VMU

Cálculo da Amortização e dos Juros pagos anualmente do valor total de ativos da Sanepar, para cada ano.

Criação de fluxo de caixa de pagamento de Amortizações + Juros do valor total dos ativos da Sanepar, para cada ano.

Glossário
    VNR: Valor Novo de Reposição 
    VMU: Valor de Mercado em Uso 
    QRR: Quota de Reposição Regulatória 
    JCP: Juros sobre Capital Próprio
    JR: Justa Rentabilidade 

Totais:
    VNR = Soma dos VNR individuais
    Vida útil[anos] = VNR Total > 0; Média Ponderada dos anos (VNR * Vida útil[anos])
    Taxa dep.[R$/ano] = Soma das Taxas individuais
    Taxa dep.[%a.a.] = VNR Total > 0; Média Ponderada das taxas (VNR * Taxa dep.[%a.a.])
    Depreciação Acum.[R$] = Soma das Dep. Acum. individuais
    Depreciação Acum.[%] = VNR Total > 0; Média Ponderada das taxas (VNR * Dep. Acum.[%])
    Vida útil remanesc.[%] = Taxa dep.[%a.a.] Total > 0; Média Ponderada das taxas (VNR * Vida útil remanesc.[%])
    Vida útil remanesc.[anos] = VNR Total > 0; Média Ponderada dos anos (VNR * Vida útil remanesc.[anos])
    VMU = Soma dos VMU individuais

Itens Necessários:
    Ativo
    VNR (Valor Original do Ativo)
    Vida útil[anos]
    Taxa dep.[R$/ano] = VNR / Vida útil[anos]
    Taxa dep.[%a.a.] = 1 / Vida útil[anos]
    Depreciação Acum.[R$] = VNR - VMU
    Depreciação Acum.[%] = Depreciação Acum.[R$] / VNR
    Vida útil remanesc.[%] = 1 - Depreciação Acum.[%]
    Vida útil remanesc.[anos] = Vida útil[anos] * Vida útil remanesc.[%]
    VMU (VNR - Depreciação Acumulada)
    Total de cada Item
    QRR (Amortização do Ativo dado por VNR * Taxa dep.[%a.a.])
    JCP (Taxa de juros dada, TMA * VMU)
    JR (Amortização + Juros)
    Fluxo
    VP
    VP acum.
    TIR

Determinação dos valores seguintes ao ano:
    VNR(n):
        if Dep. Acum.[R$](n) = VNR/(n-1):
            VNR(n) = 0
        elif Vida útil remanesc.[anos](n) < 1:
            VNR(n) = Vida útil remanesc.[anos](n) * VNR(n-1)
        else:
            VNR(n) = VNR(n-1)
    
    Dep. Acum.[R$](n):    
        if Dep. Acum.[R$](n-1) + Taxa dep.[R$/ano](n) > VNR(n-1):
            Dep. Acum.[R$](n) = VNR(n-1)
        else:
            Dep. Acum.[R$](n) = Dep. Acum.[R$](n-1) + Taxa dep.[R$/ano](n)
    
    Taxa Dep. [R$/ano](n) = VNR(n-1) / Vida útil[anos]
    
    Dep. Acum. [%](n):
        if VNR(n) > 0:
            Dep. Acum. [%](n) = Dep. Acum.[R$](n) / VNR(n)
        else:
            Dep. Acum. [%](n) = 0
            
    Vida útil remanesc.[%]¹:
        if VNR(n) > 0:
            Vida útil remanesc.[%](n) = VMU(n) / VNR(n-1)
        else:
            Vida útil remanesc.[%](n) = 0
            
    VMU(n):
        VMU(n) = VNR(n-1) - Dep. Acum.[R$](n)
        
Valores do Fluxo:
    Fluxo(0) = -VMU(0)
    Fluxo(1) = JR(1)
    Fluxo(2) = JR(2)
    Fluxo(n) = JR(n)
    ...
    
    VP(n) = Fluxo(n) / (1 + TMA)^n
    
    VP Acum.(n) = ...+ VP(n-2) + VP(n-1) + VP(n)
"""

import pandas as pd
import numpy as np

def arruma_nome_colunas(df):
    #Ajusta os nomes das colunas de um DataFrame removendo espaços em branco no início e fim da string
    dataframe = df.copy()
    colunas = dataframe.columns.astype(str)
    colunas_new = []
    for i in colunas:
        x = i.strip().upper()
        colunas_new.append(x)
    dataframe.columns = colunas_new 
    return dataframe

#Cálculo da Depreciação Acumulada[%] (DA_per)
def DA_per(da_val, VNR):
    aux = da_val/VNR
    aux[abs(aux) == np.inf] = 0
    aux[np.isnan(aux) == True] = 0
    return aux

#Cálculo da Taxa de Depreciação[R$/ano] (TD_val) (VU = vida útil [anos])
def TD_val(VNR, VU):
    aux = VNR/VU
    aux[abs(aux) == np.inf] = 0
    aux[np.isnan(aux) == True] = 0
    return aux

#Cálculo da Taxa de Depreciação[%a.a.] (TD_per) (VU = vida útil [anos])
def TD_per(VU):
    aux = 1/VU
    aux[abs(aux) == np.inf] = 0
    aux[np.isnan(aux) == True] = 0
    return aux

#Cálculo da Média Ponderada
def media_ponderada(x,peso):
    var = x * peso
    tot = x.sum()
    aux = var.sum()
    media_pond = aux / tot
    return media_pond

#Criador de dataframe formatado ABAR
def formata_df(df_base):
    #TD_val
    df_base.loc[:,'TAXA_DEP[R$/ANO]'] = TD_val(df_base.loc[:,'VNR'],df_base.loc[:,'VIDA ÚTIL [ANOS]'])
    
    #TD_per
    df_base.loc[:,'TAXA_DEP[%A.A.]'] = TD_per(df_base.loc[:,'VIDA ÚTIL [ANOS]'])
    
    #DA_val
    df_base.loc[:,'DEP_ACUM[R$]'] = df_base.loc[:,'VNR'] - df_base.loc[:,'VMU']
    
    #DA_per
    df_base.loc[:,'DEP_ACUM[%]'] = DA_per(df_base.loc[:,'DEP_ACUM[R$]'], df_base.loc[:,'VNR'])
    
    #VUR_per
    df_base.loc[:,'VIDA_UTIL_REM[%]'] = 1 - df_base.loc[:,'DEP_ACUM[%]']
    
    #VUR_anos
    df_base.loc[:,'VIDA_UTIL_REM[ANOS]'] = df_base.loc[:,'VIDA ÚTIL [ANOS]'] * df_base.loc[:,'VIDA_UTIL_REM[%]']
    
    #Cálculo do Total
    df_origin = df_base.copy()
    df_base.loc['TOTAL',:] = np.nan
    df_base.loc['TOTAL', 'ATIVO'] = 'TOTAL'
    
    df_base.loc['TOTAL', 'VNR'] = df_base.loc[:, 'VNR'].sum()
    
    df_base.loc['TOTAL', 'VMU'] = df_base.loc[:, 'VMU'].sum()
    
    df_base.loc['TOTAL', 'TAXA_DEP[R$/ANO]'] = df_base.loc[:, 'TAXA_DEP[R$/ANO]'].sum()
    
    df_base.loc['TOTAL', 'DEP_ACUM[R$]'] = df_base.loc[:, 'DEP_ACUM[R$]'].sum()
    
    if df_base.loc['TOTAL','VNR'] > 0:
        df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = media_ponderada( df_origin.loc[:,'VNR'], df_origin.loc[:,'VIDA ÚTIL [ANOS]'])
        df_base.loc['TOTAL', 'DEP_ACUM[%]'] = media_ponderada(df_origin.loc[:,'VNR'], df_origin.loc[:,'DEP_ACUM[%]'])      
        df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = media_ponderada(df_origin.loc[:,'VNR'], df_origin.loc[:,'TAXA_DEP[%A.A.]'])
        df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = media_ponderada( df_origin.loc[:,'VNR'], df_origin.loc[:,'VIDA_UTIL_REM[ANOS]'])
    else:
        df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = 0
        df_base.loc['TOTAL', 'DEP_ACUM[%]'] = 0
        df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = 0
        df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = 0
        
    if df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] > 0:
        df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = media_ponderada(df_origin.loc[:,'VNR'], df_origin.loc[:,'VIDA_UTIL_REM[%]'])
    else:
        df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = 0

    return df_base


#Cálculo do VNR para o ano seguinte
def VNR_seg_ajust(VNR_ant, da_val, vur_anos):
    aux = VNR_ant
    aux[aux == da_val] = 0
    aux[vur_anos < 1] = vur_anos * aux
    return aux

#Cálculo do VNR para o ano seguinte
def VNR_seg_n_ajust(VNR_ant, da_val):
    aux = VNR_ant
    aux[aux == da_val] = 0
    return aux

#Cálculo da Depreciação Acumulada[R$] para o ano seguinte
def DA_val_seg(VNR_ant,da_val_ant,td_val):
    aux = da_val_ant + td_val
    aux[aux > VNR_ant] = VNR_ant
    return aux

#Cálculo da Vida Útil Remanescente[%] para o ano seguinte
def VUR_per_seg(VNR_ant,VMU):
    aux = VMU / VNR_ant
    aux[abs(aux) == np.inf] = 0
    aux[np.isnan(aux) == True] = 0
    return aux

def fluxo_df_ajust(df_origin, p):
    #Cria um vetor com o DataFrame inicial inserido
    df_all = [df_origin]
    #Cria um DataFrame para inserir os dados para o fluxo de caixa
    d = {'QRR': [] , 'JCP': [], 'JR': []}
    df_fluxo = pd.DataFrame(data = d)
    #Criação dos dados para fluxo de caixa base
    df_fluxo.loc[0, 'QRR'] = df_origin.loc['TOTAL', 'VNR'] * df_origin.loc['TOTAL', 'TAXA_DEP[%A.A.]']
    df_fluxo.loc[0, 'JCP'] = df_origin.loc['TOTAL', 'VMU'] * tma
    df_fluxo.loc[0,'JR'] = df_fluxo.loc[0, 'QRR'] + df_fluxo.loc[0, 'JCP']
    for i in p:       
        #Cria uma cópia da base original com células vazias e sem a linha do total
        df_origin = df_origin.iloc[0:-1,:]
        df_seguinte = df_origin.copy()
        df_seguinte.iloc[:,:] = ''
        
        #Preenchimento dos dados
        df_seguinte.loc[:,'ATIVO'] = df_origin.loc[:,'ATIVO']
        
        df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'] = df_origin.loc[:,'VIDA ÚTIL [ANOS]']
        
        df_seguinte.loc[:,'TAXA_DEP[R$/ANO]'] = df_origin.loc[:,'VNR'] / df_seguinte.loc[:,'VIDA ÚTIL [ANOS]']
        
        df_seguinte.loc[:,'TAXA_DEP[%A.A.]'] = TD_per(df_origin.loc[:,'VIDA ÚTIL [ANOS]'])
        
        df_seguinte.loc[:,'DEP_ACUM[R$]'] = DA_val_seg(df_origin.loc[:,'VNR'], df_origin.loc[:,'DEP_ACUM[R$]'], df_seguinte.loc[:,'TAXA_DEP[R$/ANO]'])
        
        df_seguinte.loc[:,'VMU'] = df_origin.loc[:,'VNR'] - df_seguinte.loc[:,'DEP_ACUM[R$]']
        
        df_seguinte.loc[:,'VIDA_UTIL_REM[%]'] = VUR_per_seg(df_origin.loc[:,'VNR'], df_seguinte.loc[:,'VMU'])
        
        df_seguinte.loc[:,'VIDA_UTIL_REM[ANOS]'] = df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'] * df_seguinte.loc[:,'VIDA_UTIL_REM[%]']
        
        df_seguinte.loc[:,'VNR'] = VNR_seg_ajust(df_origin.loc[:,'VNR'], df_seguinte.loc[:,'DEP_ACUM[R$]'], df_seguinte.loc[:,'VIDA_UTIL_REM[ANOS]'])
        
        df_seguinte.loc[:,'DEP_ACUM[%]'] = DA_per(df_seguinte.loc[:,'DEP_ACUM[R$]'], df_seguinte.loc[:,'VNR'])
        
        #Cálculo do Total
        df_base = df_seguinte.copy()
        df_base.loc['TOTAL',:] = np.nan
        df_base.loc['TOTAL', 'ATIVO'] = 'TOTAL'
        
        df_base.loc['TOTAL', 'VNR'] = df_base.loc[:, 'VNR'].sum()
        
        df_base.loc['TOTAL', 'VMU'] = df_base.loc[:, 'VMU'].sum()
        
        df_base.loc['TOTAL', 'TAXA_DEP[R$/ANO]'] = df_base.loc[:, 'TAXA_DEP[R$/ANO]'].sum()
        
        df_base.loc['TOTAL', 'DEP_ACUM[R$]'] = df_base.loc[:, 'DEP_ACUM[R$]'].sum()
        
        if df_base.loc['TOTAL','VNR'] > 0:
            df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = media_ponderada( df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'])
            df_base.loc['TOTAL', 'DEP_ACUM[%]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'DEP_ACUM[%]'])      
            df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'TAXA_DEP[%A.A.]'])
            df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = media_ponderada( df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA_UTIL_REM[ANOS]'])
        else:
            df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = 0
            df_base.loc['TOTAL', 'DEP_ACUM[%]'] = 0
            df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = 0
            df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = 0
            
        if df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] > 0:
            df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA_UTIL_REM[%]'])
        else:
            df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = 0
        #Coloca o DataFrame num array
        df_all.append(df_base)
        #Transforma o novo DataFrame no df_nase
        df_origin = df_base
        #Criação dos dados seguintes para fluxo de caixa
        df_fluxo.loc[i+1, 'QRR'] = df_origin.loc['TOTAL', 'VNR'] * df_origin.loc['TOTAL', 'TAXA_DEP[%A.A.]']
        df_fluxo.loc[i+1, 'JCP'] = df_origin.loc['TOTAL', 'VMU'] * tma
        df_fluxo.loc[i+1,'JR'] = df_fluxo.loc[i+1, 'QRR'] + df_fluxo.loc[i+1, 'JCP']
       
    return df_all, df_fluxo

def fluxo_df_n_ajust(df_origin, p):
    #Cria um vetor com o DataFrame inicial inserido
    df_all = [df_origin]
    #Cria um DataFrame para inserir os dados para o fluxo de caixa
    d = {'QRR': [] , 'JCP': [], 'JR': []}
    df_fluxo = pd.DataFrame(data = d)
    #Criação dos dados para fluxo de caixa base
    df_fluxo.loc[0, 'QRR'] = df_origin.loc['TOTAL', 'VNR'] * df_origin.loc['TOTAL', 'TAXA_DEP[%A.A.]']
    df_fluxo.loc[0, 'JCP'] = df_origin.loc['TOTAL', 'VMU'] * tma
    df_fluxo.loc[0,'JR'] = df_fluxo.loc[0, 'QRR'] + df_fluxo.loc[0, 'JCP']
    for i in p:       
        #Cria uma cópia da base original com células vazias e sem a linha do total
        df_origin = df_origin.iloc[0:-1,:]
        df_seguinte = df_origin.copy()
        df_seguinte.iloc[:,:] = ''
        
        #Preenchimento dos dados
        df_seguinte.loc[:,'ATIVO'] = df_origin.loc[:,'ATIVO']
        
        df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'] = df_origin.loc[:,'VIDA ÚTIL [ANOS]']
        
        df_seguinte.loc[:,'TAXA_DEP[R$/ANO]'] = df_origin.loc[:,'VNR'] / df_seguinte.loc[:,'VIDA ÚTIL [ANOS]']
        
        df_seguinte.loc[:,'TAXA_DEP[%A.A.]'] = TD_per(df_origin.loc[:,'VIDA ÚTIL [ANOS]'])
        
        df_seguinte.loc[:,'DEP_ACUM[R$]'] = DA_val_seg(df_origin.loc[:,'VNR'], df_origin.loc[:,'DEP_ACUM[R$]'], df_seguinte.loc[:,'TAXA_DEP[R$/ANO]'])
        
        df_seguinte.loc[:,'VMU'] = df_origin.loc[:,'VNR'] - df_seguinte.loc[:,'DEP_ACUM[R$]']
        
        df_seguinte.loc[:,'VIDA_UTIL_REM[%]'] = VUR_per_seg(df_origin.loc[:,'VNR'], df_seguinte.loc[:,'VMU'])
        
        df_seguinte.loc[:,'VIDA_UTIL_REM[ANOS]'] = df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'] * df_seguinte.loc[:,'VIDA_UTIL_REM[%]']
        
        df_seguinte.loc[:,'VNR'] = VNR_seg_n_ajust(df_origin.loc[:,'VNR'], df_seguinte.loc[:,'DEP_ACUM[R$]'])
        
        df_seguinte.loc[:,'DEP_ACUM[%]'] = DA_per(df_seguinte.loc[:,'DEP_ACUM[R$]'], df_seguinte.loc[:,'VNR'])
        
        #Cálculo do Total
        df_base = df_seguinte.copy()
        df_base.loc['TOTAL',:] = np.nan
        df_base.loc['TOTAL', 'ATIVO'] = 'TOTAL'
        
        df_base.loc['TOTAL', 'VNR'] = df_base.loc[:, 'VNR'].sum()
        
        df_base.loc['TOTAL', 'VMU'] = df_base.loc[:, 'VMU'].sum()
        
        df_base.loc['TOTAL', 'TAXA_DEP[R$/ANO]'] = df_base.loc[:, 'TAXA_DEP[R$/ANO]'].sum()
        
        df_base.loc['TOTAL', 'DEP_ACUM[R$]'] = df_base.loc[:, 'DEP_ACUM[R$]'].sum()
    
        if df_base.loc['TOTAL','VNR'] > 0:
            df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = media_ponderada( df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA ÚTIL [ANOS]'])
            df_base.loc['TOTAL', 'DEP_ACUM[%]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'DEP_ACUM[%]'])      
            df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'TAXA_DEP[%A.A.]'])
            df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = media_ponderada( df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA_UTIL_REM[ANOS]'])
        else:
            df_base.loc['TOTAL', 'VIDA ÚTIL [ANOS]'] = 0
            df_base.loc['TOTAL', 'DEP_ACUM[%]'] = 0
            df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] = 0
            df_base.loc['TOTAL', 'VIDA_UTIL_REM[ANOS]'] = 0
            
        if df_base.loc['TOTAL', 'TAXA_DEP[%A.A.]'] > 0:
            df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = media_ponderada(df_seguinte.loc[:,'VNR'], df_seguinte.loc[:,'VIDA_UTIL_REM[%]'])
        else:
            df_base.loc['TOTAL','VIDA_UTIL_REM[%]'] = 0
        
        #Coloca o DataFrame num array
        df_all.append(df_base)
        #Transforma o novo DataFrame no df_nase
        df_origin = df_base
        #Criação dos dados seguintes para fluxo de caixa
        df_fluxo.loc[i+1, 'QRR'] = df_origin.loc['TOTAL', 'VNR'] * df_origin.loc['TOTAL', 'TAXA_DEP[%A.A.]']
        df_fluxo.loc[i+1, 'JCP'] = df_origin.loc['TOTAL', 'VMU'] * tma
        df_fluxo.loc[i+1,'JR'] = df_fluxo.loc[i+1, 'QRR'] + df_fluxo.loc[i+1, 'JCP']
       
    return df_all, df_fluxo

#______________________________________________SCRIPT___________________________________

#Importação da base de dados (exemplo)
path = r'C:/Users/est.gustavopietruza/Desktop/Python Scripts/Fluxo de Caixa ABAR/Fluxo_caixa_exemplo.xlsx'
df_abar = pd.read_excel(path)
df_abar = arruma_nome_colunas(df_abar)

#Criação da base de dados ABAR
df_abar = formata_df(df_abar)

#Ajustando a ordem das colunas
colunas = ['ATIVO', 'VNR', 'VIDA ÚTIL [ANOS]', 'TAXA_DEP[R$/ANO]',
       'TAXA_DEP[%A.A.]', 'DEP_ACUM[R$]', 'DEP_ACUM[%]', 'VIDA_UTIL_REM[%]',
       'VIDA_UTIL_REM[ANOS]', 'VMU']
df_abar = df_abar[colunas]

#_____________________________ABAR AJUSTADA______________________________

#Criação dos anos seguintes da base de dados ABAR

#Definição da taxa de juros
tma = 0.1
#Definição do período de tempo
period = 9
p = np.arange(0, period, dtype=int)
#Criação dos fluxos de DataFrames e dos dados para criação do fluxo de caixa
df_all_ajust, df_dados_ajust = fluxo_df_ajust(df_abar, p)

#Criação do fluxo de caixa da ABAR

#Transposição do DataFrame e seleção da coluna JR
df_fluxo_abar_ajust = df_dados_ajust.loc[:,'JR']
df_fluxo_abar_ajust = pd.DataFrame(data = df_fluxo_abar_ajust)
df_fluxo_abar_ajust = df_fluxo_abar_ajust.transpose()

#Formatando
#Adiciona uma coluna extra 
df_fluxo_abar_ajust.columns = df_fluxo_abar_ajust.columns+1

#Insere -MVU na nova coluna do período 0
df_fluxo_abar_ajust.insert(0,0,-(df_abar.loc['TOTAL', 'VMU']))

#Calcula o Valor Presente dos fluxos
df_fluxo_abar_ajust.loc['VP',:] = df_fluxo_abar_ajust.loc['JR', :] / (1+tma)**df_fluxo_abar_ajust.columns

#Calcula o Valor Presente Acumulado dos fluxos
df_fluxo_abar_ajust.loc['VP_ACUM',:] = df_fluxo_abar_ajust.loc['VP',:].cumsum(axis = 0)

#Converte números científicos em 0
for i in df_fluxo_abar_ajust.columns:
    if abs(df_fluxo_abar_ajust.loc['VP_ACUM',i]) < 1*10**(-4):
        df_fluxo_abar_ajust.loc['VP_ACUM',i] = 0

#Calcula os totais de QRR, JCP e JR
df_dados_ajust.loc['TOTAL','QRR'] = df_dados_ajust.loc[:,'QRR'].sum()
df_dados_ajust.loc['TOTAL','JCP'] = df_dados_ajust.loc[1::, 'JCP'].sum()
df_dados_ajust.loc['TOTAL', 'JR'] = df_dados_ajust.loc['TOTAL','QRR'] + df_dados_ajust.loc['TOTAL','JCP']

#Calcula o VPL do fluxo
vpl_ajust = df_fluxo_abar_ajust.loc['VP',:].sum()
if abs(vpl_ajust) < 1*10**(-4):
    vpl_ajust = 0

#____________________________ABAR NÃO AJUSTADA____________________________________

#Criação dos DataFrames, com o mesmo período de antes
df_all, df_dados = fluxo_df_n_ajust(df_abar, p)

#Transposição do DataFrame e seleção da coluna JR
df_fluxo_abar = df_dados.loc[:,'JR']
df_fluxo_abar = pd.DataFrame(data = df_fluxo_abar)
df_fluxo_abar = df_fluxo_abar.transpose()

#Formatando
#Adiciona uma coluna extra 
df_fluxo_abar.columns = df_fluxo_abar.columns+1

#Insere -MVU na nova coluna do período 0
df_fluxo_abar.insert(0,0,-(df_abar.loc['TOTAL', 'VMU']))

#Calcula o Valor Presente dos fluxos
df_fluxo_abar.loc['VP',:] = df_fluxo_abar.loc['JR', :] / (1+tma)**df_fluxo_abar.columns

#Calcula o Valor Presente Acumulado dos fluxos
df_fluxo_abar.loc['VP_ACUM',:] = df_fluxo_abar.loc['VP',:].cumsum(axis = 0)

#Converte números científicos em 0
for i in df_fluxo_abar.columns:
    if abs(df_fluxo_abar.loc['VP_ACUM',i]) < 1*10**(-4):
        df_fluxo_abar.loc['VP_ACUM',i] = 0

#Calcula os totais de QRR, JCP e JR
df_dados.loc['TOTAL','QRR'] = df_dados.loc[:,'QRR'].sum()
df_dados.loc['TOTAL','JCP'] = df_dados.loc[1::, 'JCP'].sum()
df_dados.loc['TOTAL', 'JR'] = df_dados.loc['TOTAL','QRR'] + df_dados.loc['TOTAL','JCP']

#Calcula o VPL do fluxo
vpl = df_fluxo_abar.loc['VP',:].sum()
if abs(vpl) < 1*10**(-4):
    vpl = 0