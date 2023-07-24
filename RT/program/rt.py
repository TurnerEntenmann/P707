import customtkinter as ctk
import numpy as np
import pyvisa, csv, os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from customtkinter import filedialog, CTkOptionMenu
from tkinter import messagebox, StringVar, OptionMenu
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

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
    # directory to save data in
    global saving_dir
    saving_dir = ""

    sessionData=[]
    importData=[]
    n_connections = len(resourceList)
    if n_connections != 3:
        messagebox.showerror("Connection Error", f"3 Connections Required\n{n_connections} Detected\n\nMake sure all multimeters are powered on and plugged in")
        # TODO: comment out
        # return 0
    else:
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

    def make_dir():
        global dir_name_entry, dir_name, dir_window, saving_dir
        dir_name = dir_name_entry.get()
        if dir_name in os.listdir():
            messagebox.showerror("Name Error", f"{dir_name} Already exists, please use a different name")
            dir_window.destroy()
            startNew()
        else:
            os.makedirs(dir_name)
            print("old saving dir", saving_dir)
            print("original cwd", os.getcwd())
            os.chdir(dir_name)
            saving_dir = os.getcwd()
            os.chdir("..")
            print("new saving dir", saving_dir)
            print("new cwd", os.getcwd())
            dir_window.destroy()

    def cancel_new_entry():
        dir_window.destroy()
        start_window()
       
    def startNew():
        global dir_name_entry, dir_window
        firstWindow.destroy()
        dir_window = ctk.CTkToplevel(root)
        dir_window.geometry("750x500")
        dir_window.title("Create Folder")
        dir_window.resizable(False,False)
        dir_window.rowconfigure(1, weight=1)
        dir_window.columnconfigure(1, weight=1)
   
        dir_grid = ctk.CTkFrame(dir_window,corner_radius=10)
        dir_grid.grid(row=1,column=1,padx=100,pady=100)
        dir_grid.rowconfigure(1, weight=1)
        dir_grid.columnconfigure(1, weight=1)
        dir_grid.rowconfigure(2, weight=1)
        dir_grid.columnconfigure(2, weight=1)
 
        dir_name_entry = ctk.CTkEntry(dir_grid, width=300,placeholder_text="Folder Name e.g. group1")
        dir_name_entry.grid(row=0,column=0,pady=10,padx=10)

        create_dir_but = ctk.CTkButton(dir_grid,text="Create",command=make_dir)
        create_dir_but.grid(row=0,column=1,pady=10,padx=10)

        cancel_but = ctk.CTkButton(dir_grid, text="Cancel", command=cancel_new_entry)
        cancel_but.grid(row=1, column=0, pady=10, padx=10)


    def choose_dir():
        global selected, saving_dir, con_window
        print("old saving dir", saving_dir)
        print("original cwd", os.getcwd())
        os.chdir(selected.get())
        saving_dir = os.getcwd()
        os.chdir("..")
        print("new saving dir", saving_dir)
        print("new cwd", os.getcwd())
        con_window.destroy()



    def choose_folder():
        global selected
        print(selected.get())


    def continueOld():
        global selected, con_window
        firstWindow.destroy()
        con_window = ctk.CTkToplevel(root)
        con_window.geometry("500x500")
        con_window.title("Select Folder")
        con_window.resizable(False,False)
        con_window.rowconfigure(1, weight=1)
        con_window.columnconfigure(1, weight=1)

        con_grid = ctk.CTkFrame(con_window,corner_radius=10)
        con_grid.grid(row=1,column=1,padx=100,pady=100)
        con_grid.rowconfigure(1, weight=1)
        con_grid.columnconfigure(1, weight=1)
        con_grid.rowconfigure(2, weight=1)
        con_grid.columnconfigure(2, weight=1)

        folder_list = os.listdir()

        selected = StringVar()
        selected.set(os.listdir()[0])
        drop_menu = ctk.CTkOptionMenu(master=con_grid, variable=selected, values=folder_list)
        drop_menu.grid(row=0, column=0, pady=10, padx=10)

        choose_button = ctk.CTkButton(con_grid,text="Select Folder",command=choose_dir)
        choose_button.grid(row=1, column=0, pady=10, padx=10)


        #skip = True
        #global sessionData
        #global importData
        #root.filename = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select Directory to Save in")
        ## if a dir is selected
        #if len(root.filename) > 0:
        #    with open(root.filename, newline='') as csvfile:
        #        reader = csv.reader(csvfile)
        #        for i in reader:
        #            if skip:
        #                skip = False
        #                continue
        #            importData.append(i)
        #        fix()
        #        graph()
        #    firstWindow.destroy()
        ## if the operation is canceled
        #else:
        #    firstWindow.destroy()
        #    start_window()


    def start_window():
        global firstWindow
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
    
    start_window()
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
        subV_P = graphV_P.add_subplot(111, xlabel="$V-V_s$ (V)", ylabel="$V_p$ (V)")
        subV_P.spines[['right', 'top']].set_visible(False)
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
        global sessionData, saving_dir
        filevariable = filename.get()
        # force .csv
        if ".csv" not in filevariable:
            messagebox.showerror("File Type Error", "Make sure to include '.csv' in the filename")
        else:
            os.chdir(saving_dir)
            f = open(filevariable, 'w', newline='')
            writer = csv.writer(f)
            header = ["Vp", "Vs", "V - Vs"]
            writer.writerow(header)
            for i in range(len(sessionData)):
                writer.writerow(sessionData[i])
            f.close()
            os.chdir("..")

    # fxn for plotting
    def get_ax(figsize=(6,4), fsize=15):
        fig, ax = plt.subplots(figsize=figsize)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        return ax, fsize

    #TODO: make_igraph
    # isave_to_file
    # button to gen graph
    # make dir to collect data / figs

    #global sessionData
    #Vp = column(sessionData,0)
    #Vs = column(sessionData,1)
    #VVs = column(sessionData,2)

    def make_igraph():
        global sessionData
        Vp = column(sessionData,0)
        Vs = column(sessionData,1)
        VVs = column(sessionData,2)

        rp = float(Rp.get())
        fs = float()
       
        graphI_P = Figure(figsize=(3.5,3.5), dpi=100)
        subI_P = graphI_P.add_subplot(111, xlabel="$V-V_s$ (V)", ylabel="$I_p$ (A)", fontsize=float(fs))
        subI_P.spines[['right', 'top']].set_visible(False)

        subI_P.plot(np.sqrt(VVs), Vp / rp)
        graphI_P.set_layout_engine('constrained')
        canvasI_P = FigureCanvasTkAgg(graphI_P, master=graphGrid)
        canvasI_P.draw()
        canvasI_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)
   
    def isave_to_file():
        pass

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
   


    # I graph page config
    igraph_page = tabControl.add("Current Plot")
    igraph_page.rowconfigure(10, weight=1)
    igraph_page.columnconfigure(2, weight=1)

    settings_grid = ctk.CTkFrame(igraph_page, corner_radius=10, width=100)
    settings_grid.grid(row=1, column=1, padx=20)
    settings_grid.rowconfigure(1, weight=1)
    settings_grid.columnconfigure(0, weight=1)

    ibutton_grid = ctk.CTkFrame(settings_grid,corner_radius=10)
    ibutton_grid.grid(row=3,column=0,padx=20,pady=20)
    ibutton_grid.rowconfigure(1, weight=1)
    ibutton_grid.columnconfigure(2, weight=1)

    make_igraph_button = ctk.CTkButton(ibutton_grid,text="Make Graph",command=make_igraph)
    make_igraph_button.grid(row=0,column=0,pady=10,padx=10)
   
    filename = ctk.CTkEntry(saveGrid, width=300,placeholder_text="filename e.g. C:/Users/student/Desktop/run1.csv")
    filename.grid(row=1,column=1,pady=10,padx=10)

    igraph_grid = ctk.CTkFrame(igraph_page,corner_radius=10)
    igraph_grid.grid(row=1,column=2,padx=10,pady=10)
    igraph_grid.rowconfigure(1, weight=1)
    igraph_grid.columnconfigure(2, weight=1)

    isave_grid = ctk.CTkFrame(igraph_page,corner_radius=10)
    isave_grid.grid(row=2,column=2,padx=10,pady=10)
    isave_grid.rowconfigure(2, weight=1)
    isave_grid.columnconfigure(2, weight=1)

    isave_button = ctk.CTkButton(isave_grid,text="Save",command=isave_to_file)
    isave_button.grid(row=1,column=2,pady=10,padx=10)
    ifilename = ctk.CTkEntry(isave_grid, width=300,placeholder_text="filename e.g. C:/Users/student/Desktop/Ip.pdf")
    ifilename.grid(row=1,column=1,pady=10,padx=10)

    # rp
    frameR_P = ctk.CTkFrame(settings_grid,width=500,height=50,corner_radius=10)
    frameR_P.grid(row=0,column=0,padx=20,pady=50)
    frameR_P.rowconfigure(0)
    frameR_P.columnconfigure((0,1), weight=1)
    Rp_lab = ctk.CTkLabel(frameR_P, text="R_p:",fg_color="grey", corner_radius=10, text_color="white")
    Rp_lab.grid(row=0, column=0)
    Rp = ctk.CTkEntry(frameR_P, width=100, placeholder_text="10000")
    Rp.grid(row=0, column=1, padx=10, pady=10)
    
    # fontsize
    frame_font = ctk.CTkFrame(settings_grid,width=500,height=50,corner_radius=10)
    frame_font.grid(row=1,column=0,padx=20,pady=50)
    frame_font.rowconfigure(0)
    frame_font.columnconfigure((0,1), weight=1)
    Fs_lab = ctk.CTkLabel(frame_font, text="Fontsize",fg_color="grey", corner_radius=10, text_color="white")
    Fs_lab.grid(row=0, column=0)
    Fs = ctk.CTkEntry(frame_font, width=100, placeholder_text="15")
    Fs.grid(row=0, column=1, padx=10, pady=10)

    # I_P
    graphI_P = Figure(figsize=(3.5,3.5), dpi=100)
    subI_P = graphI_P.add_subplot(111, xlabel="$\sqrt{V-V_s}$ ($\sqrt{V}$)", ylabel="$I_p$ (A)", )
    subI_P.spines[['right', 'top']].set_visible(False)
    graphI_P.set_layout_engine('constrained')
    canvasI_P = FigureCanvasTkAgg(graphI_P, master=igraph_grid)
    canvasI_P.draw()
    canvasI_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)  
   
   # subV_P.plot(1,1)
   # graphV_P.set_layout_engine('constrained')
   # canvasV_P = FigureCanvasTkAgg(graphV_P, master=graphGrid)
   # canvasV_P.draw()
   # canvasV_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)  
   ## V_S
   # graphV_S = Figure(figsize=(3.5,3.5), dpi=100)
   # subV_S = graphV_S.add_subplot(111, xlabel="$V-V_s$ (V)", ylabel="$V_s$ (V)", )
   # subV_S.spines[['right', 'top']].set_visible(False)

   # subV_S.plot(1,1)
   # graphV_S.set_layout_engine('constrained')
   # canvasV_S = FigureCanvasTkAgg(graphV_S, master=graphGrid)
   # canvasV_S.draw()
   # canvasV_S.get_tk_widget().grid(row=1,column=2,padx=10,pady=10)






   
    ''' Multimeter Page Configuration '''
    multimeterPage = tabControl.add("Multimeter Settings")
    multimeterPage.rowconfigure(0, weight=1)
    multimeterPage.columnconfigure(0, weight=1)
    multimeterSet = ctk.CTkFrame(multimeterPage,corner_radius=10)
    multimeterSet.grid(row=0,column=0)
    multimeterSet.rowconfigure(2, weight=1)
    multimeterSet.columnconfigure(0, weight=1)







   
    ''' Graph Initialization '''
    # V_P
    graphV_P = Figure(figsize=(3.5,3.5), dpi=100)
    subV_P = graphV_P.add_subplot(111, xlabel="$V-V_s$ (V)", ylabel="$V_p$ (V)", )
    subV_P.spines[['right', 'top']].set_visible(False)

    subV_P.plot(1,1)
    graphV_P.set_layout_engine('constrained')
    canvasV_P = FigureCanvasTkAgg(graphV_P, master=graphGrid)
    canvasV_P.draw()
    canvasV_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)  
   # V_S
    graphV_S = Figure(figsize=(3.5,3.5), dpi=100)
    subV_S = graphV_S.add_subplot(111, xlabel="$V-V_s$ (V)", ylabel="$V_s$ (V)", )
    subV_S.spines[['right', 'top']].set_visible(False)

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
   
    filename = ctk.CTkEntry(saveGrid, width=300,placeholder_text="filename e.g. C:/Users/student/Desktop/run1.csv")
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