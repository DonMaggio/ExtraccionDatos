# ExtraccionDatos

_Automatización para extracción de datos de archivos pdf y generacion de mensajes personalizados para envío de Whatsapp._


## Comenzando 🚀

_Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas._


### Instalación 🔧

_Para tener un entorno de desarrollo ejecutandose_


_Instalación de entorno virtal_

```
python -m venv <nombre_de_carpeta>
```

_Activación de entorno virtual_

```
venv/Scripts/activate
```

_Instalación de paquetes necesarios_

```
pip install pdfplumber pandas openpyxl
```

_Correr el script desde la consola_

```
python script.py
```

## Esquema de carpetas
Carpeta principal
|__output
    |__log.txt (archivo de salida)
    |__mensaje.txt (archivo de salida)
    |__datos_extraidos.xlsx (archivo de salida)
|__pdfs
    |__archivo.pdf (archivos a procesar, tantos como se quiera)
|__config.ini
|__script.py

## Construido con 🛠️

_Herramientas utilizadas para crear el proyecto_

* [Pandas](https://pandas.pydata.org/) - Para la crecion de la hoja de calculos
* [pdfplumber](https://pypi.org/project/pdfplumber/) - Para la extracción del texto del pdf
* [configparser](https://docs.python.org/3/library/configparser.html) - Para configurar datos desde un archivo externo


## Autores ✒️

_Menciona a todos aquellos que ayudaron a levantar el proyecto desde sus inicios_

* **Alan Maggio** - [DonMaggio](https://github.com/DonMaggio)



## Expresiones de Gratitud 🎁

* Comenta a otros sobre este proyecto 📢
* Invita una cerveza 🍺 o un café ☕ a alguien del equipo. 
* Da las gracias públicamente 🤓.
