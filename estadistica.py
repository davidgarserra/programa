import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression

def regresion(par,vida_estimada, vida_experimental):
    """Cálculo de la recta de regresion entre la vida estimada y la vida experimental
    INPUTS:
        par: parámetro de los cálculos (SWT o FS)   

        vida_estimada: ubicación del archivo.dat con los resultados de todos los experimentos

        vida_experimental: ubicacion del archivo.xlsx con los datos de todos los experimentos de
    
    OUTPUTS:
        figura: Gráfica con la representación de los puntos, la recta de regresion y los
        datos de los coeficientes.

    """
    data_exp = pd.read_excel(vida_experimental,index_col=0) #datos de vida experimental

    data_est =pd.read_table(vida_estimada,sep=r"\s+",skiprows =1, names =["exp_id", "param","N_t_min","N_i_min", "N_p_min","%N_i","%N_p","a_inic" ])
    data_est =data_est[data_est.param==par] #Filtramos solo para ese parámetro 

    dict_est = {} #Diccionario con las datos estimados


    for j,exp in enumerate(data_est.exp_id): #Rellenamos los diccionarios con el valor N_t_min
        if exp !='6629_971_70':
            dict_est[exp]=data_est.iloc[j].N_t_min

    exps = data_exp.columns.values[1:] #vector de columnas de data_exp menos el primer elemento que es el 6629_971_70

    Df_est_exp = pd.DataFrame() #Dataframe con todos los datos
    Df_est_exp["exp_id"]=exps
    Df_est_exp["vida_estimada"]=[dict_est[i] for i in exps]
    Df_est_exp["vida_experimental1"]=[data_exp[i].values[0] for i in exps]
    Df_est_exp["vida_experimental2"]=[data_exp[i].values[1] for i in exps]
    Df_est_exp["vida_est_log"] =np.log10(Df_est_exp.vida_estimada)
    Df_est_exp["vida_exp_log1"] =np.log10(Df_est_exp.vida_experimental1)
    Df_est_exp["vida_exp_log2"] =np.log10(Df_est_exp.vida_experimental2)
    
    
    
    #Hacemos la regresion con los logaritmos 
    x =np.concatenate((Df_est_exp.vida_est_log.values,Df_est_exp.vida_est_log.values))
    y =np.concatenate((Df_est_exp.vida_exp_log1.values,Df_est_exp.vida_exp_log2.values))


    Lm= LinearRegression(fit_intercept=False)
    try:
        Lm.fit(x.reshape(-1,1),y.reshape(-1,1))
    except:
        Lm.fit(x.reshape(-1,1),y.reshape(-1,1))

    a= Lm.coef_[0] #coeficiente de la regresion forzados en el origen
    r =Lm.score(x.reshape(-1,1),y.reshape(-1,1)) # Coeficiente de correlación
    xs = np.array([0,15])
    ys = a*xs

    # plt.figure(figsize =(5,5))
    plt.plot(x,y,"ok")
    plt.xlim([np.min(x)*0.95,np.max(x)*1.05])
    plt.ylim([np.min(x)*0.95,np.max(x)*1.05])
    plt.xlabel('Log(Vida estimada)')
    plt.ylabel('Log(Vida experimental)')
    plt.annotate("$a= {:.3f}$\n$r^2= {:.3f}$".format(a[0],r),xy =(np.min(x),np.max(x)),xytext =(np.min(x),np.max(x)))
    plt.plot([0,15],[0,15],'--r')
    plt.plot(xs,ys,"-g")
    plt.grid()
    # plt.show()

    #Figura con los datos sin aplicar logaritmo decimal

    # x_sin =np.concatenate((Df_est_exp.vida_estimada.values,Df_est_exp.vida_estimada.values))
    # y_sin =np.concatenate((Df_est_exp.vida_experimental1.values,Df_est_exp.vida_experimental2.values))

    # plt.figure(figsize=(5,5))
    # plt.plot(x_sin,y_sin,'ok')
    # plt.xscale("log")
    # plt.yscale("log")
    # plt.plot([0, 1e10], [0, 1e10], '--r')
    # plt.yscale('log')    
    # plt.xscale('log')
    # plt.ylim([np.min(x_sin)/2,np.max(x_sin)*2])
    # plt.xlim([np.min(x_sin)/2,np.max(x_sin)*2])
    # plt.xlabel('Vida estimada')
    # plt.ylabel('Vida experimental')
    # plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    # plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)
    # plt.show()
    
    
def grafica_lon_vida(par,vida_estimada):
    data_est =pd.read_table(vida_estimada,sep=r"\s+",skiprows =1, names =["exp_id", "param","N_t_min","N_i_min", "N_p_min","%N_i","%N_p","a_inic" ])
    data_est=data_est[data_est.exp_id !="6629_971_70"]
    data_est = data_est[data_est.param == par]

    x = data_est.N_i_min.values
    y = data_est.a_inic.values

    fig = plt.figure(figsize=(5,3))

    plt.plot(x,y,'ok')
    plt.xscale('log')
    plt.ylim([0,1])
    plt.xlim([1e2,1e5])
    plt.xlabel('Vida estimada')
    plt.ylabel('a_inic(mm)')
    plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)

    return fig


def grafica_per_vida(par,vida_estimada):
    data_est =pd.read_table(vida_estimada,sep=r"\s+",skiprows =1, names =["exp_id", "param","N_t_min","N_i_min", "N_p_min","%N_i","%N_p","a_inic" ])
    data_est=data_est[data_est.exp_id !="6629_971_70"]
    data_est = data_est[data_est.param == par]

    x = data_est.N_i_min.values
    y = data_est["%N_i"].values
    y =np.array([float(i[:-1]) for i in y])

    fig = plt.figure(figsize=(5,3))

    plt.plot(x,y,'ok')
    plt.xscale('log')
    plt.ylim([0,100])
    plt.xlim([1e2,1e5])
    plt.xlabel('Vida estimada')
    plt.ylabel('Porcentaje de iniciación %')
    plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)

    return fig

