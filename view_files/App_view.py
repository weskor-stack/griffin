import customtkinter as ctk
from PIL import Image

def frameView():
    # Configuración inicial
    ctk.set_appearance_mode("dark") # Modo de apariencia: system, light, dark
    ctk.set_default_color_theme("dark-blue") # Tema de color: blue, dark-blue, green
    # Crear la ventana principal
    root = ctk.CTk()
    width = root.winfo_screenwidth()
    height= root.winfo_screenheight()
    root.geometry("%dx%d" % (width, height))

    #root.geometry("1930x1200")
    root.title("Store Data")
    # root.iconbitmap("favicon.ico")

    # Crear frame principal
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=30, padx=60, fill="both", expand=True)


    # Crear los componentes
    # Showing the label
    lbl_station = ctk.CTkLabel(master=frame, text='Station:')
    lbl_station.pack(side=ctk.LEFT, pady=10, padx=80, anchor='nw')
    #lbl_station.place(x=80, y=10)

    entry_station = ctk.CTkEntry(master=frame, width=300, justify="center")
    entry_station.pack(side=ctk.LEFT, pady=10, padx=0, anchor='nw')
    #entry_station.place(x=140, y=10)

    lbl_model = ctk.CTkLabel(master=frame, text='Model:')
    lbl_model.pack(side=ctk.LEFT, pady=10, padx=50, anchor='n')
    #lbl_model.place(x=550, y=10)

    entry_model = ctk.CTkEntry(master=frame, width=300, justify="center")
    entry_model.pack(side=ctk.LEFT, pady=10, padx=0, anchor='n')
    #entry_model.place(x=600, y=10)
    
    lbl_ip_address = ctk.CTkLabel(master=frame, text='IP Address:')
    lbl_ip_address.pack(side=ctk.LEFT, pady=10, padx=50, anchor='ne')
    #lbl_ip_address.place(x=1080, y=10)

    entry_ip_address = ctk.CTkEntry(master=frame, width=110, justify="center")
    entry_ip_address.pack(side=ctk.LEFT, pady=10, padx=5, anchor='ne')
    #entry_ip_address.place(x=1160, y=10)

    lbl_union = ctk.CTkLabel(master=frame, text=':')
    lbl_union.pack(side=ctk.LEFT, pady=10, padx=0, anchor='ne')
    #lbl_union.place(x=1273, y=10)

    entry_port = ctk.CTkEntry(master=frame, width=50, justify="center")
    entry_port.pack(side=ctk.LEFT, pady=10, padx=5, anchor='ne')
    #entry_port.place(x=1280, y=10)

    lbl_piece = ctk.CTkLabel(master=frame, text='Piece:')
    lbl_piece.place(x=550, y=60)

    entry_piece = ctk.CTkEntry(master=frame, width=300, justify="center")
    entry_piece.place(x=640, y=60)

    lbl_comand = ctk.CTkLabel(master=frame, text='Command:')
    lbl_comand.place(x=700, y=150)

    # Load the image 
    image_green = ctk.CTkImage(light_image=Image.open('./images/verde.png'),
                                      dark_image=Image.open('./images/verde.png'),
                                      size=(30, 30))
    image_red = ctk.CTkImage(light_image=Image.open('./images/rojo.png'),
                                      dark_image=Image.open('./images/rojo.png'),
                                      size=(30, 30))

    green_label = ctk.CTkLabel(master=frame, image=image_green, text="")
    green_label.place(x=780, y=150)

    pass_label = ctk.CTkLabel(master=frame, text="Pass")
    pass_label.place(x=820, y=150)

    red_label = ctk.CTkLabel(master=frame, image=image_red, text="")
    red_label.place(x=870, y=150)

    fail_label = ctk.CTkLabel(master=frame, text="Fail")
    fail_label.place(x=910, y=150)

    button_hide = ctk.CTkButton(master=frame, text="Hide", width=80)
    button_hide.place(x=800, y=200)

    lbl_history = ctk.CTkLabel(master=frame, text='History:')
    lbl_history.place(x=80, y=300)

    ################################################ Logos ######################################################

    image_tesla = ctk.CTkImage(light_image=Image.open('./images/tesla.png'),
                                      dark_image=Image.open('./images/tesla.png'),
                                      size=(150, 150))

    image_amc = ctk.CTkImage(light_image=Image.open('./images/amc.png'),
                                      dark_image=Image.open('./images/amc.png'),
                                      size=(200, 90))

    tesla_label = ctk.CTkLabel(master=frame, image=image_tesla, text="")
    tesla_label.place(x=1070, y=600)

    amc_label = ctk.CTkLabel(master=frame, image=image_amc, text="")
    amc_label.place(x=1210, y=650)

    #############################################################################################################

    #entry_model.place_forget()

    ############################################# Buttons ########################################################

    button_model = ctk.CTkButton(master=frame, text="Model", width=80)
    button_model.place(x=1200, y=200)

    button_recipe = ctk.CTkButton(master=frame, text="Recipe", width=80)
    button_recipe.place(x=1300, y=200)

    button_tcp = ctk.CTkButton(master=frame, text="TCP/IP", width=80)
    button_tcp.place(x=1200, y=250)

    label_user = ctk.CTkLabel(master=frame, text="User:")
    label_user.place(x=1300, y=250)

    label_users = ctk.CTkLabel(master=frame, text="Admin")
    label_users.place(x=1340, y=250)

    button_export = ctk.CTkButton(master=frame, text="Export", width=80)
    button_export.place(x=1200, y=300)

    ##############################################################################################################

    root.mainloop()

if __name__ == "__main__":
    app = frameView()