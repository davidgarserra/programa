# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 14:11:21 2018

@author: Alejandro Quirós
"""

import os
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from propagacion import fase_propagacion
from propagacion import constantes_material

def ciclos_totales(param, crit, MAT):
    """Devuelve los ciclos totales en funcion del criterio usado, utilizando 
    un fsolve().
    
    INPUTS: param = Fatemi-Socie o Smith-Watson-Topper en un punto 
            crit  = parametro a utilizar
            MAT   = indice asignado al material
            
    OUTPUT: N_t   = ciclos totales"""
    
    #Constantes del material necesarias 
    sigma_y = constantes_material(MAT)[7]
    sigma_f = constantes_material(MAT)[8]
    k       = sigma_y/sigma_f
    E       = constantes_material(MAT)[9]
    nu      = constantes_material(MAT)[10]
    b       = constantes_material(MAT)[11]

    def fsolve_FS(x):
        """Funcion que utiliza el fsolve para calcular los ciclos de vida
        cuando se utiliza el Fatemi-Socie."""
        expr = param - ((1+nu)*sigma_f/E*(2.0*x)**b + k/2.0*(1.0 
                     + nu)*sigma_f**2.0/(E*sigma_y)*(2.0*x)**(2.0*b))
        
        return expr
        
    def fsolve_SWT(x):
        """Funcion que utiliza el fsolve para calcular los ciclos de vida
        cuando se utiliza el Smith-Watson-Topper."""        
        expr = param - (sigma_f**2.0/E*(2*x)**(2.0*b))
        
        return expr
        
    if crit == 'FS':        
        N_t = fsolve(func=fsolve_FS, x0=10, xtol=1e-10)[0]
    
    elif crit == 'SWT':
        N_t = fsolve(func=fsolve_SWT, x0=100, xtol=1e-10)[0]
    
    return N_t
    
###############################################################################
###############################################################################

def fase_iniciacion(param, sigma, crit, a_i, da, W, MAT):
    """Devuelve los ciclos de la fase de iniciacion de una grieta, conocida
    la tension media desde la superficie hasta la punta de la misma.
    
    INPUTS: param = Fatemi-Socie o Smith-Watson-Topper en un punto 
            sigma = tension x en ese punto
            crit  = parametro a utilizar
            a_i   = (m) tamaño de la grieta de iniciacion
            da    = paso para realizar los calculos 
            W     = (m) anchura del especimen
            MAT   = indice asignado del material
                  
    OUTPUT: N_i   = ciclos de la fase de iniciacion"""
    
    #Calcula los ciclos totales hasta el fallo
    N_t = ciclos_totales(param, crit, MAT)
    
    #ind_a se utiliza para la propia fase de propagacion por lo 
    #que en la fase de iniciacion no es una variable relevante y puede tomar 
    #cualquier valor
    ind_a = 0
    
    #Calculos los ciclos que necesita la grieta para propagarse
    N_p = fase_propagacion(sigma, ind_a, a_i, da, W, MAT)
    
    #Calculamos los ciclos de iniciacion
    N_i = N_t - N_p
    
    #Si el numero es negativo devuelve 0
    if N_i < 0:
        N_i = 0.0
        
    #Para ciclos muy altos solo se tiene en cuenta la iniciación para evitar 
    #errores que se producen en la integración de la propagación
    if N_t > 1.5e7:
        N_i = N_t
    
    return N_i
    
###############################################################################
############################################################################### 
    
def curvas_iniciacion(par, da, W, MAT):
    """Escribe un archivo de texto con las curvas de
    iniciación para distintas longitudes de grieta para un material.
    
    INPUT:   par   = parametro para el modelo de iniciacion
             da    = paso para realizar los calculos 
             W     = (m) anchura del especimen
             MAT   = indice asignado al material
        
    OUTPUTS: MATX_par.dat = archivo con las curvas de iniciacion
             figura.png   = imagen con las curvas de iniciacion"""
             
    print(('Curvas de iniciacion del material {} '
           +'utilizando el parametro {}\n').format(MAT, par))
    
    #Abrimos el archivo donde se van a escribir los datos,
    #escribimos la cabecera del mismo y creamos los vectores con las tensiones
    #y los tamaños de grieta para crear las curvas de iniciación
    cwd      = os.getcwd()
    ruta     = cwd + '/curvas_inic'
    ruta_fig = cwd + '/grafs'
    if(os.path.isdir(ruta_fig)):
        pass
    else:
        os.mkdir(ruta_fig)

    archivo  = open('{}/MAT{}_{}.dat'.format(ruta, MAT, par), 'w')
        
    archivo.write('0      ')
    
    v_sigma     = []       #Vector de tensiones
    v_param     = []       #Vector de Fatemi-Socie o Smith-Watson-Topper
    n_sigma     = 45          #Discretizaciones de la curva de iniciacion
    
    sigma_max   = 500.0    #(MPa) tension maxima
    sigma_min   = 50.0     #(MPa) tension minima
        
    delta_sigma = (sigma_max - sigma_min)/n_sigma #Paso de tensiones

    #Cargamos propiedades del material
    sigma_y = constantes_material(MAT)[7]
    sigma_f = constantes_material(MAT)[8]
    k       = sigma_y/sigma_f
    E       = constantes_material(MAT)[9]
    G       = constantes_material(MAT)[12]

    #Generamos el vector de Fatemi-Socie o Smith-Watson-Topper
    for i in range(n_sigma+1):
        sigma_i = sigma_min+i*delta_sigma
        def_i   = sigma_i/E
        gamma_i = sigma_i/2.0/G
        v_sigma.append(sigma_i)
        if par == 'FS':
            v_param.append(gamma_i*(1.0+k*sigma_i/2.0/sigma_y))
        elif par == 'SWT':
            v_param.append(sigma_i*def_i)        
    
    m_N_i = [[], []]       #Matriz para guardar ciclos y tensiones para
                           #facilitar la generacion de las graficas 
    v_a   = []             #Vector de tamaños de grietas
    n_a   = 10          #Número de curvas de iniciacion por material
    a_min = 5e-5           #Tamaño más pequeño grieta
    ex    = 1.45		   #Variable para controlar como crece la diferencia
    					   #entre longitudes de grieta
    
    for i in range(n_a):
        v_a.append(a_min*(i+1.0)**ex)
        archivo.write('{:.2e}  '.format(v_a[-1]))
        
    #Creamos las curvas de iniciación en el archivo
    for i in range(len(v_param)):
        archivo.write('\n{:+.2e}'.format(v_param[i]))
            
        for j in v_a:
            N_i   = fase_iniciacion(v_param[i], v_sigma[i], par, j, da, W, MAT)
            m_N_i[0].append(N_i)
            m_N_i[1].append(v_sigma[i])
 
            archivo.write(' {:+.6e}'.format(N_i))
            
        #Pintamos en la consola el porcentaje realizado
        print('\r{:.2%} completado'.format((i+1.0)/len(v_param)), end = '')
    
    #Cerramos el archivo
    archivo.close()
    
    v_N_i = []
    v_sigma2 = []

    #Utilizando la matriz auxiliar m_N_i, creamos los vectores de ciclos de
    #iniciacion y tensiones en el formato adecuado para dibujar las curvas.
    for i in range(n_a):
        v_N_i.append([])
        v_sigma2.append([])
    
    for i in range(n_sigma):
        for j in range(n_a):
            v_N_i[j].append(m_N_i[0][j+i*n_a])
            v_sigma2[j].append(m_N_i[1][j+i*n_a])       
    
    #Pintamos las curvas de iniciación
 
    plt.figure(figsize=(6,5),dpi=100)
    
    for i in range(n_a):
        plt.plot(v_N_i[i], v_sigma2[i])
    
    plt.xlabel('Ciclos de iniciacion')
    plt.xscale('log')
    plt.grid()
    plt.show()
    
    #Guardamos la figura y la cerramos
    plt.savefig(ruta_fig + f'/curvas_inic_{par}.png')
   
    
###############################################################################
###############################################################################    

if __name__ == "__main__":
    
    curvas_iniciacion(par = 'FS', da=1e-5, W = 10e-3, MAT = 0)
        
