# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 14:14:01 2018

@author: Alejandro Quirós
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import interp2d
from propagacion import fase_propagacion
from propagacion import constantes_material

def lectura_datos(ruta, exp_max, exp_min):
    """Carga los datos experimentales.
    
    INPUT:   ruta    = ruta para cargar los datos experimentales
             exp_max = nombre del archivo con la tensiones y defs maximas
             exp_min = nombre del archivo con la tensiones y defs minimas
             
    OUTPUTS: x       = (m) vector de distancias a la superficie de la grieta
             sxx_max = (MPa) vector de tensiones máximas en la direccion x
             s_max   = (MPa) vector de tensiones máximas
             e_max   = vector de deformaciones máximas
             e_min   = vector de deformaciones minimas"""
             
    #Cargamos los datos de distancias. Cambiamos el vector para
    #que sea positivo y empiece en 0
    x = np.loadtxt("{}/{}.dat".format(ruta, exp_max), skiprows = 1, 
                   usecols = (1,))*-1e-3
    x = x.tolist()
    
    for i in x:
        x[x.index(i)] = i - 0.1      
        
    #Cargamos el resto de datos
    sxx_max = np.loadtxt("{}/{}.dat".format(ruta, exp_max), skiprows = 1,
                         usecols = (2,)).tolist()
    
    s_max = np.loadtxt("{}/{}.dat".format(ruta, exp_max), skiprows = 1, 
                       usecols = (2, 3, 4, 5, 6, 7)).tolist()
    
    e_max = np.loadtxt("{}/{}.dat".format(ruta, exp_max), skiprows = 1, 
                       usecols = (8, 9, 10, 11, 12, 13)).tolist()
        
    e_min = np.loadtxt("{}/{}.dat".format(ruta, exp_min), skiprows = 1, 
                       usecols = (8, 9, 10, 11, 12, 13)).tolist()
    
    return x, sxx_max, s_max, e_max, e_min

###############################################################################    
###############################################################################

def indice_a(a, x):
    """Devuelve el indice asociado a una longitud de grieta.
    
    INPUT:   a     = longitud de grieta de iniciacion
             x     = vector de distancias a la superficie
             
    OUTPUTS: ind_a = indice asociado a la longitud de grieta de iniciacion"""
    
    #Redondeamos a la 8 cifra para evitar errores numéricos
    a = round(a, 8)
    
    #Calculamos el índice para el cual tenemos esa longitud de grieta
    for i in x:
        i_round = round(i, 8)
        if i_round >= a:
            ind_a = x.index(i)
            break    
    
    return ind_a

###############################################################################    
###############################################################################

