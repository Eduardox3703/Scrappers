import csv
import re

# Ruta del archivo CSV de entrada (donde están las URLs)
csv_file_path = 'tiktok/s/untiafatled.csv'

# Ruta del archivo CSV de salida (nombre del archivo incluido)
output_csv_path = 'tiktok/s/output.csv'

# Expresión regular para encontrar los nombres de usuario (después del símbolo @)
pattern = r'@([a-zA-Z0-9_.]+)'

# Lista para almacenar los usuarios
usuarios = []

# Leer el archivo CSV de entrada
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    
    for row in csv_reader:
        # Procesar cada celda de la fila
        for cell in row:
            # Buscar todos los usuarios en la celda actual
            found_users = re.findall(pattern, cell)
            usuarios.extend(found_users)  # Añadir los usuarios encontrados a la lista

# Escribir los resultados en un nuevo archivo CSV
with open(output_csv_path, mode='w', newline='', encoding='utf-8') as output_file:
    csv_writer = csv.writer(output_file)
    
    # Escribir encabezado
    csv_writer.writerow(['Usuario'])
    
    # Escribir cada usuario en una fila del archivo CSV
    for usuario in usuarios:
        csv_writer.writerow([usuario])

print(f"Usuarios guardados en: {output_csv_path}")
