# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 12:13:47 2019

@author: Alejandro Quirós
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def grafs_globales(vida_exp, crit):
    """Funcion para generar las graficas de vida estimada frente a vida
    experimental, porcentaje de iniciacion y longitud de iniciacion."""
    
    sin_SP = []
    SP     = []
    plt.figure(0)
    sin_SP += plt.plot([1], [1], 'bo')
    SP     += plt.plot([1], [1], 'ro')
    plt.close(0)
         
    #Cargamos los resultamos de las simulaciones
    vida_est  = {}
    inic      = {}
    long_inic = {}
    
    f = np.loadtxt('resultados.dat', dtype = str, skiprows = 1)
    
    for i in f:
        exp_id = i[0]
        par = i[1]
        if par == crit:
            vida_est[exp_id]  = float(i[2])
            inic[exp_id]      = float(i[5][:-1])
            long_inic[exp_id] = float(i[7])
            
    #Vida estimada frente a vida experimental
    plt.figure(1)
    pts = []
    
    for i in vida_exp:
        try:
            pts += plt.plot(vida_exp[i], [vida_est[i], vida_est[i]], 'bo')
        except KeyError:
            pass
        
    plt.plot([0, 1e10], [0, 1e10], 'k')
    plt.plot([0, 1e10], [0, 5e9], 'k')
    plt.plot([0, 1e10], [0, 2e10], 'k')
    plt.yscale('log')    
    plt.xscale('log')
    plt.ylim([1e3,1e9])
    plt.xlim([1e3,1e9])
    plt.xlabel('Vida experimental')
    plt.ylabel('Vida estimada')
    plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)
#    plt.legend([sin_SP[0], SP[0], pts_SWT[0]], 
#               ['Sin tratamiento', 'Shot peening', 'Electroerosion'], 
#               numpoints = 1, loc = 0)
    plt.show()
    
    #Vida estimada frente a porcentaje de iniciacion
    plt.figure(2)
    
    pts_inic = []
    
    for i in vida_exp:
        try:
            pts_inic += plt.plot(vida_est[i], inic[i], 'bo')
        except KeyError:
            pass
        
    plt.xscale('log')
    plt.ylim([0,102])
    plt.xlim([1e3,1e8])
    plt.xlabel('Vida estimada')
    plt.ylabel('% inic')
    plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)
#    plt.legend([sin_SP[0], SP[0], pts_inic_SWT[0]], 
#               ['Sin tratamiento', 'Shot peening', 'Electroerosion'], 
#               numpoints = 1, loc = 4)
    plt.show()
    
    #Vida estimada frente a longitud de iniciacion
    plt.figure(3)
    
    pts_long = []
    
    for i in vida_exp:
        try:
            pts_long += plt.plot(vida_est[i], long_inic[i], 'bo')
        except KeyError:
            pass
        
    plt.xscale('log')
    plt.yscale('log')
    plt.ylim([0.01,6])
    plt.xlim([1e3,1e8])
    plt.xlabel('Vida estimada')
    plt.ylabel('Longitud inic (mm)')
    plt.grid(which = 'major', color = 'k', linestyle='-', linewidth=0.4)
    plt.grid(which = 'minor', color = 'gray', linestyle=':', linewidth=0.2)    
#    plt.legend([sin_SP[0], SP[0], pts_long_SWT[0]], 
#               ['Sin tratamiento', 'Shot peening', 'Electroerosion'], 
#               numpoints = 1, loc = 0)
    plt.show()

###############################################################################
###############################################################################         