def parametro(par, MAT, x, s_max, e_max, e_min):
    """Calcula el vector para el modelo de iniciacion asociado 
    a un experimento.
    
    INPUT:   par    = parametro para el modelo de iniciacion      
             MAT    = indice asignado al material
             x      = (m) vector de distancias a la superficie de la grieta
             s_max  = (MPa) vector de tensiones máximas
             e_max  = vector de deformaciones máximas
             e_min  = vector de deformaciones minimas

    OUTPUTS: FS/SWT = vector con los Fatemi-Socie o Smith-Watson-Topper en cada
             punto"""    
        
    def func_FS(alfa, j):
        """"Devuelve delta_gamma_max/2 en un punto concreto. Se utiliza en el
        calculo del Fatemi-Socie."""
        R_x   = np.array([[1.0, 0.0, 0.0],
                          [0.0, math.cos(alfa[0]), -math.sin(alfa[0])], 
                          [0.0, math.sin(alfa[0]), math.cos(alfa[0])]])
        R_x_T = np.transpose(R_x)
        R_y   = np.array([[math.cos(alfa[1]), 0.0, -math.sin(alfa[1])],
                          [0.0, 1.0, 0.0], 
                          [math.sin(alfa[1]), 0.0, math.cos(alfa[1])]])
        R_y_T = np.transpose(R_y)
        R_z   = np.array([[math.cos(alfa[2]), -math.sin(alfa[2]), 0.0], 
                          [math.sin(alfa[2]), math.cos(alfa[2]), 0.0],
                          [0.0, 0.0, 1.0]])
        R_z_T = np.transpose(R_z)
        
        E_xyz_max = np.array([[e_max[j][0], e_max[j][3], e_max[j][4]],
                              [e_max[j][3], e_max[j][1], e_max[j][5]],
                              [e_max[j][4], e_max[j][5], e_max[j][2]]])

        E_xyz_min = np.array([[e_min[j][0], e_min[j][3], e_min[j][4]],
                              [e_min[j][3], e_min[j][1], e_min[j][5]],
                              [e_min[j][4], e_min[j][5], e_min[j][2]]])
        
        E_max = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T, np.dot(R_z_T,
                       E_xyz_max))), R_z), R_y), R_x).tolist()
        E_min = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T, np.dot(R_z_T,
                       E_xyz_min))), R_z), R_y), R_x).tolist()
        
        #El signo negativo se debe a que la función minimiza en vez de
        #maximizar.
        return -(E_max[0][1] - E_min[0][1])
        
    def func_SWT(alfa, j):
        """"Devuelve el Smith-Watson-Topper asociado a un punto."""
        R_x   = np.array([[1.0, 0.0, 0.0],
                          [0.0, math.cos(alfa[0]), -math.sin(alfa[0])], 
                          [0.0, math.sin(alfa[0]), math.cos(alfa[0])]])
        R_x_T = np.transpose(R_x)
        R_y   = np.array([[math.cos(alfa[1]), 0.0, -math.sin(alfa[1])],
                          [0.0, 1.0, 0.0], 
                          [math.sin(alfa[1]), 0.0, math.cos(alfa[1])]])
        R_y_T = np.transpose(R_y)
        R_z   = np.array([[math.cos(alfa[2]), -math.sin(alfa[2]), 0.0], 
                          [math.sin(alfa[2]), math.cos(alfa[2]), 0.0],
                          [0.0, 0.0, 1.0]])
        R_z_T = np.transpose(R_z)
        
        E_xyz_max = np.array([[e_max[j][0], e_max[j][3], e_max[j][4]],
                              [e_max[j][3], e_max[j][1], e_max[j][5]],
                              [e_max[j][4], e_max[j][5], e_max[j][2]]])

        E_xyz_min = np.array([[e_min[j][0], e_min[j][3], e_min[j][4]],
                              [e_min[j][3], e_min[j][1], e_min[j][5]],
                              [e_min[j][4], e_min[j][5], e_min[j][2]]])
        
        S_xyz_max = np.array([[s_max[j][0], s_max[j][3], s_max[j][4]],
                              [s_max[j][3], s_max[j][1], s_max[j][5]],
                              [s_max[j][4], s_max[j][5], s_max[j][2]]])
        
        E_max = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T, np.dot(R_z_T,
                       E_xyz_max))), R_z), R_y), R_x).tolist()
        E_min = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T, np.dot(R_z_T,
                       E_xyz_min))), R_z), R_y), R_x).tolist()
        S_max = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T, np.dot(R_z_T,
                       S_xyz_max))), R_z), R_y), R_x).tolist()

        #El signo negativo se debe a que la función minimiza en vez de
        #maximizar.
        return -(S_max[0][0]*(E_max[0][0]-E_min[0][0])/2.0)
    
    #Inicializamos variables
    alfa0 = [0.0, 0.0, 0.0] #Ángulo para primera iteracion de la funcion de
                           #minimizacion
    #Limites para el angulo
    bnds = ((-math.pi, math.pi), (-math.pi, math.pi), (-math.pi, math.pi))
    
    sigma_y = constantes_material(MAT)[7]
    sigma_f = constantes_material(MAT)[8]
    k       = sigma_y/sigma_f
    
    alfa            = []
    delta_gamma_max = []
    s_norm          = []
    FS              = []
    SWT             = []
    
    #Calculamos en cada punto el Fatemi-Socie o el Smith-Watson-Topper asociado
    for j in range(len(x)):
        if par == 'FS':
            fs = minimize(func_FS, alfa0, bounds = bnds, args=(j),
                            options={'disp': False})
            alfa.append(fs.x.tolist())
            delta_gamma_max.append(-func_FS(alfa[j], j)*2.0)
            
            R_x   = np.array([[1.0, 0.0, 0.0],
                              [0.0, math.cos(alfa[j][0]), -math.sin(alfa[j][0])], 
                              [0.0, math.sin(alfa[j][0]), math.cos(alfa[j][0])]])
            R_x_T = np.transpose(R_x)
            R_y   = np.array([[math.cos(alfa[j][1]), 0.0, -math.sin(alfa[j][1])],
                              [0.0, 1.0, 0.0], 
                              [math.sin(alfa[j][1]), 0.0, math.cos(alfa[j][1])]])
            R_y_T = np.transpose(R_y)
            R_z   = np.array([[math.cos(alfa[j][2]), -math.sin(alfa[j][2]), 0.0], 
                              [math.sin(alfa[j][2]), math.cos(alfa[j][2]), 0.0],
                              [0.0, 0.0, 1.0]])
            R_z_T = np.transpose(R_z)
            
            S_xyz_max = np.array([[s_max[j][0], s_max[j][3], s_max[j][4]],
                                  [s_max[j][3], s_max[j][1], s_max[j][5]],
                                  [s_max[j][4], s_max[j][5], s_max[j][2]]])
            
            S_max = np.dot(np.dot(np.dot(np.dot(R_x_T, np.dot(R_y_T,
                           np.dot(R_z_T, S_xyz_max))), R_z), R_y), R_x).tolist()
            s_norm.append(S_max[2][2])
            
            FS.append(delta_gamma_max[j]/2.0*(1.0 + k*s_norm[j]/sigma_y))
            
        elif par == 'SWT':
            swt  = minimize(func_SWT, alfa0, bounds = bnds,  args=(j),
                            options={'disp': False})
            alfa.append(swt.x.tolist())
            SWT.append(-func_SWT(alfa[j], j))
        
    if par == 'FS':
        return FS
        
    elif par == 'SWT':           
        return SWT

