import cv2
import numpy as np

# Cargar captura
captura = cv2.imread("captura_hamburguesa.png")

# Convertir a escala de grises
gris = cv2.cvtColor(captura, cv2.COLOR_BGR2GRAY)

# Aplicar desenfoque para reducir ruido
gris_suavizado = cv2.GaussianBlur(gris, (5, 5), 0)

# Umbral adaptativo (ajusta los valores para resaltar las pepitas)
_, umbral = cv2.threshold(gris_suavizado, 200, 255, cv2.THRESH_BINARY)

# Mostrar imagen umbralizada (solo pepitas en blanco)
cv2.imshow("Imagen Umbralizada", umbral)

# Operaciones morfológicas (expansión y reducción de áreas)
kernel = np.ones((3, 3), np.uint8)

# Dilatar para expandir áreas pequeñas
dumbral_dilatada = cv2.dilate(umbral, kernel, iterations=2)
cv2.imshow("Dilatada", dumbral_dilatada)

# Erosionar para restaurar forma y eliminar ruido
umbral_erosionada = cv2.erode(dumbral_dilatada, kernel, iterations=1)
cv2.imshow("Erosionada", umbral_erosionada)

# Encontrar contornos (las pepitas aparecerán como áreas blancas)
contornos, _ = cv2.findContours(umbral_erosionada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Umbral de área para filtrar pepitas grandes
area_maxima = 100  # Ajusta este valor según el tamaño típico de las pepitas

# Dibujar contornos en la imagen original
for contorno in contornos:
    area = cv2.contourArea(contorno)
    if area <= area_maxima:  # Filtrar pepitas grandes
        x, y, w, h = cv2.boundingRect(contorno)
        cv2.rectangle(captura, (x, y), (x+w, y+h), (0, 255, 0), 2)
        print(f"Pepita encontrada en: x={x}, y={y}, área={area}")
    else:
        print(f"Pepita descartada por área: {area}")

# Mostrar resultados
cv2.imwrite("captura_gris.png", umbral)
cv2.imwrite("captura_dilatada.png", dumbral_dilatada)
cv2.imwrite("captura_erosionada.png", umbral_erosionada)
cv2.imwrite("captura_verde.png", captura)

cv2.imshow("Pepitas Detectadas", captura)
cv2.waitKey(0)
cv2.destroyAllWindows()