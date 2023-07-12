import customtkinter as ctk
import pyvisa
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from customtkinter import filedialog

def main():
    ''' Initializations '''
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.geometry("1200x800")
    root.title("Ramsauer Experiment")
    root.resizable(False,False)
    colorTheme=["Light Mode", "Dark Mode"]
    tabControl = ctk.CTkTabview(root,width=1150,height=750)
    tabControl.pack(padx=20,pady=20)
    resourceList = pyvisa.ResourceManager().list_resources()
    global multimeterV_P
    global multimeterV_S
    global multimeterVV_S
    global tempData
    global sessionData
    global importData
    sessionData=[]
    importData=[]
    multimeterV_P = pyvisa.ResourceManager().open_resource(resourceList[0])
    multimeterV_P.write('DISP:TEXT "V_P"')
    multimeterV_S = pyvisa.ResourceManager().open_resource(resourceList[1])
    multimeterV_S.write('DISP:TEXT "V_S"')
    multimeterVV_S = pyvisa.ResourceManager().open_resource(resourceList[2])
    multimeterVV_S.write('DISP:TEXT "V - V_S"')
   
    ''' First Window '''
    def fix():
        global importData
        global sessionData
        for i in range(len(importData)):
            temp=[]
            for j in range(len(importData[i])):
                temp.append(float(importData[i][j]))
            sessionData.append(temp)
        print(sessionData)
       
    def startNew():
        firstWindow.destroy()
       
    def continueOld():
        skip = True
        global sessionData
        global importData
        root.filename = filedialog.askopenfilename(initialdir = '/Users/student/Desktop', title = "Select Directory to Save in")
        with open(root.filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for i in reader:
                if skip:
                    skip = False
                    continue
                importData.append(i)
            fix()
            graph()
        firstWindow.destroy()
       
    firstWindow = ctk.CTkToplevel(root)
    firstWindow.geometry("500x250")
    firstWindow.title("New or Returning User?")
    firstWindow.resizable(False,False)
    firstWindow.rowconfigure(1, weight=1)
    firstWindow.columnconfigure(2, weight=1)
   
    firstGrid = ctk.CTkFrame(firstWindow,corner_radius=10)
    firstGrid.grid(row=1,column=1,padx=100,pady=100)
    firstGrid.rowconfigure(1, weight=1)
    firstGrid.columnconfigure(1, weight=1)
   
    startNewWindow = ctk.CTkButton(firstGrid,text="Start New Collection",command=startNew)
    startNewWindow.grid(row=1,column=1,pady=10,padx=10)
   
    continueOldWindow = ctk.CTkButton(firstGrid,text="Continue Old Collection",command=continueOld)
    continueOldWindow.grid(row=1,column=2,pady=10,padx=10)
   
    ''' Functions '''
    def changeV_P(newV_P):
        global multimeterV_P
        multimeterV_P = pyvisa.ResourceManager().open_resource(newV_P)
        multimeterV_P.write('DISP:TEXT "V_P"')
       
    def changeV_S(newV_S):
        global multimeterV_S
        multimeterV_S = pyvisa.ResourceManager().open_resource(newV_S)
        multimeterV_S.write('DISP:TEXT "V_S"')
       
    def changeVV_S(newVV_S):
        global multimeterVV_S
        multimeterVV_S = pyvisa.ResourceManager().open_resource(newVV_S)
        multimeterVV_S.write('DISP:TEXT "V - V_S"')
       
    def changeTheme(choice):
        if (choice=="Dark Mode"):
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
           
    def adjust(x):
        return str(round(x,6))+" V"
           
    def measure():
        global tempData
        tempData = [multimeterV_P.query_ascii_values("MEAS:VOLT?")[0],
                    multimeterV_S.query_ascii_values("MEAS:VOLT?")[0],
                    multimeterVV_S.query_ascii_values("MEAS:VOLT?")[0]]
        resultV_Pm.configure(text=adjust(tempData[0]))
        resultV_Sm.configure(text=adjust(tempData[1]))
        resultVV_Sm.configure(text=adjust(tempData[2]))
       
    def appendData():
        global tempData
        global sessionData
        sessionData.append(tempData)
        graph()
       
    def column(matrix, i):
        return [row[i] for row in matrix]
       
    def graph():
        global sessionData
        Vp = column(sessionData,0)
        Vs = column(sessionData,1)
        VVs = column(sessionData,2)
       
        graphV_P = Figure(figsize=(3.5,3.5), dpi=100)
        subV_P = graphV_P.add_subplot(111, xlabel="V - Vs (V)", ylabel="Vp (V)")
        subV_P.plot(VVs, Vp)
        graphV_P.set_layout_engine('constrained')
        canvasV_P = FigureCanvasTkAgg(graphV_P, master=graphGrid)
        canvasV_P.draw()
        canvasV_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)
       
        graphV_S = Figure(figsize=(3.5,3.5), dpi=100)
        subV_S = graphV_S.add_subplot(111, xlabel="V - Vs (V)", ylabel="VS (V)", )
        subV_S.plot(VVs, Vs)
        graphV_S.set_layout_engine('constrained')
        canvasV_S = FigureCanvasTkAgg(graphV_S, master=graphGrid)
        canvasV_S.draw()
        canvasV_S.get_tk_widget().grid(row=1,column=2,padx=10,pady=10)
   
    def saveToFile():
        global sessionData
        filevariable = filename.get()
        f = open(("C:/Users/student/Desktop/" + filevariable + ".csv"), 'w', newline='')
        writer = csv.writer(f)
        header = ["Vp", "Vs", "V - Vs"]
        writer.writerow(header)
        for i in range(len(sessionData)):
            writer.writerow(sessionData[i])
        f.close()
   
    ''' Main Page Configuration '''
    mainPage = tabControl.add("Main Application")
    mainPage.rowconfigure(10, weight=1)
    mainPage.columnconfigure(2, weight=1)
    collectionGrid = ctk.CTkFrame(mainPage,corner_radius=10, width=1000)
    collectionGrid.grid(row=1,column=1,padx=20)
    collectionGrid.rowconfigure(1, weight=1)
    collectionGrid.columnconfigure(0, weight=1)
    buttonGrid = ctk.CTkFrame(collectionGrid,corner_radius=10)
    buttonGrid.grid(row=3,column=0,padx=20,pady=20)
    buttonGrid.rowconfigure(1, weight=1)
    buttonGrid.columnconfigure(2, weight=1)
    graphGrid = ctk.CTkFrame(mainPage,corner_radius=10)
    graphGrid.grid(row=1,column=2,padx=10,pady=10)
    graphGrid.rowconfigure(1, weight=1)
    graphGrid.columnconfigure(2, weight=1)
    saveGrid = ctk.CTkFrame(mainPage,corner_radius=10)
    saveGrid.grid(row=2,column=2,padx=10,pady=10)
    saveGrid.rowconfigure(2, weight=1)
    saveGrid.columnconfigure(2, weight=1)
   
   
    ''' Multimeter Page Configuration '''
    multimeterPage = tabControl.add("Multimeter Settings")
    multimeterPage.rowconfigure(0, weight=1)
    multimeterPage.columnconfigure(0, weight=1)
    multimeterSet = ctk.CTkFrame(multimeterPage,corner_radius=10)
    multimeterSet.grid(row=0,column=0)
    multimeterSet.rowconfigure(2, weight=1)
    multimeterSet.columnconfigure(0, weight=1)
   
    ''' Graph Initialization '''
    graphV_P = Figure(figsize=(3.5,3.5), dpi=100)
    subV_P = graphV_P.add_subplot(111, xlabel="V - Vs (V)", ylabel="Vp (V)", )
    subV_P.plot(1,1)
    graphV_P.set_layout_engine('constrained')
    canvasV_P = FigureCanvasTkAgg(graphV_P, master=graphGrid)
    canvasV_P.draw()
    canvasV_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)  
   
    graphV_S = Figure(figsize=(3.5,3.5), dpi=100)
    subV_S = graphV_S.add_subplot(111, xlabel="V - Vs (V)", ylabel="VS (V)", )
    subV_S.plot(1,1)
    graphV_S.set_layout_engine('constrained')
    canvasV_S = FigureCanvasTkAgg(graphV_S, master=graphGrid)
    canvasV_S.draw()
    canvasV_S.get_tk_widget().grid(row=1,column=2,padx=10,pady=10)
   
    ''' Main Page Utilities '''
    measureButton = ctk.CTkButton(buttonGrid,text="Measure",command=measure)
    measureButton.grid(row=3,column=0,pady=10,padx=10)
   
    appendButton = ctk.CTkButton(buttonGrid,text="Append",command=appendData)
    appendButton.grid(row=3,column=1,pady=10,padx=10)
   
    dropdown = ctk.CTkOptionMenu(mainPage,values=colorTheme,command=changeTheme)
    dropdown.grid(row=10,column=1)
   
    saveButton = ctk.CTkButton(saveGrid,text="Save",command=saveToFile)
    saveButton.grid(row=1,column=2,pady=10,padx=10)
   
    filename = ctk.CTkEntry(saveGrid, width=300,placeholder_text="Enter filename without filetype (saves to Desktop)")
    filename.grid(row=1,column=1,pady=10,padx=10)
   
    ''' V_P Multimeter selection '''
    frameV_P = ctk.CTkFrame(multimeterSet,width=500,height=50,corner_radius=10)
    frameV_P.grid(row=0,column=0,padx=20,pady=50)
    frameV_P.rowconfigure(0)
    frameV_P.columnconfigure((0,1), weight=1)
   
    labelV_P = ctk.CTkLabel(frameV_P, text="V_P Multimeter:",fg_color="grey", corner_radius=10, text_color="white")
    labelV_P.grid(column=0, row=0, padx=10, pady=10)
   
    resourceListDropdownV_P = ctk.CTkOptionMenu(frameV_P,width=300,values=resourceList,command=changeV_P)
    resourceListDropdownV_P.grid(column=1, row=0, padx=10, pady=10)
   
    ''' V_S Multimeter selection '''
    frameV_S = ctk.CTkFrame(multimeterSet,width=500,height=50,corner_radius=10)
    frameV_S.grid(row=1,column=0,padx=20,pady=50)
    frameV_S.rowconfigure(0)
    frameV_S.columnconfigure((0,1), weight=1)
   
    labelV_S = ctk.CTkLabel(frameV_S, text="V_S Multimeter:",fg_color="grey", corner_radius=10, text_color="white")
    labelV_S.grid(column=0, row=0, padx=10, pady=10)
   
    resourceListDropdownV_S = ctk.CTkOptionMenu(frameV_S,width=300,values=resourceList,command=changeV_S)
    resourceListDropdownV_S.grid(column=1, row=0, padx=10, pady=10)
   
    ''' V - V_S Multimeter selection '''
    frameVV_S = ctk.CTkFrame(multimeterSet,width=500,height=50,corner_radius=10)
    frameVV_S.grid(row=2,column=0,padx=20,pady=50)
    frameVV_S.rowconfigure(0)
    frameVV_S.columnconfigure((0,1), weight=1)
   
    labelVV_S = ctk.CTkLabel(frameVV_S, text="V - V_S Multimeter:",fg_color="grey", corner_radius=10, text_color="white")
    labelVV_S.grid(column=0, row=0, padx=10, pady=10)
   
    resourceListDropdownVV_S = ctk.CTkOptionMenu(frameVV_S,width=300,values=resourceList,command=changeVV_S)
    resourceListDropdownVV_S.grid(column=1, row=0, padx=10, pady=10)
   
   
   
    ''' V_P Multimeter measuring '''
    frameV_Pm = ctk.CTkFrame(collectionGrid,width=200,height=50,corner_radius=10)
    frameV_Pm.grid(row=0,column=0,padx=20,pady=50)
    frameV_Pm.rowconfigure(0)
    frameV_Pm.columnconfigure((0,1), weight=1)
   
    labelV_Pm = ctk.CTkLabel(frameV_Pm, text="V_P Measurement (V):",fg_color="grey", corner_radius=10, text_color="white")
    labelV_Pm.grid(column=0, row=0, padx=10, pady=10)
   
    resultV_Pm = ctk.CTkLabel(frameV_Pm, text="-----",fg_color="grey", corner_radius=10, text_color="white")
    resultV_Pm.grid(column=1, row=0, padx=10, pady=10)
   
    ''' V_S Multimeter measuring '''
    frameV_Sm = ctk.CTkFrame(collectionGrid,width=200,height=50,corner_radius=10)
    frameV_Sm.grid(row=1,column=0,padx=20,pady=50)
    frameV_Sm.rowconfigure(0)
    frameV_Sm.columnconfigure((0,1), weight=1)
   
    labelV_Sm = ctk.CTkLabel(frameV_Sm, text="V_S Measurement (V):",fg_color="grey", corner_radius=10, text_color="white")
    labelV_Sm.grid(column=0, row=0, padx=10, pady=10)
   
    resultV_Sm = ctk.CTkLabel(frameV_Sm, text="-----",fg_color="grey", corner_radius=10, text_color="white")
    resultV_Sm.grid(column=1, row=0, padx=10, pady=10)
   
    ''' V - V_S Multimeter measuring '''
    frameVV_Sm = ctk.CTkFrame(collectionGrid,width=200,height=50,corner_radius=10)
    frameVV_Sm.grid(row=2,column=0,padx=20,pady=50)
    frameVV_Sm.rowconfigure(0)
    frameVV_Sm.columnconfigure((0,1), weight=1)
   
    labelV_Sm = ctk.CTkLabel(frameVV_Sm, text="V - V_S Measurement (V):",fg_color="grey", corner_radius=10, text_color="white")
    labelV_Sm.grid(column=0, row=0, padx=10, pady=10)
   
    resultVV_Sm = ctk.CTkLabel(frameVV_Sm, text="-----",fg_color="grey", corner_radius=10, text_color="white")
    resultVV_Sm.grid(column=1, row=0, padx=10, pady=10)
     
    root.mainloop()
main()