###############################################################################
###############################################################################

def principal(par, W, MAT, exp_max, exp_min):
    """Estima la vida a fatiga.
    
    INPUTS:  par     = parametro para el modelo de iniciacion
             W       = (m) anchura del especimen        
             MAT     = indice asignado al material
             exp_max = nombre del archivo con la tensiones y defs maximas
             exp_min = nombre del archivo con la tensiones y defs minimas
            
    OUTPUTS: resultados.dat = actualiza el archivo de resultados con la
             longitud de iniciacion y los ciclos de iniciacion, propagacion y 
             total para que se produzca el fallo
             exp_id.dat     = archivo con los datos de las curvas de vida"""
             
    print('Datos Experimentales:\n    {}.dat\n    {}.dat\n'.format(exp_max,
                                                                   exp_min))
    #exp_id obtiene a partir del nombre del archivo con los datos un
    #identificador del experimento. Dependiendo del nombre del archivo debe
    #modificarse.
    exp_id      = exp_max[16:]

    #Obtenemos las rutas a las carpetas necesarias para los calculos 
    cwd         = os.getcwd()
    ruta_exp    = cwd + '/datos_exp'
    ruta_curvas = cwd + '/curvas_inic'
    ruta_fig    = cwd + '/resultados/grafs/' + par
    ruta_datos  = cwd + '/resultados/datos/' + par
             
    #Cargamos los datos de las curvas de iniciación del material
    data_interp = np.loadtxt("{}/MAT{}_{}.dat".format(ruta_curvas, MAT, par))  
    
    #Separamos las curvas en las variables necesarias
    x_interp = data_interp[0][1:] #Eje x de la matriz de interpolación 
    y_interp = []          #Eje y de la matriz de interpolación
    m_N_i    = []          #Matriz con los ciclos de iniciación

    for i in data_interp[1:]:
        y_interp.append(i[0])
        m_N_i.append(i[1:])
    
    y_interp = np.array(y_interp)
    
    #Creamos la función de interpolación
    function_interp = interp2d(x_interp, y_interp, m_N_i, kind='quintic', 
                               bounds_error=False)
                       
    #Cargamos los datos experimentales y generamos el vector de FS o SWT
    x, sxx_max, s_max, e_max, e_min = lectura_datos(ruta_exp, exp_max,
                                                             exp_min)
    param = parametro(par, MAT, x, s_max, e_max, e_min)
    
    #Iniciamos variables
    v_ai    = []           #Vector de longitudes de grieta en m
    v_ai_mm = []           #Vector de longitudes de grieta en mm
    N_i     = []           #Vector de ciclos de iniciación 
    N_p     = []           #Vector de ciclos de propagación
    N_t     = []           #Vector de ciclos totales
    
    a_i_min = round(x[1], 8) #Tamaño mínimo de longitud de grieta de
                             #iniciacion. Redondeamos para evitar errores
                             #numericos.
    a_i_max = round(x[-2], 8) #Tamaño máximo de longitud de grieta de iniciacion
    da      = a_i_min      #Paso entre longitudes de grietas
    N       = int((a_i_max - a_i_min)/da)+1 #Número de grietas a calcular
    
    #Creamos el vector de longitudes de grieta de iniciacion
    a_i     = a_i_min

    for i in range(N):
        v_ai.append(a_i + i*da)
    
    #Calculamos los ciclos de iniciación, de propagación y totales para cada
    #longitud de grieta de iniciacion   
    for i in v_ai:
        ind_a     = indice_a(i, x) #Indice asociado a esa longitud de grieta
        param_med = np.mean(param[:ind_a + 1]) #Valor medio del parametro para
                           #realizar la interpolacion
        #Realizamos la interpolacion para calcular los ciclos de iniciacion
        n_i = function_interp(i, param_med)[0] 

        #La interpolacion puede dar valores menores que 0 para ciclos muy bajos
        if n_i < 0:
            n_i = 0
        
        #Calculamos los ciclos de propagacion
        n_p = fase_propagacion(sxx_max, ind_a, i, da, W, MAT) 
        
        #Se añaden los datos calculados a las curvas
        N_i.append(n_i)
        N_p.append(n_p)
        N_t.append(n_i+n_p)
        v_ai_mm.append(i*1e3)
    
    #Pintamos los curvas de iniciación, de propagación y totales
    plt.close(exp_id + '_' + par)
    plt.figure(exp_id + '_' + par)
    plt.yscale('log')
    plt.xlabel('Longitud de iniciacion (mm)')
    plt.ylabel('Ciclos')
    plot_inic  = []
    plot_prop  = []    
    plot_tot   = []
    plot_inic += plt.plot(v_ai_mm, N_i, 'b')
    plot_prop += plt.plot(v_ai_mm, N_p, 'k')
    plot_tot  += plt.plot(v_ai_mm, N_t, 'r')
    
    #Calculamos el numero de ciclos hasta el fallo y la longitud de iniciación
    #de la grieta, que se producen en el mínimo de la curva de ciclos totales
    N_t_min   = min(N_t)
    i_N_t_min = N_t.index(N_t_min)
    N_i_min   = N_i[i_N_t_min]
    N_p_min   = N_p[i_N_t_min]
    a_inic    = v_ai_mm[i_N_t_min]

    #Pintamos el punto donde se da el minimo
    plt.plot(a_inic, N_t_min, 'ro')
    plt.ylim([1e3,1e8])
    plt.xlim([0.0,a_i_max*1e3])
    plt.legend([plot_inic[0], plot_prop[0], plot_tot[0]],
               ['Vida de iniciacion', 'Vida de propagacion', 'Vida total'],
               loc = 0)
    plt.show()
    
    #Guardamos la figura y la cerramos
    plt.savefig(ruta_fig + '/{}.png'.format(exp_id))
    plt.close(exp_id + '_' + par)
    
    #Pintamos la figura con la evolucion de la longitud de grieta y guardamos
    #en un archivo los datos
    ciclos = open(ruta_datos + '/{}.dat'.format(exp_id), 'w')
    ciclos.write('{:<5}\t{:<12}\t{:<12}\t{:<12}\t{:<12}'.format('a_i', 'N_t', 
                                                                'N_i', 'N_p', 
                                                                'N_a'))
    
    N_a = []               #Vector de ciclos con la evolución de la grieta

    for i in v_ai:
        #Hasta la longitud de iniciacion crece como los ciclos de iniciacion
        if i <= a_inic*1e-3:
            n_a = N_i[v_ai.index(i)]
            N_a.append(n_a)
        #A partir de la longitud de iniciacion crece de acuerdo con los ciclos
        #de propagacion
        else:
            n_a = N_a[-1] + N_p[v_ai.index(i)-1] - N_p[v_ai.index(i)]
            N_a.append(n_a)
        n_i = N_i[v_ai.index(i)]
        n_p = N_p[v_ai.index(i)]
        
        ciclos.write('\n{:.3f}\t{:.6e}\t{:.6e}\t{:.6e}\t{:.6e}'.format(i*1e3,
                     n_i+n_p, n_i, n_p, n_a))            
    ciclos.close()
            
    plt.figure('Longitud de grieta')
    plt.xscale('log')
    plt.xlabel('Ciclos')
    plt.ylabel('Longitud de grieta (mm)')
    plt.plot(N_a, v_ai_mm, 'k')
    plt.xlim([5e2,1e8])
    plt.show()
    
    #Generamos/actualizamos el archivo con los resultados para la estimacion
    lines = np.loadtxt('resultados.dat', dtype = str, skiprows = 1).tolist()
    
    results = open('resultados.dat', 'w')
    results.write('{:<13}\t{:<}\t{:<12}\t{:<12}\t{:<12}\t{:<5}\t{:<5}\t{:<}'.format('exp_id', 
                  'param', 'N_t_min', 'N_i_min', 'N_p_min', '% N_i', '% N_p', 'a_inic (mm)'))
    
    #Se reescriben las lineas que ya estaban en el archivo. EL if else es debido
    #a que el formato de lines varía según haya una línea de resultados escrita 
    #o mas de una.
    if len(lines[0][0]) == 1:
        #Solo se escriben los resultados que no pertenezcan al calculo actual
        if lines[0] != exp_id or lines[1] != par:
            results.write('\n')
            for j in i:
                results.write('{}\t'.format(j))
    else:
        for i in lines:
            #Solo se escriben los resultados que no pertenezcan al calculo actual
            if i[0] != exp_id or i[1] != par:
                results.write('\n')
                for j in i:
                    results.write('{}\t'.format(j))
                    
    #Se escribe en el archivo el calculo actual
    results.write('\n{}\t{}\t{:.6e}\t{:.6e}\t{:.6e}\t{:.1%}\t{:.1%}\t{:.3f}'.format(exp_id, par, 
                  N_t_min, N_i_min, N_p_min, float(N_i_min)/N_t_min, 
                  float(N_p_min)/N_t_min, a_inic))
    results.close()
      
    print('Longitud de iniciación de la grieta: {} mm'.format(a_inic))
    print('Numero de ciclos hasta el fallo: {}\n'.format(N_t_min))
    
###############################################################################
###############################################################################

if __name__ == "__main__":

    par  = 'SWT'
    W     = 10e-3
    MAT   = 0
    tracc = 'TENSOR_TRACCION_'
    comp  = 'TENSOR_COMPRESION_'
    exp   = ['6629_971_70', '5429_971_110',
             '5429_1257_110', '4217_1543_110',
             '5429_1543_110', '3006_971_150',
             '4217_971_150', '5429_971_150',
             '3006_1543_150', '4217_1543_150',
             '5429_1543_150', '3006_2113_150', 
             '4217_2113_150', '5429_2113_150',
             '3006_971_175', '4217_971_175', 
             '5429_971_175', '3006_1543_175', 
             '4217_1543_175', '5429_1543_175',
             '3006_2113_175', '4217_2113_175', '5429_2113_175']
             
    exp =['4217_2113_175']
             
    for i in exp:
        exp_max = tracc + i
        exp_min = comp + i
        principal(par, W, MAT, exp_max, exp_min)
