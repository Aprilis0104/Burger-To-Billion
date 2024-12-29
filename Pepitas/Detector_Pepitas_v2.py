import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import keyboard

# Variable para detener/reanudar el proceso
detener = False

# Función para alternar el estado de automatización
def toggle():
    global detener
    detener = not detener
    print("Automatización detenida" if detener else "Automatización reanudada")

# Asignar la tecla 'q' para encender/apagar
keyboard.add_hotkey('q', toggle)

paso_a_paso = False  # Habilitar modo paso a paso

pyautogui.PAUSE = 0.001


# Cargar plantillas de cada fase
plantillas = {
    "pan_inferior": cv2.imread("pan_inferior.png", 0),
    "lechuga": cv2.imread("lechuga.png", 0),
    "carne": cv2.imread("carne.png", 0),
    "queso": cv2.imread("queso.png", 0),
    "pan_pepitas": cv2.imread("pan_pepitas.png", 0),
    "pan_pepitas_queso": cv2.imread("pan_pepitas_queso.png", 0),
    "pepitas": cv2.imread("pepita_big_black.png", 0)
}

fase_actual = None

# Inicializar ORB
orb = cv2.ORB_create(nfeatures=1000)

# Extraer descriptores de plantillas
descriptores_plantillas = {}

for nombre, plantilla in plantillas.items():
    if plantilla is not None:
        keypoints, descriptors = orb.detectAndCompute(plantilla, None)
        descriptores_plantillas[nombre] = (keypoints, descriptors)
    else:
        print(f"Error: La plantilla {nombre} no se pudo cargar")

while True:
    # Si la automatización está detenida, espera hasta que se reanude
    if detener:
        pyautogui.sleep(0.1)
        continue

    # Obtener la ventana del juego (ajusta el nombre)
    ventana = gw.getWindowsWithTitle("Burger")  # Cambia el título exacto

    if ventana:
        ventana = ventana[0]
        ventana.activate()  # Asegura que esté en primer plano
        pyautogui.sleep(0.2)  # Espera breve antes de capturar
        
        x, y, ancho, alto = ventana.left, ventana.top, ventana.width, ventana.height
        #print(f"Posición ventana - x: {x}, y: {y}, ancho: {ancho}, alto: {alto}")

        # Captura solo el área de la ventana
        screenshot = pyautogui.screenshot(region=(x, y, ancho, alto))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        cv2.imwrite("captura_ventana.png", screenshot)

        x_hamburguesa = int(ancho//3)
        y_hamburguesa = int(alto//3.5)
        x_hamburguesa_ancho = int(ancho//2.82)
        y_hamburguesa_alto = int(ancho//2.82)

        # Recortar la imagen para centrarse en un área cuadrada
        screenshot = screenshot[y_hamburguesa:y_hamburguesa+y_hamburguesa_alto, x_hamburguesa:x_hamburguesa+x_hamburguesa_ancho]
        cv2.imwrite("captura_hamburguesa.png", screenshot)

    else:
        print("Ventana no encontrada")
        continue

    # Convertir la captura a escala de grises
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    keypoints_img, descriptors_img = orb.detectAndCompute(gray, None)

    mejor_fase = None
    mejor_matches = 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    for nombre, (keypoints, descriptors) in descriptores_plantillas.items():
        if descriptors is not None and descriptors_img is not None:
            matches = bf.match(descriptors, descriptors_img)
            matches = sorted(matches, key=lambda x: x.distance)

            if len(matches) > mejor_matches:
                mejor_matches = len(matches)
                mejor_fase = nombre

    if mejor_fase:
        fase_actual = mejor_fase
        #print(f"Fase detectada: {fase_actual}")
    

    # Ejecutar acciones según la fase detectada
    if fase_actual == "pan_pepitas" or fase_actual == "pan_pepitas_queso":
        repetir_busqueda = True

        while repetir_busqueda:
            screenshot = pyautogui.screenshot(region=(x, y, ancho, alto))
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            screenshot = screenshot[y_hamburguesa:y_hamburguesa+y_hamburguesa_alto, x_hamburguesa:x_hamburguesa+x_hamburguesa_ancho]

            # Convertir la captura a escala de grises
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            # Aplicar desenfoque para reducir ruido
            gris_suavizado = cv2.GaussianBlur(gray, (5, 5), 0)

            # Umbral adaptativo (ajusta para resaltar pepitas)
            _, umbral = cv2.threshold(gris_suavizado, 200, 255, cv2.THRESH_BINARY)


            # Operaciones morfológicas (expansión y reducción de áreas)
            kernel = np.ones((3, 3), np.uint8)

            # Dilatar para expandir áreas pequeñas
            dumbral_dilatada = cv2.dilate(umbral, kernel, iterations=2)

            # Erosionar para restaurar forma y eliminar ruido
            umbral_erosionada = cv2.erode(dumbral_dilatada, kernel, iterations=1)
            cv2.imwrite("filtro.png", umbral_erosionada)
            # Encontrar contornos
            contornos, _ = cv2.findContours(umbral_erosionada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Umbral de área para filtrar pepitas grandes
            area_maxima = 100  # Ajusta este valor según el tamaño típico de las pepitas

            contornos_filtrados = [c for c in contornos if cv2.contourArea(c) <= area_maxima]
            # Dibujar solo pepitas que cumplan con el área
            if contornos_filtrados:
                for contorno in contornos_filtrados: 
                    x_pepita, y_pepita, w_pepita, h_pepita = cv2.boundingRect(contorno)
                    pyautogui.click((int(x_pepita)+int(w_pepita//2)) + x_hamburguesa + x, (int(y_pepita)+int(h_pepita//2)) + y_hamburguesa + y)
            else:
                repetir_busqueda = False

        pyautogui.click(x+ancho//2, y+alto//2)  # Retirar hamburguesa
        #print("Hamburguesa retirada")
        
        for i in range(5):
                pyautogui.click(x+ancho//4*3, y+alto//5*2)  # Aumentar probabilididad queso
            
    else:
        pyautogui.click(x+ancho//2, y+alto//2)
        #print("Avanzando en la construcción de la hamburguesa")
    
    # Salir del bucle al presionar 'esc'
    if keyboard.is_pressed('esc'):
        print("Saliendo...")
        break