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

paso_a_paso = True  # Habilitar modo paso a paso

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

#pepitas_ampliada = cv2.resize(plantillas['pepitas'], (plantillas['pepitas'].shape[1]*2, plantillas['pepitas'].shape[0]*2))
#plantillas['pepitas'] = cv2.resize(plantillas['pepitas'], (60, 120), interpolation=cv2.INTER_CUBIC)

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
        continue

    # Obtener la ventana del juego (ajusta el nombre)
    ventana = gw.getWindowsWithTitle("Burger")  # Cambia el título exacto

    if ventana:
        ventana = ventana[0]
        ventana.activate()  # Asegura que esté en primer plano
        pyautogui.sleep(0.5)  # Espera breve antes de capturar
        
        x, y, ancho, alto = ventana.left, ventana.top, ventana.width, ventana.height
        print(f"Posición ventana - x: {x}, y: {y}, ancho: {ancho}, alto: {alto}")

        # Captura solo el área de la ventana
        screenshot = pyautogui.screenshot(region=(x, y, ancho, alto))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        cv2.imwrite("captura_ventana.png", screenshot)

        x_hamburguesa = 280
        y_hamburguesa = 160
        x_hamburguesa_ancho = 300
        y_hamburguesa_alto = 300

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

            #resultado = cv2.drawMatches(plantillas[nombre], keypoints, screenshot, keypoints_img, matches[:10], None, flags=2)
            #cv2.imshow(f"Resultado {nombre}", resultado)
            #cv2.waitKey(1000)

    if mejor_fase:
        fase_actual = mejor_fase
        print(f"Fase detectada: {fase_actual}")



    '''
    # Detección de fase
    #for nombre, template in list(plantillas.items())[:-1]:
    #    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    #    if np.max(res) > 0.8:
    ##        fase_actual = nombre
    #        print(f"Fase detectada: {fase_actual}")
    #        break

    for nombre, template in plantillas.items():
        if template is None:
            print(f"Error: La plantilla {nombre} no se pudo cargar")

        template = cv2.resize(template, (screenshot.shape[1], screenshot.shape[0]))

        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)

        resultado = screenshot.copy()
        loc = np.where(res >= 0.7)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(resultado, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 2)
        cv2.imshow(f"Resultado {nombre}", resultado)
        cv2.waitKey(5000)

        if np.max(res) > 0.8:
            fase_actual = nombre
            print(f"Fase detectada: {fase_actual}")
            break
    '''

    # Mostrar en tiempo real lo que "ve" el bot
    #cv2.imshow("Vista en tiempo real", screenshot)
    #cv2.waitKey(500)  # Mostrar la ventana durante medio segundo
    

    # Ejecutar acciones según la fase detectada
    if fase_actual == "pan_pepitas" or fase_actual == "pan_pepitas_queso":
        print(f"Detectada fase: {fase_actual}. Buscando pepitas...")
        gray = gray[0:200,:]
        #cv2.imshow("Pepita", plantillas['pepitas'])
        #cv2.imshow("Captura", gray)
        #cv2.waitKey(5000)
        cv2.destroyAllWindows()

        # Aplicar ORB para encontrar pepitas
        orb = cv2.ORB_create(nfeatures=1500)
        keypoints1, descriptors1 = orb.detectAndCompute(gray, None)

        # Escalar y buscar con diferentes versiones de la plantilla de pepitas
        matches_totales = []
        for escala in [1.0, 1.2]:
            plantilla_escalada = cv2.resize(plantillas['pepitas'], None, fx=escala, fy=escala)
            keypoints2, descriptors2 = orb.detectAndCompute(plantilla_escalada, None)

            if descriptors1 is None or descriptors2 is None:
                print(f"No se detectaron descriptores en escala {escala}")
                continue

            # Comparador de fuerza bruta
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(descriptors1, descriptors2)
            matches_totales.extend(matches)  # Acumular todos los matches

        # Verificar que se hayan detectado descriptores
        if descriptors1 is None or descriptors2 is None:
            print("No se detectaron descriptores en una de las imágenes.")
            continue

        # Asegurar que los descriptores sean del mismo tipo
        if descriptors1.dtype != descriptors2.dtype:
            descriptors1 = descriptors1.astype(np.uint8)
            descriptors2 = descriptors2.astype(np.uint8)

        '''
        # Comparador de fuerza bruta para encontrar coincidencias
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors1, descriptors2)
        matches = sorted(matches, key=lambda x: x.distance)
        '''
        '''
        resultado = cv2.drawMatches(screenshot, keypoints1, plantillas['pepitas'], keypoints2, matches[:20], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imshow("Coincidencias de Pepitas", resultado)
        cv2.waitKey(1000)  # Mostrar por 1 segundo
        '''
        if paso_a_paso:
            input("Presiona Enter para continuar con el siguiente paso...")

        cv2.destroyAllWindows()

         # Click en las pepitas
        for match in matches:
            x_pepita, y_pepita = keypoints1[match.queryIdx].pt
            cv2.circle(screenshot, (int(x_pepita), int(y_pepita)), 10, (0, 255, 0), 2)
            pyautogui.click(int(x_pepita) + x_hamburguesa + x, int(y_pepita) + y_hamburguesa + y)
            print(f"Click en pepita: ({int(x_pepita)}, {int(y_pepita)})")
            pyautogui.sleep(0.1)

        cv2.imwrite("resultado_deteccion.png", screenshot)

        cv2.imshow("Vista en tiempo real", screenshot)
        cv2.waitKey(1000)  # Mostrar por 1 segundo
        
        if paso_a_paso:
            input("Presiona Enter para continuar con el siguiente paso...")

        pyautogui.click(x+ancho//2, y+alto//2)  # Retirar hamburguesa
        print("Hamburguesa retirada")
        '''
        keypoints_pepitas, descriptors_pepitas = orb.detectAndCompute(plantillas['pepitas'], None)
        matches = bf.match(descriptors_pepitas, descriptors_img)

        loc = [keypoints_img[m.trainIdx].pt for m in matches]

        for pt in loc:
            cv2.circle(screenshot, (int(pt[0]), int(pt[1])), 10, (0, 255, 0), 2)
            print("Click en pepita en:", pt)
            pyautogui.click(int(pt[0]) + x, int(pt[1]) + y)

        pyautogui.click(x+ancho//2, y+alto//2)  # Retirar hamburguesa
        print("Hamburguesa retirada")
        '''
    else:
        pyautogui.click(x+ancho//2, y+alto//2)
        print("Avanzando en la construcción de la hamburguesa")
    '''
    if fase_actual == "pan_pepitas" or fase_actual == "pan_pepitas_queso":
        # Buscar pepitas solo en la última fase
        res = cv2.matchTemplate(gray, plantillas['pepitas'], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.8)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(screenshot, pt, (pt[0], pt[1]), (0, 255, 0), 2)
            cv2.imshow("Vista en tiempo real", screenshot)
            cv2.waitKey(500)  # Mostrar la ventana durante medio segundo
            #pyautogui.click(pt[0] + ancho//2, pt[1] + alto//2)
            print("Click en pepita en:", pt)
            if paso_a_paso:
                input("Presiona Enter para continuar...")
        pyautogui.click(460, 400)  # Retirar hamburguesa
        print("Hamburguesa retirada")
    else:
        pyautogui.click(460, 400)  # Avanzar en construcción
        print("Avanzando en la construcción de la hamburguesa")
    '''
    # Salir del bucle al presionar 'esc'
    if keyboard.is_pressed('esc'):
        print("Saliendo...")
        break
