import customtkinter as ctk
import numpy as np
import pandas as pd
import pyvisa, csv, os
from math import log10, floor
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

    global fig, tfig
    global hot_cold
    global avail_csvs
    global hot_csv, cold_csv, tfilename, tFs_ent

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
    def populate_csv_menu():
        global saving_dir, avail_csvs
        data_dir=os.path.join(saving_dir, "data")
        avail_csvs = os.listdir(data_dir)
        hot_csv_menu = ctk.CTkOptionMenu(master=hcsv_frame, variable=hot_csv, values=avail_csvs)
        hot_csv_menu.grid(row=0, column=1, pady=10, padx=10)
        cold_csv_menu = ctk.CTkOptionMenu(master=ccsv_frame, variable=cold_csv, values=avail_csvs)
        cold_csv_menu.grid(row=0, column=1, pady=10, padx=10)

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
            os.makedirs("plots")
            os.makedirs("data")
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
        populate_csv_menu()
        con_window.destroy()

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
        global sessionData, saving_dir, hot_cold
        filevariable = hot_cold.get() +"_" + filename.get()
        # force .csv
        if ".csv" not in filevariable:
            if "." in filevariable:
                messagebox.showerror("File Type Error", "Make sure to save as a '.csv'")
                return 0
            else:
                filevariable += ".csv"
        data_dir = os.path.join(saving_dir, "data")
        os.chdir(data_dir)
        if filevariable in os.listdir():
            messagebox.showerror("File Name Error", f"{filevariable} already exists, please use a different file name")
            return 0
        try:
            f = open(filevariable, 'w', newline='')
            writer = csv.writer(f)
            header = ["Vp", "Vs", "V - Vs"]
            writer.writerow(header)
            for i in range(len(sessionData)):
                writer.writerow(sessionData[i])
            f.close()
            messagebox.showinfo("", f"Data saved as\n\t{filevariable}\nIn\n\t{data_dir}")
        except:
            messagebox.showerror("File Type Error", f"Failed to write to {filevariable}\nMake sure to save with a valid filename")
        os.chdir("..")
        os.chdir("..")
        populate_csv_menu()

    def round_sig(x, sig=2):
        return round(x, sig-int(floor(log10(abs(x))))-1)
    #TODO:
    # i plot hot and cold
        # add as option in transmission graph page
    # plot and T, find best T
        # customization
        # error handeling eg not selecting files to plot
    # color buttons

    def make_igraph():
        global sessionData, fig, hot_cold
        Vp = np.array(column(sessionData,0))
        Vs = np.array(column(sessionData,1))
        VVs = np.array(column(sessionData,2))

        try:
            rp = float(Rp_var.get())
            fs = float(Fs_var.get())
        except ValueError as ve:
            messagebox.showerror("Value Error", f"R_p and Fontsize must be numbers, please check their values")
            return 0
        
        fig, ax = plt.subplots(figsize=(3.5,3.5), dpi=100)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel("$\sqrt{V-V_s}$ $(\sqrt{V})$", size=fs)
        print(hot_cold.get())
        if hot_cold.get() == "Hot":
            y_lab = "$I_p$ (A)"
        else:
            y_lab = "$I_p^*$ (A)"
        fig, ax = plt.subplots(figsize=(3.5,3.5), dpi=100)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel("$\sqrt{V-V_s}$ $(\sqrt{V})$", size=fs)
        if hot_cold.get() == "Hot":
            ax.set_ylabel("$I_p$ (A)", size=fs)
        else:
            ax.set_ylabel("$I_p^*$ (A)", size=fs)
        ax.tick_params(axis='both', which='major', labelsize=fs-2)
        fig.set_layout_engine("constrained")
        canvasI_P = FigureCanvasTkAgg(fig, master=igraph_grid)
        canvasI_P.draw()
        canvasI_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)

   
    def isave_to_file():
        global saving_dir, fig, hot_cold
        fname = hot_cold.get() + "_" + ifilename.get()
        if ".pdf" not in fname:
            if "." in fname:
                messagebox.showerror("File Type Error", "Make sure to save as a '.pdf'")
                return 0
            else:
                fname += ".pdf"
        plot_dir = os.path.join(saving_dir, "plots")
        os.chdir(plot_dir)
        try:
            fig.savefig(fname)
            messagebox.showinfo("", f"Plot saved as\n\t{fname}\nIn\n\t{plot_dir}")
        except Exception as e:
            print(e)
            messagebox.showerror("File Type Error", f"Failed to write to {fname}\nMake sure to save with a valid finame")
        os.chdir("..")
        os.chdir("..")


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
   


    # single I graph page config
    igraph_page = tabControl.add("Single Current Plot")
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

    make_igraph_button = ctk.CTkButton(ibutton_grid,text="Draw Graph",command=make_igraph)
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
    isave_grid.columnconfigure(3, weight=1)

    hot_cold = StringVar()
    hot_cold.set("Hot")
    i_hc_menu = ctk.CTkOptionMenu(master=isave_grid, variable=hot_cold, values=["Hot", "Cold"])
    i_hc_menu.grid(row=1, column=2, pady=10, padx=10)

    isave_button = ctk.CTkButton(isave_grid,text="Save",command=isave_to_file)
    isave_button.grid(row=1,column=3,pady=10,padx=10)
    ifilename = ctk.CTkEntry(isave_grid, width=300,placeholder_text="filename e.g. C:/Users/student/Desktop/Ip.pdf")
    ifilename.grid(row=1,column=1,pady=10,padx=10)

    # rp
    frameR_P = ctk.CTkFrame(settings_grid,width=500,height=50,corner_radius=10)
    frameR_P.grid(row=0,column=0,padx=20,pady=50)
    frameR_P.rowconfigure(0)
    frameR_P.columnconfigure((0,1), weight=1)
    Rp_var = ctk.StringVar(value="1000")
    Rp_lab = ctk.CTkLabel(frameR_P, text="R_p:",fg_color="grey", corner_radius=10, text_color="white")
    Rp_lab.grid(row=0, column=0)
    Rp_ent = ctk.CTkEntry(frameR_P, width=100, placeholder_text="1000", textvariable=Rp_var)
    Rp_ent.grid(row=0, column=1, padx=10, pady=10)

    
    # fontsize
    frame_font = ctk.CTkFrame(settings_grid,width=500,height=50,corner_radius=10)
    frame_font.grid(row=1,column=0,padx=20,pady=50)
    frame_font.rowconfigure(0)
    frame_font.columnconfigure((0,1), weight=1)
    Fs_var = ctk.StringVar(value="15")
    Fs_lab = ctk.CTkLabel(frame_font, text="Fontsize",fg_color="grey", corner_radius=10, text_color="white")
    Fs_lab.grid(row=0, column=0)
    Fs = ctk.CTkEntry(frame_font, width=100, placeholder_text="15", textvariable=Fs_var)
    Fs.grid(row=0, column=1, padx=10, pady=10)


    def make_tgraph():
        global hot_csv, cold_csv, tfilename, tfig, tFs_ent
        fsize = float(tFs_ent.get())
        sig_figs = 3
        hot_path = os.path.join(saving_dir, "data", hot_csv.get())
        hot_df = pd.read_csv(hot_path)
        cold_path = os.path.join(saving_dir, "data", cold_csv.get())
        cold_df = pd.read_csv(cold_path)

        num = hot_df["Vp"] * cold_df["Vs"]
        den = hot_df["Vs"] * cold_df["Vp"]
        T = num / den
        try:
            drp = float(tRp_var.get())
            dfs = float(tFs_var.get())
        except ValueError as ve:
            messagebox.showerror("Value Error", f"R_p and Fontsize must be numbers, please check their values")
            return 0
        
        tfig, tax = plt.subplots(figsize=(3.5,3.5), dpi=100)
        tax.spines[['right', 'top']].set_visible(False)

        plt.plot(hot_df["V - Vs"], T*100, c="0", markersize=fsize-5, marker=".")

        x_max = hot_df["V - Vs"][np.argmax(T)]
        tax.vlines(x_max, 0, np.max(T)*100, color="r")
        x_max_r = round_sig(x_max, sig_figs)

        T_max_r = round_sig(round_sig(np.max(T), sig_figs) * 100, sig_figs)
        plt.text(x_max+0.1, 0, f"$V-V_s={x_max_r},\;T={T_max_r}\%$", color="r")

        plt.xticks(size=fsize-2)
        plt.yticks(size=fsize-2)
        plt.xlabel("$V-V_s$ (V)", size=fsize)
        plt.ylabel("$T\;(\%)$", size=fsize)

        plt.tight_layout()
        canvas_T = FigureCanvasTkAgg(tfig, master=tgraph_page)
        canvas_T.draw()
        canvas_T.get_tk_widget().grid(row=1,column=2,padx=10,pady=10)

        #t_filepath = os.path.join(saving_dir, "plots", tfilename.get() + ".pdf")
        #plt.savefig(t_filepath)



     # double I graph page config
    

    def save_tgraph():
        global saving_dir, tfig
        fname = tfilename.get()
        if ".pdf" not in fname:
            if "." in fname:
                messagebox.showerror("File Type Error", "Make sure to save as a '.pdf'")
                return 0
            else:
                fname += ".pdf"
        plot_dir = os.path.join(saving_dir, "plots")
        os.chdir(plot_dir)
        try:
            tfig.savefig(fname)
            messagebox.showinfo("", f"Plot saved as\n\t{fname}\nIn\n\t{plot_dir}")
        except Exception as e:
            print(e)
            messagebox.showerror("File Type Error", f"Failed to write to {fname}\nMake sure to save with a valid filename")
        os.chdir("..")
        os.chdir("..")


    tgraph_page = tabControl.add("Transmission Plot")
    tgraph_page.rowconfigure(10, weight=1)
    tgraph_page.columnconfigure(2, weight=1)

    tsettings_grid = ctk.CTkFrame(tgraph_page, corner_radius=10, width=100)
    tsettings_grid.grid(row=1, column=1, padx=20)
    tsettings_grid.rowconfigure(1, weight=1)
    tsettings_grid.columnconfigure(0, weight=1)


    tfig, tax = plt.subplots(figsize=(3.5,3.5), dpi=100)
    tax.spines[['right', 'top']].set_visible(False)
    tax.set_xlabel("$V-V_s$ $(V)$", size=15)
    tax.set_ylabel("$T$ (%)", size=15)
    tax.tick_params(axis='both', which='major', labelsize=13)
    tfig.set_layout_engine("constrained")
    canvas_T = FigureCanvasTkAgg(tfig, master=tgraph_page)
    canvas_T.draw()
    canvas_T.get_tk_widget().grid(row=1,column=2,padx=10,pady=10)


    # transmission rp
    t_frameR_P = ctk.CTkFrame(tsettings_grid,width=500,height=50,corner_radius=10)
    t_frameR_P.grid(row=0,column=0,padx=20,pady=50)
    t_frameR_P.rowconfigure(0)
    t_frameR_P.columnconfigure((0,1), weight=1)
    tRp_var = ctk.StringVar(value="1000")
    tRp_lab = ctk.CTkLabel(t_frameR_P, text="R_p:",fg_color="grey", corner_radius=10, text_color="white")
    tRp_lab.grid(row=0, column=0)
    tRp_ent = ctk.CTkEntry(t_frameR_P, width=100, placeholder_text="1000", textvariable=tRp_var)
    tRp_ent.grid(row=0, column=1, padx=10, pady=10)

    
    # fontsize
    tframe_font = ctk.CTkFrame(tsettings_grid,width=500,height=50,corner_radius=10)
    tframe_font.grid(row=1,column=0,padx=20,pady=50)
    tframe_font.rowconfigure(0)
    tframe_font.columnconfigure((0,1), weight=1)
    tFs_var = ctk.StringVar(value="15")
    tFs_lab = ctk.CTkLabel(tframe_font, text="Fontsize",fg_color="grey", corner_radius=10, text_color="white")
    tFs_lab.grid(row=0, column=0)
    tFs_ent = ctk.CTkEntry(tframe_font, width=100, placeholder_text="15", textvariable=tFs_var)
    tFs_ent.grid(row=0, column=1, padx=10, pady=10)

    tmake_frame = ctk.CTkFrame(tgraph_page, corner_radius=10, width=100)
    tmake_frame.grid(row=1, column=3, padx=20)
    tmake_frame.rowconfigure(1, weight=1)
    tmake_frame.columnconfigure(0, weight=1)

    # draw button
    make_igraph_button = ctk.CTkButton(tsettings_grid,text="Draw Graph",command=make_tgraph)
    make_igraph_button.grid(row=2,column=0,pady=10,padx=10)

    # hot csv
    hcsv_frame = ctk.CTkFrame(tmake_frame,width=500,height=50,corner_radius=10)
    hcsv_frame.grid(row=1,column=0,padx=20,pady=50)
    hcsv_frame.rowconfigure(0)
    hcsv_frame.columnconfigure((0,1), weight=1)
    hcsv_lab = ctk.CTkLabel(hcsv_frame, text="Hot csv File:",fg_color="grey", corner_radius=10, text_color="white")
    hcsv_lab.grid(row=0, column=0)
    hot_csv = StringVar()
    hot_csv.set("")
    avail_csvs = []
    hot_csv_menu = ctk.CTkOptionMenu(master=hcsv_frame, variable=hot_csv, values=avail_csvs)
    hot_csv_menu.grid(row=0, column=1, pady=10, padx=10)


    # cold csv
    ccsv_frame = ctk.CTkFrame(tmake_frame,width=500,height=50,corner_radius=10)
    ccsv_frame.grid(row=2,column=0,padx=20,pady=50)
    ccsv_frame.rowconfigure(0)
    ccsv_frame.columnconfigure((0,1), weight=1)
    ccsv_lab = ctk.CTkLabel(ccsv_frame, text="Cold csv File:",fg_color="grey", corner_radius=10, text_color="white")
    ccsv_lab.grid(row=0, column=0)
    cold_csv = StringVar()
    cold_csv.set("")
    cold_csv_menu = ctk.CTkOptionMenu(master=ccsv_frame, variable=cold_csv, values=avail_csvs)
    cold_csv_menu.grid(row=0, column=1, pady=10, padx=10)

    # file name entry
    tfilename = ctk.CTkEntry(tmake_frame, width=300,placeholder_text="filename e.g. C:/Users/student/Desktop/both.pdf")
    tfilename.grid(row=3,column=0,pady=10,padx=10)

    # make graph buttion
    tbutton_grid = ctk.CTkFrame(tmake_frame,corner_radius=10)
    tbutton_grid.grid(row=4,column=0,padx=20,pady=20)
    tbutton_grid.rowconfigure(1, weight=1)
    tbutton_grid.columnconfigure(2, weight=1)

    make_igraph_button = ctk.CTkButton(tbutton_grid,text="Save Graph",command=save_tgraph)
    make_igraph_button.grid(row=0,column=0,pady=10,padx=10)







    fig, ax = plt.subplots(figsize=(3.5,3.5), dpi=100)
    ax.spines[['right', 'top']].set_visible(False)
    ax.set_xlabel("$\sqrt{V-V_s}$ $(\sqrt{V})$", size=15)
    ax.set_ylabel("$I_p$ (A)", size=15)
    ax.tick_params(axis='both', which='major', labelsize=13)
    fig.set_layout_engine("constrained")
    canvasI_P = FigureCanvasTkAgg(fig, master=igraph_grid)
    canvasI_P.draw()
    canvasI_P.get_tk_widget().grid(row=1,column=1,padx=10,pady=10)


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

    def reset():
        global multimeterV_P, multimeterV_S, multimeterVV_S, sessionData
        ans = messagebox.askquestion(message="Are you sure you want to reset your data?")
        if ans == "yes":
            sessionData=[]

    reset_button = ctk.CTkButton(buttonGrid,text="Reset",command=reset)
    reset_button.grid(row=4, column=1)

    dropdown = ctk.CTkOptionMenu(mainPage,values=colorTheme,command=changeTheme)
    dropdown.grid(row=10,column=1)
   
    saveButton = ctk.CTkButton(saveGrid,text="Save",command=saveToFile)
    saveButton.grid(row=1,column=3,pady=10,padx=10)
   
    hc_menu = ctk.CTkOptionMenu(master=saveGrid, variable=hot_cold, values=["Hot", "Cold"])
    hc_menu.grid(row=1, column=2, pady=10, padx=10)

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