"""

@author: David García Serrano
"""
import os
import  tkinter as tk
from tkinter import ttk
import numpy as np
from iniciacion_b import curvas_iniciacion
from propagacion_b import MAT
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import pandas as pd

class programa(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo de Fatiga")
        self.state("zoomed")
        
        self.geometry("800x600+10+10")
        

        ### variables 
        self.props = ["C","n","f","l_0","K_th","sigma_fl","a_0","K_IC","sigma_y","sigma_f","E","nu","b","G"]
        self.units = ["","","","m","MPa m^0.5","MPa","m","MPa m^0.5","MPa","MPa","MPa","","","MPa"]
        self.dict_prop = {}
        self.mat_values ={}

        self.dict_units = dict(zip(self.props,self.units))

        self.N_i=[]
        self.n_a=1
        self.v_sigma=[]
        self.par =""
        self.W =0.0
        self.da =0.0
        self.filename =""
        self.df =pd.DataFrame()
        
        
        
        self.dir_exp =""
        self.files_exp =[]
        self.subdir_exp =""
        self.exp_files_path =""
        self.file_path =""
        self.acabados =["Sin Acabado","Electroerosion","Shotpeeling"]
        self.dict_acabados={self.acabados[0]:"sin_tratamiento",
                            self.acabados[2]:"shot_peening",
                            self.acabados[1]:"electroerosion"}
        self.acabado_var = tk.StringVar()
        self.df_datos =pd.DataFrame()

        for prop in self.props:
            self.mat_values[prop] = tk.StringVar()
        
    

        ### Menu
        self.menu = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Nuevo")
        self.file_menu.add_command(label="Abrir",command=self.carga_datos)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Guardar")
        self.file_menu.add_command(label="Guardar como...")
        self.menu.add_cascade(label="Archivo", menu=self.file_menu)
        self.menu.add_command(label="Acerca de",command =self.mostrar_info)
        self.menu.add_command(label="Salir", command=self.destroy)
        self.config(menu=self.menu)

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
            self.props_entries[prop] = ttk.Entry(props_lf,textvariable = self.mat_values[prop],width = 20,justify = "right",font =("Arial",10)) 
        props_labels = [ttk.Label(props_lf,text = f"{p}({self.dict_units[p]})",font =("Arial",10)) for p in self.props]
        self.props_entries["C"].focus_set()
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
        self.tabs["Material"].bind("<Return>",self.guardar_campos)

        #combobox
        self.comb_val = ["Acero"]
        self.combo = ttk.Combobox(props_lf,width = 30,value =self.comb_val,font =("Arial",12,"bold"),foreground="green",background="black")
        self.combo.bind("<<ComboboxSelected>>",self.combosel) 
        self.combo.grid(column = 0, row = len(self.props)+1,columnspan=2,padx = 5, pady = 8)
        
       
        ### Label Frame del resumen 
        self.resum_lf =ttk.Labelframe(self.tabs["Material"],text = "Resumen")
        self.resum_lf.grid(column = 1,row =0,padx =20,pady=30,sticky=tk.NW)
        self.intro_resumen = ttk.Label(self.resum_lf, text = "Datos que se van a utilizar para la realización de los cálculos:",font = ("Arial",12))
        self.intro_resumen.grid(column = 0, row =0,padx = 20)
        self.resum_label ={}

        for i,prop in enumerate(self.props):
            self.resum_label[prop] = ttk.Label(self.resum_lf,text = prop+": ",font =("Arial",12,"bold")) 
            self.resum_label[prop].grid(column = 0,row =i+1, padx = 5,pady = 5,sticky=tk.W)

        ### Pestaña de Iniciación

        self.vars_iniciacion_frame = ttk.Labelframe(self.tabs["Iniciación"],text ="Variables para el cálculo de la iniciación",width=1200,height= 600)
        self.vars_iniciacion_frame.place(relx= 0.01,rely =0.01,relwidth=0.975,relheight=0.25)
        
        self.var_param = tk.StringVar()
        self.var_param.set("SWT")
        
        self.CB_param_SWT =ttk.Radiobutton(self.vars_iniciacion_frame,text ="\tSWT",variable= self.var_param,value="SWT")
        self.CB_param_SWT.grid(column = 0, row= 0 , columnspan= 2,pady = 5, padx = 5,sticky = tk.W)
        self.CB_param_FS =ttk.Radiobutton(self.vars_iniciacion_frame,text ="\tFS",variable = self.var_param,value="FS")
        self.CB_param_FS.grid(column = 0, row= 1 , columnspan= 2,pady = 5, padx = 5,sticky = tk.W)
        
        self.W_entry = ttk.Entry(self.vars_iniciacion_frame,width = 6,justify=tk.RIGHT,font =("Arial",10))
        self.W_entry.grid(column = 0, row =2, sticky= tk.W,padx=5,pady=5)
        self.W_label = ttk.Label(self.vars_iniciacion_frame,text = "W",font =("Arial",10))
        self.W_label.grid(column =1, row = 2, sticky= tk.W)
        self.W_entry.insert(0,"10e-3")
        
        self.da_entry = ttk.Entry(self.vars_iniciacion_frame,width = 6,justify=tk.RIGHT)
        self.da_entry.grid(column = 0, row =3, sticky= tk.W,padx=5,pady=5)
        self.da_label = ttk.Label(self.vars_iniciacion_frame,text = "da")
        self.da_label.grid(column =1, row = 3, sticky= tk.W)
        self.da_entry.insert(0,"1e-5")
        
        #boton de probar
        self.ini_btn = ttk.Button(self.vars_iniciacion_frame,text = "Ejecutar iniciación",command =self.ejecutar_curvas)
        self.ini_btn.grid(column = 0,row= 4,columnspan=2 ,sticky=tk.W,padx = 5, pady = 5)

       
        
        #TreeFrame 
        
        self.tree_frame = tk.LabelFrame(self.tabs["Iniciación"],text = "Datos de Iniciación")
        self.tree_frame.place(relx =0.51,rely =0.27,relwidth=0.475,relheight=0.7)
        
        self.tree_scrollbarx = ttk.Scrollbar(self.tree_frame,orient =tk.HORIZONTAL)
        self.tree_scrollbary = ttk.Scrollbar(self.tree_frame,orient =tk.VERTICAL)
    
        self.tree_view =ttk.Treeview(self.tree_frame,xscrollcommand = self.tree_scrollbarx.set,yscrollcommand =self.tree_scrollbary.set)
        
        self.tree_scrollbarx.pack(side= tk.BOTTOM,fill =tk.X)
        self.tree_scrollbary.pack(side= tk.RIGHT,fill =tk.Y)
        self.tree_scrollbarx.config(command =self.tree_view.xview)
        self.tree_scrollbary.config(command =self.tree_view.yview)
        
        
        #CHART
        self.canvas_chart = tk.LabelFrame(self.tabs["Iniciación"],text = "gráfica de Iniciación")
        self.canvas_chart.place(relx =0.01,rely =0.27,relwidth=0.475,relheight=0.7)
        
        ### Pestaña Datos 
        
        #Label frame de datos experimentales
        self.dat_exp_lf = ttk.LabelFrame(self.tabs["Datos"],text = "Datos Experimentales")
        self.dat_exp_lf.place(relx = 0.01,rely = 0.01,relwidth=0.98,relheight=0.2)
        
        #combobox 
        self.combo_exp = ttk.Combobox(self.dat_exp_lf,width =50)
        self.combo_exp.bind("<<ComboboxSelected>>",self.sel_exp) 
        self.combo_exp.grid(column = 0, row =0,padx = 5, pady = 5)
        
        #Label frame acabado 
        self.acabado_lf =ttk.Labelframe(self.dat_exp_lf,text = "Tipo de acabado")
        self.acabado_lf.grid(column = 1, row =0,padx = 5, pady = 5)
        
        #RadioButtons de acabado    
        self.acabado_RB = {}
        self.acabado_var.set("Sin Acabado")
        
        for a in self.acabados: 
            self.acabado_RB[a]=ttk.Radiobutton(self.acabado_lf,text=a,variable =self.acabado_var, value =a,command=self.sel_acabado)
            self.acabado_RB[a].pack(anchor = tk.W,padx = 5, pady = 5)
        
        
        #Boton Cargar datos 
        self.cargar_dat_btn  = ttk.Button(self.dat_exp_lf, text = "Cargar Datos",command= self.carga_datos)
        self.cargar_dat_btn.grid(column = 2, row= 0, padx = 5, pady = 5)

        # Label Frame Gráficas 
        self.graf_lf = ttk.Labelframe(self.tabs["Datos"],text = "Gráficas")
        self.graf_lf.place(relx = 0.01, rely =0.22,relheight=0.75,relwidth= 0.48)

        self.graf_frame =tk.Frame(self.graf_lf)
        self.graf_frame.place(x = 5,rely = 0.16, relheight=0.83,relwidth =0.98)

        self.graf_opt_frame = tk.Frame(self.graf_lf,)
        self.graf_opt_frame.place(x = 5, y = 5, relwidth =0.98,relheight=0.15)

        self.combo_eje_x = ttk.Combobox(self.graf_opt_frame,width =40)
        self.combo_eje_y = ttk.Combobox(self.graf_opt_frame,width =40)
        self.combo_eje_x.grid(column =1, row=0, pady = 5, padx = 5)
        self.combo_eje_y.grid(column =1, row=1, pady = 5, padx = 5)

        self.label_eje_x = ttk.Label(self.graf_opt_frame ,text = "Eje X")
        self.label_eje_y =ttk.Label(self.graf_opt_frame ,text = "Eje Y")
        self.label_eje_x.grid(column =0, row =0, padx = 5)
        self.label_eje_y.grid(column =0, row = 1, padx = 5, pady =5)

        self.btn_graf =ttk. Button(self.graf_opt_frame,text = "Actualizar",command =self.actualizar_grafica)
        self.btn_graf.grid(column = 2, row = 0, rowspan= 2, padx = 5, pady = 5)



        # Label Frame Treeview
        self.dat_tree_lf = ttk.Labelframe(self.tabs["Datos"],text = "Datos")
        self.dat_tree_lf.place(relx = 0.5, rely =0.22,relheight=0.75,relwidth= 0.48)

        self.dat_scrollbarx = ttk.Scrollbar(self.dat_tree_lf,orient=tk.HORIZONTAL)
        self.dat_scrollbary = ttk.Scrollbar(self.dat_tree_lf,orient=tk.VERTICAL)

        self.dat_tv =ttk.Treeview(self.dat_tree_lf,xscrollcommand = self.dat_scrollbarx.set,yscrollcommand =self.dat_scrollbary.set)
        
        self.dat_scrollbarx.config(command =self.dat_tv.xview)
        self.dat_scrollbary.config(command =self.dat_tv.yview)
        self.dat_scrollbarx.pack(side= tk.BOTTOM,fill =tk.X)
        self.dat_scrollbary.pack(side= tk.RIGHT,fill =tk.Y)

        
        
        
        # self.mostrar_info()
        
        ### Funciones
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
                # self.props_entries[prop].config(fg= "green")
                self.resum_label[prop].config(text = "{}:\t{:.3e}\t{}".format(prop,self.dict_prop[prop],self.dict_units[prop]))
        
        
    def mostrar_info(self):
        """Muestra la información del programa en una alerta.
        """
        tk.messagebox.showinfo("Información", """Este programa ha sido desarrollado por David García Serrano\npara el Trabajo de Fin de Máster\nAño 2021""")

    def plot_iniciacion(self):
        if len(self.canvas_chart.winfo_children())>=1:
            for widget in self.canvas_chart.winfo_children():
                widget.destroy()
        self.figure = plt.figure(figsize =(6,4),dpi=100)
        self.figure.add_subplot(111)
        for i in range(self.n_a):
            
            plt.plot(self.N_i[:,i],self.v_sigma)
        plt.grid()
        plt.title(f"Curvas de iniciación para el parámetro {self.par}")
        plt.xscale("log")
        plt.xlabel("Ciclos")
        plt.ylabel("$\sigma (MPa)$")
        self.chart = FigureCanvasTkAgg(self.figure,self.canvas_chart)
        self.chart.draw()
        self.toolbar  = NavigationToolbar2Tk(self.chart,self.canvas_chart)
        self.toolbar.update()
        self.chart.get_tk_widget().pack(side = tk.TOP,padx =5,pady =5,fill= tk.BOTH,expand = 1)
        

    def ejecutar_curvas(self):
        self.par =self.var_param.get()
        self.da =float(self.da_entry.get())
        self.W= float(self.W_entry.get())
        
        self.N_i,self.n_a,self.v_sigma =curvas_iniciacion(par = self.par, da=self.da, W = self.W, MAT=self.dict_prop)

        self.plot_iniciacion()
        self.cargar_csv()
      
        
    def cargar_csv(self):
        
        try: 
            self.filename ="curvas_inic/MAT_{}.csv".format(self.par)
            self.df  =pd.read_csv(self.filename,sep="\t").dropna(axis =1)
        
        except ValueError:
            print("NO existe el archivo")
        except FileNotFoundError:
            print("NO existe el archivo")

        self.tree_view.delete(*self.tree_view.get_children())

        self.tree_view["column"] = list(self.df.columns.values)
        self.tree_view["show"] = "headings"

        for column in self.tree_view["column"] :
            self.tree_view.heading(str(column), text= str(column))

        df_rows = self.df.to_numpy().tolist()
        
     
        for row in df_rows:
            self.tree_view.insert("","end",values = tuple(row))
    
        
        self.tree_view.pack(fill =tk.BOTH, expand=1)

    def carga_datos(self):
        self.subdir_exp = self.acabado_var.get()
        self.dir_exp= tk.filedialog.askdirectory(title= "Abrir carpeta",initialdir=r"D:\Users\davidgarserra\Desktop\CLASE\MASTER\TFM")
        
        try:
            self.exp_files_path = os.path.join(self.dir_exp,self.dict_acabados[self.subdir_exp])
            self.files_exp = os.listdir(path=self.exp_files_path)
            self.combo_exp.config(value= self.files_exp)
        except FileNotFoundError:
            tk.messagebox.showerror("ERROR","En esta ruta no se encuentran las carpetas con los experimentos. Selecciona otra carpeta")
            
     
    def sel_exp(self,event):
        # if len(self.graf_lf.winfo_children())>=1:
        #     for widget in self.graf_frame.winfo_children():
        #         widget.destroy()
        self.file_path = os.path.join(self.exp_files_path,self.combo_exp.get())
        self.df_datos = pd.read_table(self.file_path,sep="\s+")
        self.df_datos.Y = -self.df_datos.Y*1e-3-0.1
        self.df_datos = self.df_datos.drop(r"%X",axis=1)
        
        self.dat_tv.delete(*self.dat_tv.get_children())

        self.combo_eje_x.config(value=list(self.df_datos.columns.values))
        self.combo_eje_y.config(value=list(self.df_datos.columns.values))
        self.combo_eje_x.set("Y")
        self.combo_eje_y.set("s_xx")

        # self.dat_figure = plt.figure(figsize=(6,4),dpi = 100)
        # self.dat_figure.add_subplot(111)
        # plt.plot(self.df_datos[self.combo_eje_x.get()],self.df_datos[self.combo_eje_y.get()])
        # plt.grid()
        # plt.title(f"Gráfica de {self.combo_eje_y.get()} con respecto {self.combo_eje_x.get()}")
        # plt.xlabel(f"{self.combo_eje_x.get()}")
        # plt.ylabel(f"{self.combo_eje_y.get()}")
        # self.dat_chart= FigureCanvasTkAgg(self.dat_figure,self.graf_frame)
        # self.dat_chart.draw()
        # self.toolbar_dat  = NavigationToolbar2Tk(self.dat_chart,self.graf_frame)
        # self.toolbar_dat.update()
        # self.dat_chart.get_tk_widget().pack(fill = tk.BOTH,expand=1)

        self.actualizar_grafica()

        self.dat_tv["column"] = list(self.df_datos.columns.values)
        self.dat_tv["show"] = "headings"

        for column in self.dat_tv["column"] :
            self.dat_tv.heading(column, text= column)

        df_rows = self.df_datos.to_numpy().tolist()

        for row in df_rows:
            self.dat_tv.insert("","end",values = tuple(row))
    
        
        self.dat_tv.pack(fill =tk.BOTH, expand=1,padx = 5, pady = 5)



    def sel_acabado(self):
        try:
            self.subdir_exp = self.acabado_var.get()
            self.exp_files_path = os.path.join(self.dir_exp,self.dict_acabados[self.subdir_exp])
            self.files_exp = os.listdir(path=self.exp_files_path)
            self.combo_exp.config(value= self.files_exp)
        except FileNotFoundError:
            tk.messagebox.showerror("ERROR","No existen la carpeta con los experimentos")
        
    def actualizar_grafica(self):
        if len(self.graf_lf.winfo_children())>=1:
            for widget in self.graf_frame.winfo_children():
                widget.destroy()

        self.dat_figure = plt.figure(figsize=(6,4),dpi = 100)
        self.dat_figure.add_subplot(111)
        plt.plot(self.df_datos[self.combo_eje_x.get()],self.df_datos[self.combo_eje_y.get()])
        plt.grid()
        plt.title(f"Gráfica de {self.combo_eje_y.get()} con respecto {self.combo_eje_x.get()}")
        plt.xlabel(f"{self.combo_eje_x.get()}")
        plt.ylabel(f"{self.combo_eje_y.get()}")
        self.dat_chart= FigureCanvasTkAgg(self.dat_figure,self.graf_frame)
        self.dat_chart.draw()
        self.toolbar_dat  = NavigationToolbar2Tk(self.dat_chart,self.graf_frame)
        self.toolbar_dat.update()
        self.dat_chart.get_tk_widget().pack(fill = tk.BOTH,expand=1)
                    

        
        
        
        

        












if __name__ =="__main__":
    app = programa() 
    app.mainloop()





