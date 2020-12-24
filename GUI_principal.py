"""

@author: David García 
"""
import  tkinter as tk
from tkinter import ttk

class programa(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo de Fatiga")
        self.geometry("800x600+10+10")

        #Menu
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Nuevo")
        file_menu.add_command(label="Abrir")
        file_menu.add_separator()
        file_menu.add_command(label="Guardar")
        file_menu.add_command(label="Guardar como...")
        menu.add_cascade(label="Archivo", menu=file_menu)
        menu.add_command(label="Acerca de")
        menu.add_command(label="Salir", command=self.destroy)
        self.config(menu=menu)

        #Pestañas 
        pestanas = ["Material","Datos","Iniciación","Comparación"]
        tabControl = ttk.Notebook(self)
        tabs =[ttk.Frame(tabControl) for _ in pestanas]
        for i,tab in enumerate(pestanas):
            tabControl.add(tabs[i], text =tab)

        tabControl.pack(expand=1,fill= "both")

        #Label Frame de propiedades del material
        props_lf = ttk.Labelframe(tabs[0],text = "Propiedades")
             
        props_lf.grid(column = 0,row =0,padx =20,pady=30)


        
        props = ["C","n","f","l_0","K_th","a_0","K_IC","sigma_y","sigma_f","E","nu","b","G"]

        props_entries = [tk.Entry(props_lf,width = 8,justify = "right") for _ in props]
        props_labels = [ttk.Label(props_lf,text = p) for p in props]
        props_entries[5].config(state=tk.DISABLED)
        props_entries[-1].config(state=tk.DISABLED)
        
        for i,_ in enumerate(props):
            props_entries[i].grid(column = 0, row = i, padx = 5,pady = 5)
            props_labels[i].grid(column = 1, row = i, padx = 8,pady = 5,sticky= tk.W)
        """C = coeficiente de la ley de crecimiento
             n           = exponente de la ley de crecimiento
             f           = parametro en aproximacion al diagrama
             Kitagawa-Takahashi
             l_0         = (m) distancia de la superficie a la primera barrera
             microestructural 
             K_th        = (MPa m^0.5) umbral de creciemiento de la grieta
             a_0         = (m) parametro de El Haddad
             K_IC        = (MPa m^0.5) tenacidad a fractura
             sigma_y     = (MPa) limite elastico
             sigma_f     = (MPa) coeficiente de resistencia a fatiga
             E           = (MPa) modulo de Young
             nu          = coeficiente de Poisson
             b           = exponente de resistencia a fatiga
             G           = (MPa) modulo de cizalladura"""

 



        # #Label Frame del resumen 
        self.resum_lf =ttk.Labelframe(tabs[0],text = "Resumen")
        self.resum_lf.grid(column = 0,row =0,padx =20,pady=30)














if __name__ =="__main__":
    app = programa() 
    app.mainloop()





