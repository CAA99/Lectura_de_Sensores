# Lectura de sensores 

Este proyecto se enfoca en recolectar datos de sensores conectados a un SoC, los procesarlos para su almacenamiento y análisis.

## Requisitos
- python 3.8 o superior
- paquetes: statistics, serial, json, csv, paho-mqtt, mysql-connector, datetime

## Uso
1. Conecta los sensores IoT a tu dispositivo
2. Asegúrate de tener acceso a una base de datos MySQL
3. Configura las variables _hostDB, _userDB, _passwordDB y _database en el archivo _VP.py con los detalles de tu base de datos
4. Ejecuta el script principal con python

## Funcionamiento
- El script se conecta a los sensores IoT y recolecta datos de temperatura, presión, humedad, partículas PM1, PM2.5 y PM10, y ruido.
- Los datos se procesan utilizando la librería statistics para calcular promedios.
- Los datos promedios se almacenan en una base de datos MySQL para su posterior análisis.

- leerValores(datos): Esta función recibe los datos enviados por el dispositivo IoT y los almacena en las variables globales correspondientes (_temperatura, _presion, _humedad, _pm_1, _pm_25, _pm_10, _ruido); Luego, se calculan los promedios de cada variable y se almacenan en un diccionario llamado datos_promedio, el cual es almacenado en la base de datos MySQL, Finalmente, se limpian las variables globales para recibir nuevos datos.
- publish(TEMPERTURA,PRESION,HUMEDAD,PM_1,PM_25,PM_10,RUIDO): Esta función se encarga de publicar los valores recibidos en un topic MQTT.

## Conexión a la base de datos

La conexión a la base de datos se realiza utilizando las variables globales _hostDB, _userDB, _passwordDB y _database. Es importante que estas variables estén definidas con los valores correctos antes de ejecutar el código.

## Configuración del dispositivo IoT

El ID del dispositivo IoT debe ser definido en la variable global _idDispositivo antes de ejecutar el código. Los datos enviados por el dispositivo deben tener el siguiente formato:

```{
    'Temperatura': valor,
    'Presion': valor,
    'Humedad': valor,
    'PM_1.0': valor,
    'PM_2.5': valor,
    'PM_10.0': valor,
    'dB': valor
}```