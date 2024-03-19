#!/usr/bin/env python3
"""
Llegeix el sector indicat a la variable sector amb la clau per defecte FFFFFF

readExtended.py
Quim Delgado
"""


import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal

def fi_de_la_lectura(signal, frame):
    global continuar_lectura
    continuar_lectura = False
    print("Capturat Ctrl+C, acabant lectura.")

def detectar_targeta(lector):
    print("Apropa la targeta...")
    while continuar_lectura:
        (status, _) = lector.MFRC522_Request(lector.PICC_REQIDL)
        if status == lector.MI_OK:
            print("Targeta detectada")
            return True
    return False

def llegir_targeta(lector, sector):
    (status, uid) = lector.MFRC522_Anticoll()
    if status == lector.MI_OK:
        print("UID de la targeta: " + str(uid))
        return lector.MFRC522_Read(sector)
    else:
        print("No s'ha pogut llegir l'UID de la targeta")
        return None

def autenticar(lector, sector, clau, uid):
    status = lector.MFRC522_SelectTag(uid)
    if status != lector.MI_OK:
        print("Error en seleccionar la targeta")
        return False
    status = lector.MFRC522_Auth(lector.PICC_AUTHENT1A, sector, clau, uid)
    if status != lector.MI_OK:
        print(f"Autenticació del sector {sector} fallida")
        return False
    return True

def imprimir_dades(sector, dades):
    if dades:
        dades_text = ''.join(chr(x) for x in dades if 32 <= x < 127)
        print(f"Dades del bloc {sector} en text pla (si és convertible): " + dades_text)
        dades_hex = ' '.join(f'{x:02X}' for x in dades)
        print(f"Dades del bloc {sector} en format hexadecimal: " + dades_hex)
    else:
        print(f"No s'han pogut llegir dades del bloc {sector}")

def neteja():
    print("Netejant recursos...")
    GPIO.cleanup()

# Programa principal
if __name__ == "__main__":
    continuar_lectura = True
    sector = 8
    clau = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Clau predeterminada per autenticació

    # Enganxa la senyal SIGINT per netejar els recursos en sortir.
    signal.signal(signal.SIGINT, fi_de_la_lectura)

    # Crea una instància de l'objecte MFRC522
    LectorMFRC522 = MFRC522()

    try:
        if detectar_targeta(LectorMFRC522):
            dades_targeta = llegir_targeta(LectorMFRC522, sector)
            if dades_targeta and autenticar(LectorMFRC522, sector, clau, dades_targeta[0]):
                imprimir_dades(sector, LectorMFRC522.MFRC522_Read(sector))
                LectorMFRC522.MFRC522_StopCrypto1()

    except Exception as e:
        print(f"Ha ocorregut un error: {e}")

    finally:
        neteja()
