import statistics as cl
import serial
import json 
import csv
import paho.mqtt.client as mqtt
import time
import mysql.connector


from mysql.connector import errorcode
from datetime import datetime
from _VP import _hostDB, _userDB, _passwordDB, _database

_hostDB 
_userDB
_passwordDB
_database
_idDispositivo = "" 
_temperatura = []
_presion = []
_humedad = []
_pm_1 = []
_pm_25 = []
_pm_10 = []
_ruido = []

client = mqtt.Client(client_id="", clean_session=False, )

global _columns
global _values

# global TEMPERTURA
# global PRESION
# global HUMEDAD
# global PM_1
# global PM_25
# global PM_10

def leerValores(datos):
    PM_1 = (datos.get('PM_1.0')) if datos.get('PM_1.0') else 0
    PM_25 = (datos.get('PM_2.5')) if datos.get('PM_2.5') else 0
    PM_10 = (datos.get('PM_10.0')) if datos.get('PM_10.0') else 0

    TEMPERTURA = (datos.get('Temperatura')) if datos.get('Temperatura') else 0
    PRESION = (datos.get('Presion')) if datos.get('Presion') else 0
    HUMEDAD = (datos.get('Humedad')) if datos.get('Humedad') else 0
    RUIDO = (datos.get('dB')) if datos.get('dB') else 0
    
    _pm_1.append(PM_1)
    _pm_25.append(PM_25)
    _pm_10.append(PM_10)

    _temperatura.append(TEMPERTURA)
    _presion.append(PRESION)
    _humedad.append(HUMEDAD)

    _ruido.append(RUIDO)

    publish(TEMPERTURA,PRESION,HUMEDAD,PM_1,PM_25,PM_10,RUIDO)
    #print(f'temp\n{_temperatura}\n pre\n{_presion} mbar\n hum\n{_humedad}%\n')
    l_datos = len(_temperatura)

    if l_datos < 67:
            pass
    else:
        prom_temp = round(cl.mean(_temperatura), 2)
        prom_presion = round(cl.mean(_presion), 2)
        prom_humedad = round(cl.mean(_humedad), 2)
        prom_pm_1 = int(cl.mean(_pm_1))
        prom_pm_25 = int(cl.mean(_pm_25))
        prom_pm_10 = int(cl.mean(_pm_10))
        prom_ruido = round(cl.mean(_ruido),3)

        dt = datetime.now()

        datos_promedio = {
            'Dispositivo':_idDispositivo,
            'Temperatura':prom_temp, 
            'Presion':prom_presion, 
            'Humedad':prom_humedad, 
            'PM_1':prom_pm_1, 
            'PM_25':prom_pm_25, 
            'PM_10':prom_pm_10,
            'dB':prom_ruido, 
            'Tiempo':dt
            }
        
        
        _temperatura.clear()
        _presion.clear()
        _humedad.clear()
        _pm_1.clear()
        _pm_25.clear()
        _pm_10.clear()
        _ruido.clear()

        #print(f'Promedio Temperatura: {prom_temp} Â°C\n')
        #print(f'Promedio Presion: {prom_presion} mbar\n')
        #print(f'Promedio Humedad: {prom_humedad} %\n')
        #print(f'Promedio Ruido: {prom_ruido} db\n')
        #print(f'Promedio Material Particulado 1.0: {prom_pm_1}\n')
        #print(f'Promedio Material Particulado 2.0: {prom_pm_25}\n')
        #print(f'Promedio Material Particulado 10.0: {prom_pm_10}\n')
        
        
        _columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in datos_promedio.keys())
        _values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in datos_promedio.values())
        base_de_datos(_columns, _values)

        with open('datos.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Dispositivo','Temperatura', 'Presion', 'Humedad', 'dB', 'PM_1', 'PM_25', 'PM_10','Tiempo'])
        for row in datos_promedio:
            writer.writerow(row)


def leerSerial():
    print('entra a funcion de leer serial')
    #global connection
    while True:
        connection.flushInput() # flushInput  == reset_input_buffer()
        sArduino = connection.readline()
        
        try:
            print('leyendo serial')
            datos = json.loads(sArduino)
            print(datos)
            leerValores(datos)
        except json.JSONDecodeError as e:
            print("JSON:", e)
            connection.close()
            time.sleep(3)
            connection.open()
            conn()
        except serial.serialutil.SerialException:
            print('no se pudo concetar al Serial')
        except UnicodeDecodeError as un:
            print('No se pudo leer los datos', un)
            connection.close()
            time.sleep(3)
            connection.open()
            conn()

def conn():
    global connection
    while True:
        try:
            #connection = serial.Serial(port="COM6", baudrate=9600)
            connection = serial.Serial(port="/dev/ttyUSB0", baudrate=9600) #Linux o Raspberry
            if connection.isOpen():
                mqtt_cnn()
                leerSerial()
        except serial.serialutil.SerialException as ss:
            print('No se pudo conectar',ss)
            connection.close()
            time.sleep(3)
            conn()


def mqtt_cnn():
    client.enable_logger()
    client.username_pw_set(username='DemoAlcaldia', password='PruebaIoT')
    try:
        client.connect("10.1.10.86", 1883, 60)
        print('Se realizo la coenxion')
    except ConnectionError:
        print('Se ha negado la conexion del client')
    except OSError:
        print('Se ha desconectado')       

def publish(TEMPERTURA,PRESION,HUMEDAD,PM_1,PM_25,PM_10,RUIDO):
    client.loop_start()
    client.publish(f"{_idDispositivo}/temp", round(TEMPERTURA, 2))
    client.publish(f"{_idDispositivo}/presion", round(PRESION, 2))
    client.publish(f"{_idDispositivo}/humedad", round(HUMEDAD,2))
    client.publish(f"{_idDispositivo}/pm_1", PM_1)
    client.publish(f"{_idDispositivo}/pm_25", PM_25)
    client.publish(f"{_idDispositivo}/pm_10", PM_10)
    client.publish(f"{_idDispositivo}/ruido", round(RUIDO, 2))


def base_de_datos(_columns,_values):
    try:
        mydb = mysql.connector.connect(
            host=_hostDB,
            user=_userDB,
            password=_passwordDB,
            database=_database,
        )
        cursor = mydb.cursor()
        sql = "INSERT INTO sensores (Dispositivo ,Temperatura, Presion, Humedad, dB, PM_1, PM_25, PM_10, Tiempo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('datos', _columns, _values)
        cursor.execute(sql)
        print(sql)
        mydb.commit()
        cursor.close()
        mydb.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Usuario Ã³ ContraseÃ±a incorrectos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe")
        else:
            print(err)
    else:
        mydb.close()


if __name__ == '__main__': 
    conn()