def error(crit, vida_exp1, vida_exp2 = [], vida_exp3 = []):
    """Funcion para obtener el antilogaritmo de la media y la desviacion tipica
    del logaritmo de los cocientes entre vida estimada y vida experimental y 
    la pendiente m de la recta de regresion de las estimaciones."""
    
    #Calculamos el numero de resultados excluyendo los de 6629_971_70
    l1 = (len(vida_exp1)-2)*2

    if type(vida_exp2) is dict:
        l2 = (len(vida_exp2)-2)*2
    else:
        l2 = 0

    if type(vida_exp3) is dict:
        l3 = (len(vida_exp3)-2)*2
    else:
        l3 = 0
        
    #Cargamos los resultados de las simulaciones
    f1 = np.loadtxt('resultados.dat', dtype = str, skiprows = 1)
    
    if vida_exp2 != 0:
        f2 = np.loadtxt('resultados_SP.dat', dtype = str, skiprows = 1)
        
    if vida_exp2 != 0:
        f3 = np.loadtxt('resultados_elec.dat', dtype = str, skiprows = 1)    
        
    vida_est1     = {}
    vida_est1_log = {}   
    vida_est2     = {}
    vida_est2_log = {}
    vida_est3     = {}
    vida_est3_log = {}    

    for i in f1:
        exp_id = i[0]
        par = i[1]
        if par == crit:
            vida_est1[exp_id] = float(i[2])
            vida_est1_log[exp_id] = math.log10(float(i[2]))

    if type(vida_exp2) is dict:
        for i in f2:
            exp_id = i[0]
            par = i[1]
            if par == crit:
                vida_est2[exp_id] = float(i[2])
                vida_est2_log[exp_id] = math.log10(float(i[2]))

    if type(vida_exp3) is dict:
        for i in f3:
            exp_id = i[0]
            par = i[1]
            if par == crit:
                vida_est3[exp_id] = float(i[2])
                vida_est3_log[exp_id] = math.log10(float(i[2]))

    #Calculamos el antilogaritmo de la media y la desviacion tipica del
    #logaritmo del cociente de la vida estimada y la vida experimental
    alpha = 0.0
    sigma = 0.0
    
    #Se descartan los resultados del experimento 6629_971_70
    for i in vida_exp1:
        if i != '6629_971_70':
            alpha += math.log10(vida_est1[i]/vida_exp1[i][0])
            alpha += math.log10(vida_est1[i]/vida_exp1[i][1])

    if type(vida_exp2) is dict:
        for i in vida_exp2:
            if i != '6629_971_70':
                alpha += math.log10(vida_est2[i]/vida_exp2[i][0])
                alpha += math.log10(vida_est2[i]/vida_exp2[i][1])
                
    if type(vida_exp3) is dict:
        for i in vida_exp3:
            if i != '6629_971_70':
                alpha += math.log10(vida_est3[i]/vida_exp3[i][0])
                alpha += math.log10(vida_est3[i]/vida_exp3[i][1])
            
    alpha_m = alpha/(l1 + l2 + l3)
    
    for i in vida_exp1:
        if i != '6629_971_70':
            sigma += (math.log10(vida_est1[i]/vida_exp1[i][0])-alpha_m)**2.0
            sigma += (math.log10(vida_est1[i]/vida_exp1[i][1])-alpha_m)**2.0
   
    if type(vida_exp2) is dict:            
        for i in vida_exp2:
            if i != '6629_971_70':
                sigma += (math.log10(vida_est2[i]/vida_exp2[i][0])-alpha_m)**2.0
                sigma += (math.log10(vida_est2[i]/vida_exp2[i][1])-alpha_m)**2.0

    if type(vida_exp3) is dict:
        for i in vida_exp3:
            if i != '6629_971_70':
                sigma += (math.log10(vida_est3[i]/vida_exp3[i][0])-alpha_m)**2.0
                sigma += (math.log10(vida_est3[i]/vida_exp3[i][1])-alpha_m)**2.0
            
    sigma_alpha = math.sqrt(sigma/(l1 + l2 + l3-1))     
    
    x       = 10**alpha_m
    sigma_x = 10**sigma_alpha
            
    print('{}:\tx = {}'.format(crit, x))
    print('\tsigma_x = {}'.format(sigma_x))
    
    #Calculamos la pendiente de la recta de regresion
    y = []
    x = []
    
    #Se descartan los resultados del experimento 6629_971_70
    for i in vida_exp1:
        if i != '6629_971_70':
            y.append(vida_est1_log[i])
            y.append(vida_est1_log[i])
            
            x.append(math.log10(vida_exp1[i][0]))
            x.append(math.log10(vida_exp1[i][1]))

    if type(vida_exp2) is dict:
        for i in vida_exp2:
            if i != '6629_971_70':
                y.append(vida_est2_log[i])
                y.append(vida_est2_log[i])
                
                x.append(math.log10(vida_exp2[i][0]))
                x.append(math.log10(vida_exp2[i][1]))
    
    if type(vida_exp3) is dict:
        for i in vida_exp3:
            if i != '6629_971_70':
                y.append(vida_est3_log[i])
                y.append(vida_est3_log[i])
                
                x.append(math.log10(vida_exp3[i][0]))
                x.append(math.log10(vida_exp3[i][1]))
            
    y = np.array(y)
    x = np.array(x).reshape((-1, 1))
    
    model = LinearRegression().fit(x, y)
    m = model.coef_[0]

    print('\tm = {}'.format(m))
  
###############################################################################
###############################################################################
    
def grafs_long_grieta(exp, crit):
    """Funcion para obtener las curvas con la evolución de la grieta en 
    funcion del numero de ciclos."""
    
    cwd = os.getcwd()
    ruta_datos = cwd + '/resultados/datos/{}/'.format(crit)
    
    f = np.loadtxt('{}{}.dat'.format(ruta_datos, exp), dtype = float, 
                      skiprows = 1)    
    
    a_i = []
    N_a = []

    for i in f:
        a_i.append(i[0])
        N_a.append(i[4])
        
    plt.figure('Longitud de grieta')
    plt.xscale('log')
    plt.xlabel('Ciclos')
    plt.ylabel('Longitud de grieta (mm)')
    plt.plot(N_a, a_i, 'k')
    plt.xlim([5e2,1e8])
    plt.show()
    
    a_i = []
    N_a = []
  
