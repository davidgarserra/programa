"""

@author: David García Serrano
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
        self.geometry("1000x600+10+10")
        

        #variables 
        self.props = ["C","n","f","l_0","K_th","sigma_fl","a_0","K_IC","sigma_y","sigma_f","E","nu","b","G"]
        self.units = ["","","","m","MPa m^0.5","MPa","m","MPa m^0.5","MPa","MPa","MPa","","","MPa"]
        self.dict_prop = {}
        self.mat_values ={}
        self.dict_units = dict(zip(self.props,self.units))
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
        menu.add_command(label="Acerca de",command =self.mostrar_info)
        menu.add_command(label="Salir", command=self.destroy)
        self.config(menu=menu)

        #Pestañas 
        self.pestanas = ["Material","Iniciación","Datos","Comparación"]
        self.tabControl = ttk.Notebook(self)
        self.tabs ={}
        for pestana in self.pestanas:
            self.tabs[pestana] = ttk.Frame(self.tabControl)
        
            self.tabControl.add(self.tabs[pestana], text =pestana)

        self.tabControl.pack(expand=1,fill= "both")

        #Label Frame de propiedades del material
        props_lf = ttk.Labelframe(self.tabs["Material"],text = "Propiedades") 
        props_lf.grid(column = 0,row =0,padx =20,pady=30)

        # props_lf.place(width=180,height=500)
        self.props_entries = {}
        for prop in self.props:
            self.props_entries[prop] = tk.Entry(props_lf,textvariable = self.mat_values[prop],width = 20,justify = "right",font =("Arial",10)) 
        props_labels = [ttk.Label(props_lf,text = f"{p}({self.dict_units[p]})",font =("Arial",10)) for p in self.props]
        self.props_entries["G"].config(state=tk.DISABLED)
        self.props_entries["a_0"].config(state=tk.DISABLED)


        for i,prop in enumerate(self.props):
            self.props_entries[prop].grid(column = 1, row = i, padx = 5,pady = 5,sticky=tk.W)
            props_labels[i].grid(column = 0, row = i, padx = 8,pady = 5,sticky= tk.W)
        
        
        #Botones de las propiedades
        self.boton_borrar = ttk.Button(props_lf,width = 20,text="Borrar todo",command = self.borrar_campos)
        self.boton_borrar.grid(column = 0,row =len(self.props),padx =2, pady =5,sticky= tk.W)
        self.boton_guardar= ttk.Button(props_lf,text="Confirmar",width=20,command = lambda: self.guardar_campos(None))
        self.boton_guardar.grid(column = 1,row =len(self.props),padx =2, pady =5,sticky= tk.W)
        self.bind("<Return>",self.guardar_campos)

        #combobox
        self.comb_val = ["Acero"]
        self.combo = ttk.Combobox(props_lf,width = 30,value =self.comb_val,font =("Arial",12,"bold"),foreground="green",background="black")
        # self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>",self.combosel) 
        self.combo.grid(column = 0, row = len(self.props)+1,columnspan=2,padx = 5, pady = 8)
        
        #boton pruebav
        # self.probar_btn = ttk.Button(tabs[0],text = "probar",command=lambda: curvas_iniciacion(par = 'FS', da=1e-5, W = 10e-3, MAT=self.dict_prop))
        # self.probar_btn.grid(column = 0, row = 1, columnspan= 2,padx =10,pady = 5)
        
        #Label Frame del resumen 
        self.resum_lf =ttk.Labelframe(self.tabs["Material"],text = "Resumen")
        self.resum_lf.grid(column = 1,row =0,padx =20,pady=30,sticky=tk.NW)
        self.intro_resumen = ttk.Label(self.resum_lf, text = "Datos que se van a utilizar para la realización de los cálculos:",font = ("Arial",12))
        self.intro_resumen.grid(column = 0, row =0,padx = 20)
        self.resum_label ={}

        for i,prop in enumerate(self.props):
            self.resum_label[prop] = ttk.Label(self.resum_lf,text = prop+": ",font =("Arial",12,"bold")) 
            self.resum_label[prop].grid(column = 0,row =i+1, padx = 5,pady = 5,sticky=tk.W)

        ### Pestaña de Iniciación
        self.vars_iniciacion_frame = ttk.Labelframe(self.tabs["Iniciación"],text ="Variables para el cálculo de la iniciación",width=500)
        self.vars_iniciacion_frame.grid(column = 0, row= 0,padx =5, pady = 5)
        
        # self.boton_iniciacion = ttk.Button(self.vars_iniciacion_frame,text = "Iniciar",command = lambda:curvas_iniciacion(par = 'FS', da=1e-5, W = 10e-3, MAT=self.dict_prop) )
        # self.boton_iniciacion.pack(fill =tk.X)
        self.var_param = tk.StringVar()
        self.var_param.set("SWT")
        self.CB_param_SWT =ttk.Radiobutton(self.vars_iniciacion_frame,text ="\tSWT",variable= self.var_param,value="SWT",command = lambda: print(self.var_param.get()))
        self.CB_param_SWT.pack(anchor=tk.W,side = tk.TOP,padx =5)
        self.CB_param_FS =ttk.Radiobutton(self.vars_iniciacion_frame,text ="\tFS",variable = self.var_param,value="FS",command = lambda: print(self.var_param.get()))
        self.CB_param_FS.pack(anchor=tk.W,side = tk.TOP,padx = 5)
        
        self.mostrar_info()

        
    def combosel(self,event):
        """Selecciona un valor de la lista y completa los campos con los valores asignados.
        """
        for prop in self.props:
            if prop != "G" or prop !="a_0":
                self.props_entries[prop].delete(0,tk.END)
                self.props_entries[prop].insert(0,MAT[prop])   
    
    def borrar_campos(self):
        """Elimina los valores de los campos.
        """
        for prop in self.props:
            self.props_entries[prop].delete(0,tk.END)
        
        self.props_entries["G"].config(state=tk.DISABLED)
        self.props_entries["a_0"].config(state=tk.DISABLED)
        self.dict_prop = {}
        for prop in self.props:
            self.resum_label[prop].config(text =prop+": ")
            self.props_entries[prop].config(fg="black")
        

    def guardar_campos(self,event):
        """Guarda los valores en un diccionario que posteriormente se utiliza para la realización
        de los cálculos.
        """
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
                self.resum_label[prop].config(text = "{}:\t{:.3e}\t{}".format(prop,self.dict_prop[prop],self.dict_units[prop]))
        
        
    def mostrar_info(self):
        """Muestra la información del programa en una alerta.
        """
        tk.messagebox.showinfo("Información", """Este programa ha sido desarrollado por David García Serrano\npara el Trabajo de Fin de Máster\nAño 2021""")

   

        












if __name__ =="__main__":
    app = programa() 
    app.mainloop()





