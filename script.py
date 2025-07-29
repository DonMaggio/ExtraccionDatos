import os, re, pdfplumber, pandas as pd
from datetime import datetime, timedelta
import locale
import configparser

# --- Leer configuración desde config.ini ---
config = configparser.ConfigParser()
config.read('config.ini')

DIFERENCIA_DIAS = int(config.get('VISITA', 'dias_adelanto', fallback=1))
HORARIO_VISITA = config.get('VISITA', 'horario', fallback='9 a 14hs')

# --- Configuración ---
PDF_FOLDER = 'pdfs'
OUTPUT_FOLDER = 'output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

EXCEL_FILE = os.path.join(OUTPUT_FOLDER, 'datos_extraidos.xlsx')
MENSAJE_FILE = os.path.join(OUTPUT_FOLDER, 'mensajes.txt')

# Crear archivo de log con fecha y hora
log_filename = os.path.join(OUTPUT_FOLDER, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
def log(msg):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")

EQUIPOS_RE = r"\b(LAVARROPAS|LAVAVAJILLAS|SECARROPAS|HELADERA|LAVASECARROPAS|HORNO ELECTRICO|HORNO|MICROONDAS|AIRE ACONDICIONADO|FREEZER|CALEF[ÓO]N|CALEFACTOR|CAMPANA|CALDERA|TERMO TANQUE|TERMOTANQUE|CAVA)\b"

# --- CONFIGURACIÓN PERSONALIZABLE ---
#DIFERENCIA_DIAS = 1           # Día de visita: 1 = mañana, 2 = pasado, etc.
#HORARIO_VISITA = "9 a 14hs"   # Puede ser "14 a 18hs", etc.

# --- Localización ---
try:
    locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Argentina')
    except:
        pass

def obtener_saludo():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        return "Buen día"
    elif 12 <= hora < 20:
        return "Buenas tardes"
    else:
        return "Buenas noches"


def dia_futuro_str(dias_adelanto=DIFERENCIA_DIAS):
    futura = datetime.now() + timedelta(days=dias_adelanto)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[futura.weekday()], futura.day

def extraer_datos(path_pdf):
    with pdfplumber.open(path_pdf) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        lines = full_text.splitlines()

    nombre = compania = celular = telefono = direccion = ''
    bienes = []

    # Nombre
    for i, line in enumerate(lines):
        if 'nombre del asegurado' in line.lower():
            for j in range(1, 4):
                if i + j < len(lines):
                    candidato = lines[i + j].strip()
                    if candidato:
                        partes = candidato.split()
                        numeros = [p for p in partes if re.match(r'\d{6,}', p)]
                        texto = [p for p in partes if not re.match(r'\d{6,}', p)]
                        nombre = ' '.join(texto).title()
                        if numeros and not celular:
                            celular = numeros[0]
                        break
            break

    # Celular y Teléfono
    for i, line in enumerate(lines):
        texto = line.lower().strip()

        if 'celular' in texto or 'cel' in texto:
            for j in range(0, 1):
                if i + j < len(lines):
                    #candidato = lines[i + j].strip()
                    #numeros = re.findall(r'\b\d{6,15}\b', candidato.replace(" ", "").replace("-", ""))
                    #celulares.extend(numeros)

                    cand = lines[i + j].strip()
                    match = re.search(r'(\d[\d\s\-]{6,})', cand)
                    if match:
                        celular = match.group(1).strip()
                    break

        if 'teléfono' in texto or 'telefono' in texto or 'tel' in texto:
            for j in range(0, 1):
                if i + j < len(lines):
                    #candidato = lines[i + j].strip()
                    #numeros = re.findall(r'\b\d{6,15}\b', candidato.replace(" ", "").replace("-", ""))
                    #telefonos.extend(numeros)

                    cand = lines[i + j].strip()
                    match = re.search(r'(\d[\d\s\-]{6,})', cand)
                    if match:
                        telefono = match.group(1).strip()
                    break

    #celular = " / ".join(dict.fromkeys(celulares)) if celulares else ""
    #telefono = " / ".join(dict.fromkeys(telefonos)) if telefonos else ""

    # Dirección
    direccion_lines = []
    for i, line in enumerate(lines):
        if 'dirección' in line.lower():
            for j in range(1, 4):
                if i + j < len(lines):
                    l = lines[i + j].strip()
                    if l and not re.search(r'CP[:\s]*\d{4,5}', l, re.IGNORECASE):
                        direccion_lines.append(l)
                    if re.search(r'CP[:\s]*\d{4,5}', l, re.IGNORECASE):
                        direccion_lines.append(l)
                        break
            break
    if direccion_lines:
        direccion = ', '.join(direccion_lines).strip().title()

    # Compañía
    match_compania = re.search(r'COMPAN[IÍ]A.*?\n([^\|]+)\s*\|', full_text, re.IGNORECASE)
    compania = match_compania.group(1).strip().title() if match_compania else "No detectada"

    # Equipos (sin eliminar duplicados)
    #equipos = re.findall(EQUIPOS_RE, full_text.upper())
    #bienes = ', '.join(e.title() for e in equipos) if equipos else ""

    # --- Equipos: detectar desde sección real ---
    equipos = []

    for i, line in enumerate(lines):
        if re.search(r'EQUIPO\s+MARCA\s+MODELO\s+SERIE\s+ACCESORIOS', line.upper()):
            # Buscamos hasta 10 líneas después de esa sección
            for j in range(1, 5):
                if i + j >= len(lines):
                    break
                l = lines[i + j].strip().upper()
                if not l or "FIRMA" in l:
                    break
                equipos_en_linea = re.findall(EQUIPOS_RE, l)
                equipos.extend(e.title() for e in equipos_en_linea)
            break

    bienes = ', '.join(equipos) if equipos else ""

    return {
        "nombre": nombre,
        "compania": compania,
        "celular": celular,
        "telefono": telefono,
        "direccion": direccion,
        "bienes": bienes
    }

def generar_mensaje(dato):
    #contacto1 = dato["celular"]# or dato["telefono"]
    #ontacto2 = dato["telefono"]
    saludo = obtener_saludo()
    nombre_dia, num_dia = dia_futuro_str()

    articulos = {
        "lavarropas": "el", "lavavajillas": "el", "lavasecarropas": "el",
        "secarropas": "el", "heladera": "la", "microondas": "el",
        "notebook": "la", "televisor": "el", "horno electrico": "el",
        "horno": "el", "cocina": "la", "freezer": "el", "calefón": "el",
        "aire acondicionado": "el", "calefactor": "el", "campana":"la", "caldera":"la",
        "TERMO TANQUE":"el", "TERMOTANQUE":"el", "cava":"la"
    }

    bienes_str = dato["bienes"].lower()
    bienes_lista = [b.strip() for b in bienes_str.split(',') if b.strip()]
    cantidad = len(bienes_lista)

    def frase_con_articulos(lista):
        if not lista:
            return "el equipo"
        con_articulos = []
        for item in lista:
            art = articulos.get(item.lower(), "el")
            con_articulos.append(f"{art} {item}")
        if len(con_articulos) == 1:
            return con_articulos[0]
        elif len(con_articulos) == 2:
            return f"{con_articulos[0]} y {con_articulos[1]}"
        else:
            return ", ".join(con_articulos[:-1]) + " y " + con_articulos[-1]

    frase_equipo_raw = frase_con_articulos(bienes_lista)

    # Corregir artículo definido
    if frase_equipo_raw.startswith("el "):
        frase_equipo = f"del {frase_equipo_raw[3:]}"
    elif frase_equipo_raw.startswith("la "):
        frase_equipo = f"de la {frase_equipo_raw[3:]}"
    else:
        frase_equipo = f"de {frase_equipo_raw}"

    #Personalizar mmensaje
    verbo_verificar = "los equipos" if cantidad > 1 else "el equipo"
    mañana = "" if DIFERENCIA_DIAS > 1 else " de mañana"

    return (
        f"(Cel: {dato['celular']} - Tel: {dato['telefono']}) - {dato['nombre']} \n"
        f"{saludo}, soy Fernando Luchetti, me comunico del servicio técnico de *{dato['compania']}* "
        f"por la denuncia {frase_equipo}. El día{mañana} *{nombre_dia} {num_dia} en el horario de {HORARIO_VISITA}* vamos a estar "
        f"pasando por tu domicilio para verificar {verbo_verificar} y preciso que nos confirme si nos puede recibir "
        f"algún mayor de 18 años. En caso de no poder, nos volveremos a comunicar para coordinar nuevo día y horario. "
        f"Muchas gracias.\n"
    )

# --- Procesamiento ---
resultados = []
mensajes = []

for file in sorted(os.listdir(PDF_FOLDER)):
    if file.lower().endswith('.pdf'):
        path = os.path.join(PDF_FOLDER, file)
        log(f"Procesando archivo: {file}")
        try:
            data = extraer_datos(path)
            resultados.append(data)
            mensajes.append(generar_mensaje(data))

            log(f"Nombre: {data['nombre']} | Compañía: {data['compania']} | Equipos: {data['bienes']}")
        except Exception as e:
            log(f"❌ Error al procesar {file}: {str(e)}")

df = pd.DataFrame(resultados)
df.to_excel(EXCEL_FILE, index=False)

with open(MENSAJE_FILE, "w", encoding="utf-8") as f:
    for msg in mensajes:
        f.write(msg + "\n\n")

print("✅ Proceso finalizado. Archivos generados en la carpeta 'output/'.")
log("✅ Proceso completado. Archivos generados.")
