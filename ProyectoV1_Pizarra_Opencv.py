import cv2
import mediapipe as mp
import math
import time
import numpy as np


import pyautogui
import keyboard

# utiliza la funcionalidad de la camara para obtener la entrada del mundo fisico
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)


# Dibujo
mpDibujo = mp.solutions.drawing_utils
ConfDibujo = mpDibujo.DrawingSpec(thickness=1, circle_radius=1)


# mientras se este ejecutando el programa, se obtiene estos datos
flag = True
# para escalar a la pantalla
screen_w, screen_h = pyautogui.size()

# --------------------
# Variables y banderas Para la movilizacion de los ojos
# --------------------
finalT = 0
inicioT = 0
# indica si se Parpadeo antes
Parpadeo = False
# indica si la posicion del ojo derecho es la primera
primeraPasada = True


# --------------------
# Metodos y banderas para el dibujo en lienzo
# --------------------
def draw(event, xN, yN, flags, params):
    # variables globales
    # global blink
    global dibujando, xP, yP

    if dibujando:
        if xP == None:
            xP, yP = xN, yN
            return
        else:
            # cv2.circle(imAux, (xN, yN), 3, (0), -1)
            cv2.line(imAux, (xP, yP), (xN, yN), (0), 2)
            xP, yP = xN, yN


# inicializa el canva
xP, yP = None, None

dibujando = False
cv2.namedWindow('imAux')
imAux = np.zeros((500, 800, 3), dtype='float64')
imAux.fill(255)

# cv2.rectangle(imAux, (300, 0), (400, 50), (0, 0, 0), 1)
# cv2.putText(imAux, 'Limpiar', (320, 20), 6, 0.6,
#             (0, 0, 0), 1, cv2.LINE_AA)
# cv2.putText(imAux, 'pantalla', (320, 40), 6, 0.6,
#             (0, 0, 0), 1, cv2.LINE_AA)
cv2.setMouseCallback('imAux', draw)


while flag:
    # Si se presiona q o esc, se termina el programa
    if keyboard.is_pressed("q") or keyboard.is_pressed("Esc"):
        flag = False

    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_Frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    output = face_mesh.process(rgb_Frame)
    landmark_points = output.multi_face_landmarks

    # obtiene la altura del marco, para enfocarse en una parte dentro de ese espacio
    frame_h, frame_w, _ = frame.shape

    # si existe un rostro al que rastrear
    if (landmark_points):

        landmarks = landmark_points[0].landmark

        # Obtiene el punto medio del iris
        X_posiris = int((((landmarks[474].x)+(landmarks[476].x))/2) * frame_w)
        Y_posIris = int((((landmarks[475].y)+(landmarks[477].y))/2) * frame_h)

        screen_X = int((((landmarks[474].x)+(landmarks[476].x))/2) * screen_w)
        screen_Y = int((((landmarks[475].y)+(landmarks[477].y))/2) * screen_h)

        # Se inicializa la primera posicion del centro del ojo
        if (primeraPasada):

            # Convierte a String luego a int para separar los punteros
            str_X = str(int(
                (((landmarks[474].x)+(landmarks[476].x))/2) * screen_w))
            str_Y = str(int(
                (((landmarks[475].y)+(landmarks[477].y))/2) * screen_h))

            screenInicial_X = int(str_X)
            screenInicial_Y = int(str_Y)
            primeraPasada = False

        # Controla el desplazamiento del puntero
        # escalando la diferencia de la posicion actual con
        # la nueva posicion del Iris
        alpha_X = int((screenInicial_X - screen_X)*1.5)
        alpha_Y = int((screenInicial_Y - screen_Y)*3)

        pyautogui.moveTo(screenInicial_X - alpha_X, screenInicial_Y - alpha_Y)

        # print('Centro    ', screenInicial_X, screenInicial_Y)

        # Imprime el centro del Iris
        cv2.circle(frame, (X_posiris, Y_posIris), 3, (255, 255, 0))

        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)

            cv2.circle(frame, (x, y), 3, (0, 255, 0))

        # pyautogui.moveTo(631680, 355320)
        # Permite salir del programa si se ejecuta por 4 seg

        # ---------------------
        # ojo der
        # ---------------------
        right = [landmarks[145], landmarks[159]]
        for landmark in right:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)

            cv2.circle(frame, (x, y), 3, (0, 255, 255))

        # Longitud entre el punto mas alto del ojo izquierdo con el mas bajo
        longitud_Der = right[0].y - right[1].y

        # ---------------------
        # ojo izq
        # ---------------------
        left = [landmarks[374], landmarks[386]]
        for landmark in left:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)

            cv2.circle(frame, (x, y), 3, (0, 0, 255))
        # Longitud entre el punto mas alto del ojo izquierdo con el mas bajo
        longitud_Izq = left[0].y - left[1].y

        # ------------------------------------
        # ------------------------------------
        # Funciones con Parpadeo
        # ------------------------------------
        # ------------------------------------

        # Verifica que ambos ojos esten cerrados
        # Detecta si se ha parpadeado, tomando un tiempo inicial
        if (longitud_Der < 0.01) and (longitud_Izq < 0.01) and Parpadeo == False:
            Parpadeo = True
            inicioT = time.time()
            print('hubo parpadeo')

        # Detecta si se dejo de parpadear, tomando un tiempo final
        elif (longitud_Der >= 0.01) and (longitud_Izq >= 0.01) and Parpadeo == True:
            Parpadeo = False
            finalT = time.time()

        # Se obtiene el tiempo de Parpadeo, restando los tiempos cronometrados
        tiempo = round(finalT-inicioT, 0)

        # Si se parpadeo por mas de 4 segundos, el programa termina
        if tiempo >= 4:
            cv2.imwrite("Imagenes_pizarra\dibujo.jpg", imAux)
            flag = False

        # Si se Parpadeo entre 2 y 4 segundos, se considera una nueva posicion inical
        # del Iris
        if 2 <= tiempo and tiempo < 4:
            primeraPasada = True
            inicioT = 0
            finalT = 0

        print('tiempoInic  ', inicioT, '   tiempoFinal', finalT, "    X Y   ",
              screenInicial_X, "   ", screenInicial_Y)

        # ojos Invertidos

        if (longitud_Der < 0.01) and (longitud_Izq > 0.01):
            if (dibujando):
                dibujando = False
                xP, yP = None, None
                # pinta del color del lienzo, para borrar la palabra "dibujando"
                cv2.putText(imAux, 'Dibujando', (700, 20), 6, 0.6,
                            (255, 255, 255), 1, cv2.LINE_AA)
            else:
                dibujando = True
                # Indica al usuario que se esta "dibujando"
                cv2.putText(imAux, 'Dibujando', (700, 20), 6, 0.6,
                            (0, 0, 255), 1, cv2.LINE_AA)
            time.sleep(0.5)

    cv2.imshow('Eye Controlled Mouse', frame)
    cv2.imshow('imAux', imAux)
    cv2.waitKey(1)

# if tiempo >= 4:
    # cv2.putText(frame, 'Se detuvo el programa al parpadear por al menos 4 seg',
    #             cv2.FONT_HERSHEY_SIMPLEX, 1)
