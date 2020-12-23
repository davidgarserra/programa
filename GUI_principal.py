"""

@author: David García 
"""
import  tkinter as tk

class programa(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo de Fatiga")

if __name__ =="__main__":
    app = programa() 
    app.mainloop()





