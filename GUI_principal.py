"""

@author: David García 
"""
import  tkinter as tk
from tkinter import ttk
import numpy as np
from iniciacion_b import curvas_iniciacion
from propagacion_b import MAT
class programa(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo de Fatiga")
        self.geometry("800x600+10+10")

        #variables 
        self.props = ["C","n","f","l_0","K_th","sigma_fl","a_0","K_IC","sigma_y","sigma_f","E","nu","b","G"]
        self.dict_prop = {}
        self.mat_values ={}
        for prop in self.props:
            self.mat_values[prop] = tk.StringVar()
        


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
        # props_lf.place(width=180,height=500)
        self.props_entries = {}
        for prop in self.props:
            self.props_entries[prop] = tk.Entry(props_lf,textvariable = self.mat_values[prop],width = 12,justify = "right") 
        props_labels = [ttk.Label(props_lf,text = p) for p in self.props]
        self.props_entries["G"].config(state=tk.DISABLED)
        self.props_entries["a_0"].config(state=tk.DISABLED)

        
        for i,prop in enumerate(self.props):
            self.props_entries[prop].grid(column = 1, row = i, padx = 5,pady = 5)
            props_labels[i].grid(column = 0, row = i, padx = 8,pady = 5,sticky= tk.E)
        
        
        #Botones de las propiedades
        boton_borrar = ttk.Button(props_lf,text="Borrar",command = self.borrar_campos)
        boton_borrar.grid(column = 0,row =len(self.props),padx =5, pady =8)
        boton_guardar= ttk.Button(props_lf,text="Guardar",command = self.guardar_campos)
        boton_guardar.grid(column = 1,row =len(self.props),padx =5, pady =8)
        
        #combobox
        self.comb_val = ["Acero"]
        self.combo = ttk.Combobox(props_lf,value =self.comb_val)
        self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>",self.combosel) 
        self.combo.grid(column = 0, row = len(self.props)+1,padx = 5, pady = 8)
        
        #boton pruebav
        self.probar_btn = ttk.Button(tabs[0],text = "probar",command=lambda: curvas_iniciacion(par = 'FS', da=1e-5, W = 10e-3, MAT=self.dict_prop))
        self.probar_btn.grid(column = 0, row = 1, columnspan= 2,padx =10,pady = 5)
        
        #Label Frame del resumen 
        self.resum_lf =ttk.Labelframe(tabs[0],text = "Resumen")
        self.resum_lf.grid(column = 0,row =0,padx =20,pady=30)

    def combosel(self,event):
        for prop in self.props:
            if prop != "G" or prop !="a_0":
                self.props_entries[prop].delete(0,tk.END)
                self.props_entries[prop].insert(0,MAT[prop])   
    
    def borrar_campos(self):
        for prop in self.props:
            self.props_entries[prop].delete(0,tk.END)
        
        self.props_entries["G"].config(state=tk.DISABLED)
        self.props_entries["a_0"].config(state=tk.DISABLED)
        self.dict_prop = {}
        

    def guardar_campos(self):
        for prop in self.props:
            try:
                self.dict_prop[prop] = float(self.mat_values[prop].get())
            except ValueError:
                self.props_entries[prop].delete( 0,tk.END)

        self.props_entries["G"].config(state=tk.NORMAL)
        self.props_entries["a_0"].config(state=tk.NORMAL)

        self.dict_prop["G"]=self.dict_prop["E"]/(2.0*(1.0 + self.dict_prop["nu"]))
        self.mat_values["G"].set(self.dict_prop["G"])
        self.props_entries["G"].insert(0,self.mat_values["G"].get())

        self.dict_prop["a_0"]=1/np.pi*(self.dict_prop["K_th"]/(self.dict_prop["sigma_fl"]))**2.0
        self.mat_values["a_0"].set(self.dict_prop["a_0"])
        self.props_entries["a_0"].insert(0,self.mat_values["a_0"].get())
        if len(self.dict_prop)==len(self.props):
            for prop in self.props:
                self.props_entries[prop].config(fg= "green")
        

        print(self.dict_prop)












if __name__ =="__main__":
    app = programa() 
    app.mainloop()





