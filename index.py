import cv2
from PIL import Image as img, ImageDraw, ImageFont
import os, glob
from alive_progress import alive_bar 
import threading
import customtkinter
from customtkinter import filedialog
from CTkColorPicker import *



text = """
    _   ___  ___ ___ ___  __   _____ ___  ___ ___  
   /_\ / __|/ __|_ _|_ _| \ \ / /_ _|   \| __/ _ \ 
  / _ \\__ \ (__ | | | |   \ V / | || |) | _| (_) |
 /_/ \_\___/\___|___|___|   \_/ |___|___/|___\___/ 
                                                   
"""                                                                                      
print(text)
carpeta_destino_video = ""
video_path = ""
fontColor = "Black"
backgroundColor = "White"

def ask_font_color():
    global fontColor
    pick_color = AskColor() # open the color picker
    fontColor = pick_color.get() # get the color string
    if fontColor != None:
        buttonFontColor.configure(fg_color=fontColor)
    
def ask_background_color():
    global backgroundColor
    pick_color = AskColor() # open the color picker
    backgroundColor = pick_color.get() # get the color string
    if backgroundColor != None:
        buttonBackgroundColor.configure(fg_color=backgroundColor)    
        
def estructuraContenido():
    if not os.path.exists("fotogramas"):
        os.makedirs("fotogramas")
    if not os.path.exists("ASCII"):
        os.makedirs("ASCII")
    if not os.path.exists("fotogramasASCII"):
        os.makedirs("fotogramasASCII")
        
def borrarContenido():
    #borra el contenido de las carpetas fotogramas y ascii
    dir = 'fotogramas'
    for file in os.scandir(dir):
        os.remove(file.path)
    dir = 'ASCII'
    for file in os.scandir(dir):
        os.remove(file.path)
    dir = 'fotogramasASCII'
    for file in os.scandir(dir):
        os.remove(file.path)
    
#-------------------------------------------------------------------------- 

def selectVideo():
    global video_path
    video_path = filedialog.askopenfilename()
    label.configure(text = video_path, text_color="#a3be8c" )
    
    
def selectFolder():
    global carpeta_destino_video
    carpeta_destino_video = filedialog.askdirectory()
    label2.configure(text = carpeta_destino_video, text_color="#a3be8c" ) 
    
#--------------------------------------------------------------------------

def crear_imagen_desde_txt(txt_path, imageName):
    
    
    with open(txt_path, "r") as archivo_txt:
        lineas = archivo_txt.readlines()

    # Obtener el ancho y alto de la imagen desde las dimensiones del texto
    ancho = len(lineas[0].strip())
    alto = len(lineas)

    # Tamaño de cada carácter en la imagen
    tamano_caracter = 10

    # Crear una nueva imagen RGB
    nueva_imagen = img.new("RGB", (ancho * tamano_caracter, alto * tamano_caracter), backgroundColor)
    draw = ImageDraw.Draw(nueva_imagen)

    # Utilizar una fuente mono-espaciada para que los caracteres se alineen correctamente
    fuente = ImageFont.load_default()

    # Dibujar los caracteres en la imagen
    for y, linea in enumerate(lineas):
        for x, caracter in enumerate(linea.strip()):
            posicion = (x * tamano_caracter, y * tamano_caracter)
            draw.text(posicion, caracter, font=fuente, fill=fontColor)

    # Guardar la imagen
    nueva_imagen.save(imageName)

    #print(f"Imagen generada y guardada como {imageName}")

#--------------------------------------------------------------------------   
    
