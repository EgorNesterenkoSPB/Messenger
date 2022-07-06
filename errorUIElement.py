import tkinter as tk

def errorLabel(row,column,windowFrame,text):
    errorLabelFrame = tk.Frame(master=windowFrame)
    errorLabelFrame.grid(row=row,column=column)
    errorLabel = tk.Label(master=errorLabelFrame,text=text,foreground="red")
    errorLabel.grid(row=row,column=column)

    return errorLabelFrame