###############################################################################
###############################################################################

def grafs_vida_est(exp, crit):
    """Funcion para obtener las curvas de vida."""
    
    cwd = os.getcwd()
    ruta_datos = cwd + '/resultados/datos/{}/'.format(crit)
    
    f = np.loadtxt('{}{}.dat'.format(ruta_datos, exp), dtype = float, 
                      skiprows = 1)    
    
    a_i = []
    N_t = []
    N_i = []
    N_p = []

    for i in f:
        a_i.append(i[0])
        N_t.append(i[1])
        N_i.append(i[2])
        N_p.append(i[3])
        
    N_t_min   = min(N_t)
    i_N_t_min = N_t.index(N_t_min)
    a_inic    = a_i[i_N_t_min]
        
    plt.figure(exp + '_' + crit)
    plt.xlabel('Longitud de iniciacion (mm)')
    plt.ylabel('Ciclos')
    plt.yscale('log')
    plt.ylim([1e3,1e8])
    plt.xlim([0.0,a_i[-1]])
    plot_inic  = []
    plot_prop  = []    
    plot_tot   = []
    plot_inic += plt.plot(a_i, N_i, 'b')
    plot_prop += plt.plot(a_i, N_p, 'k')
    plot_tot  += plt.plot(a_i, N_t, 'r') 
    
    #Pintamos el punto donde se da el minimo
    plt.plot(a_inic, N_t_min, 'ro')
    plt.legend([plot_inic[0], plot_prop[0], plot_tot[0]],
               ['Vida de iniciacion', 'Vida de propagacion', 'Vida total'], loc = 0)
    plt.show()

###############################################################################
###############################################################################

if __name__ == "__main__":
    
    vida_exp_sin = {'6629_971_70':[165696, 316603], '5429_971_110':[112165, 126496],
                    '5429_1257_110':[113799, 120663], '4217_1543_110':[88216, 89376],
                    '5429_1543_110':[82559, 87481], '3006_971_150':[59234, 60040],
                    '4217_971_150':[60288, 67776], '5429_971_150':[47737, 51574],
                    '3006_1543_150':[19223, 39408], '4217_1543_150':[50369, 39001],
                    '5429_1543_150':[50268, 39202], '3006_2113_150':[34904, 41002], 
                    '4217_2113_150':[34716, 40004], '5429_2113_150':[32339, 36431],
                    '3006_971_175':[26587, 31815], '4217_971_175':[27724, 32843], 
                    '5429_971_175':[29100, 35171], '3006_1543_175':[30154, 31224], 
                    '4217_1543_175':[34748, 34930], '5429_1543_175':[28005, 33349],
                    '3006_2113_175':[21207, 21669], '4217_2113_175':[26989, 28595],
                    '5429_2113_175':[28112, 28178]}

    vida_exp_SP = {'6629_971_70':[5000000, 5000000], '5429_971_110':[980678, 1811104],
                    '5429_1257_110':[1649736, 1941545], '4217_1543_110':[1110174, 1117513],
                    '5429_1543_110':[810402, 1008310], '3006_971_150':[231459, 665167],
                    '4217_971_150':[634259, 678676], '5429_971_150':[631491, 707514],
                    '3006_1543_150':[275417, 198884], '4217_1543_150':[234651, 497260],
                    '5429_1543_150':[290460, 482862], '3006_2113_150':[140189, 267873], 
                    '4217_2113_150':[166088, 201105], '5429_2113_150':[66564, 190763],
                    '3006_971_175':[364153, 366164], '4217_971_175':[308455, 235467], 
                    '5429_971_175':[338774, 413654], '3006_1543_175':[163474, 164835], 
                    '4217_1543_175':[164384, 169382], '5429_1543_175':[228379, 231132],
                    '3006_2113_175':[68801, 83544], '4217_2113_175':[121642, 127770],
                    '5429_2113_175':[94741, 146553]}

    vida_exp_elec = {'6629_971_70':[148020, 170073], '3006_2113_150':[14239, 24875], 
                     '5429_2113_150':[16783, 19005], '3006_971_175':[19267, 23803], 
                     '5429_971_175':[23591, 25318],'3006_2113_175':[16743, 19173],
                     '5429_2113_175':[16543, 16100]}
    
    crit = 'FS'
    
    grafs_globales(vida_exp_sin, crit)
    error(crit, vida_exp_sin)
    error(crit, vida_exp_sin, vida_exp_SP, vida_exp_elec)   
    
    for exp in vida_exp_sin:    
        grafs_long_grieta(exp, crit)
        grafs_vida_est(exp, crit)