def convertir_a_ascii(imagen_path, ancho_ascii=100):
    # Cargar la imagen
    imagen = img.open(imagen_path)

    # Redimensionar la imagen si es necesario
    ratio = ancho_ascii / float(imagen.size[0])
    alto_ascii = int(float(imagen.size[1]) * float(ratio))
    imagen = imagen.resize((ancho_ascii, alto_ascii))

    # Convertir a escala de grises
    imagen_gris = imagen.convert("L")

    # Obtener los caracteres ASCII según la intensidad de cada píxel
    caracteres_ascii = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", ""]
    pixeles = imagen_gris.getdata()
    caracteres = [caracteres_ascii[pixel // 25] for pixel in pixeles]
    caracteres = ''.join(caracteres)

    # Dividir los caracteres en líneas
    caracteres_divididos = [caracteres[i:i+ancho_ascii] for i in range(0, len(caracteres), ancho_ascii)]
    ascii_art = "\n".join(caracteres_divididos)

    return ascii_art

#--------------------------------------------------------------------------

def dividir_en_fotogramas(video_path, carpeta_destino):
    global progress
    # Abrir el video
    video = cv2.VideoCapture(video_path)

    # Verificar si el video se abrió correctamente
    if not video.isOpened():
        print("Error al abrir el video.")
        return

    # Obtener información del video
    fps = int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Crear la carpeta de destino si no existe
    import os
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Leer y guardar cada fotograma
    p = "Generating video ◻"
    progressbar.configure(text = p, text_color="#b48ead")
    with alive_bar(total_frames) as bar:
        for frame_numero in range(total_frames):
            ret, frame = video.read()
            if not ret:
                print(f"Error al leer el fotograma {frame_numero}.")
                break

            # Guardar el fotograma en la carpeta de destino
            nombre_fotograma = f"{carpeta_destino}/frame_{frame_numero:04d}.png"
            cv2.imwrite(nombre_fotograma, frame)

            ascii_art = convertir_a_ascii(f"{carpeta_destino}/frame_{frame_numero:04d}.png")

            # Guardar o imprimir el arte ASCII
            with open(f"ASCII/ascii_art_{frame_numero:04d}.txt", "w") as archivo:
                archivo.write(ascii_art)

            #print(f"fotograma {frame_numero:04d} ASCII convertido")
            
            crear_imagen_desde_txt(f"ASCII/ascii_art_{frame_numero:04d}.txt", f"fotogramasASCII/img{frame_numero:04d}.png")
            
            if p == "Generating video ◻":
                p = "Generating video ◻◻"
            elif p == "Generating video ◻◻":
                p = "Generating video ◻◻◻"
            else:
                p="Generating video ◻"
                
            progressbar.configure(text = p, text_color="#b48ead")
            
            bar()
          
    # Cerrar el video
    video.release()

    #print(f"Se han guardado {total_frames} fotogramas.")

#--------------------------------------------------------------------------

def generar_video(desde_carpeta, formato_imagen, fps, nombre_video):
    imagenes = [img for img in os.listdir(desde_carpeta) if img.endswith(formato_imagen)]

    # Verificar si hay imágenes en la carpeta
    if not imagenes:
        print("No se encontraron imágenes en la carpeta especificada.")
        return

    # Ordenar las imágenes por su número (si siguen el formato esperado)
    imagenes.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

    # Obtener el tamaño de la primera imagen
    img_path = os.path.join(desde_carpeta, imagenes[0])
    img = cv2.imread(img_path)
    
    # Verificar si la imagen se cargó correctamente
    if img is None:
        print(f"Error al cargar la imagen: {img_path}")
        return

    height, width, _ = img.shape

    # Especificar el formato del video (en este caso, XVID)
    formato_video = cv2.VideoWriter_fourcc(*'mp4v')

    # Crear el objeto VideoWriter
    video = cv2.VideoWriter(nombre_video, formato_video, fps, (width, height))
    p = "Saving video ◻"
    progressbar.configure(text = p, text_color="#b48ead")
    for imagen in imagenes:
        img_path = os.path.join(desde_carpeta, imagen)
        frame = cv2.imread(img_path)
        
        if p == "Saving video ◻":
                p = "Saving video ◻◻"
        elif p == "Saving video ◻◻":
                p = "Saving video ◻◻◻"
        else:
                p="Saving video ◻"
                
        progressbar.configure(text = p)
        
        # Verificar si el fotograma se cargó correctamente
        if frame is not None:
            # Agregar el fotograma al video
            video.write(frame)
        else:
            print(f"Error al cargar el fotograma: {img_path}")

    # Cerrar el objeto VideoWriter
    video.release()
    progressbar.configure(text = "Video created :)", text_color="#a3be8c")
    #print(f"Video '{nombre_video}' generado con éxito.")

#--------------------------------------------------------------------------

def crear_video():
    try:
        #Si está marcado el checkbox no se borra el contenido generado en la ultima carga ni se vulven
        # a generar imagenes ni txt
        reprocess = str(previous_video_reprocess_check_var.get())
        #print(reprocess)
        global carpeta_destino_video
        global video_path 
        if reprocess == "off":
            borrarContenido()
           
            carpeta_destino = "fotogramas"
            dividir_en_fotogramas(video_path, carpeta_destino)
          
        carpeta_imagenes = "fotogramasASCII/"
        formato_imagen = ".png"  #Formato imagenes
        fps = 30  # Fotogramas por segundo
        nombre_video = f"{carpeta_destino_video}/video_generado.mp4"
        generar_video(carpeta_imagenes, formato_imagen, fps, nombre_video)
    except:
        print("Error")



def app():
      try:
            estructuraContenido()
            #print("Starting in ",timeSleep," seconds")
            thread1 = threading.Thread(target=crear_video)
            thread1.start()
            print("Started")
      except:
            print("Error")
            

#Tkinter
customtkinter.set_appearance_mode("dark")  # Modes: system (default),light , dark
customtkinter.set_default_color_theme("theme.json")
app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("500x400")
app.configure(bg="#red")
app.resizable(width = False, height = False)
app.title("ASCIIVIDEO")

buttonExport = customtkinter.CTkButton(master=app, text="Export",text_color="black", command=app,  font=('System', 16, "bold"), corner_radius=0)
buttonExport.place(x=10, y=360)

buttonSelectVideo = customtkinter.CTkButton(master=app, text="Load video",text_color="black", command=selectVideo,  font=('System', 16, "bold"),corner_radius=0)
buttonSelectVideo.place(x=10, y=280)
label = customtkinter.CTkLabel(app, text="Select video", fg_color="transparent", text_color="#bf616a",  font=('System', 16, "bold"))
label.place(x = 170, y=280)

buttonSelectFolder = customtkinter.CTkButton(master=app, text="Select folder",text_color="black", command=selectFolder,  font=('System', 16, "bold"), corner_radius=0)
buttonSelectFolder.place(x=10, y=320)
label2 = customtkinter.CTkLabel(app, text="Select folder", fg_color="transparent",text_color="#bf616a",  font=('System', 16, "bold"))
label2.place(x=170, y=320)

labelTitulo1 =  customtkinter.CTkLabel(app, text="""
        _      ___   ___ ___ ___   __      ____  ___   ___  ___    
      /_\  /  __|/  __|_  _|_  _|  \   \  /  /_  _|      \|  __/   _  \  
    /  _  \\__  \   (__  |  |  |  |       \  V  /  |  |  |  |)   |  _|    (_)  |
  /_/  \_\___/\___|___|___|      \_/  |___|___/  |___\___/  
                                                                                                      
""", fg_color="transparent",text_color="#bf616a",justify="left",corner_radius=0)
labelTitulo1.place(x=10, y=10)

previous_video_reprocess_check_var = customtkinter.StringVar(value="on")
previous_video_reprocess_checkbox = customtkinter.CTkCheckBox(app, text="reprocess previous video",text_color="white", font=('System', 16, "bold"),corner_radius=0,
                                     variable=previous_video_reprocess_check_var, onvalue="on", offvalue="off")
previous_video_reprocess_checkbox.place(x=10, y=160)

buttonFontColor = customtkinter.CTkButton(master=app, text="Font color", text_color="black", command=ask_font_color, font=('System', 16, "bold"),corner_radius=0)
buttonFontColor.place(x=10, y=240)

buttonBackgroundColor = customtkinter.CTkButton(master=app, text="Background color", text_color="black", font=('System', 16, "bold"), command=ask_background_color,  corner_radius=0)
buttonBackgroundColor.place(x=10, y=200)

progressbar = customtkinter.CTkLabel(app,text=" ", fg_color="transparent",text_color="#b48ead",  font=('System', 16, "bold"))
progressbar.place(x=350, y=43)
app.mainloop()