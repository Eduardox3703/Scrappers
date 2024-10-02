import json
from bs4 import BeautifulSoup

def main():
    # Ruta al archivo HTML
    file_path = "tiktok/latest_video_comments.html"  # Reemplaza esto con la ruta a tu archivo

    # Lee el contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Crea un objeto BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Encuentra todos los comentarios
    comments = soup.find_all("div", class_="css-1gstnae-DivCommentItemWrapper")

    # Lista para almacenar los comentarios limpios
    cleaned_comments = []

    # Extrae usuario y comentario
    for comment in comments:
        # Extraer el nombre de usuario
        username_elem = comment.find("a", class_="css-22xkqc-StyledLink")
        if username_elem:
            username = username_elem['href'].split('/')[-1]  # Obtiene el usuario del href
            display_name = username_elem.find("span").get_text(strip=True)  # Nombre a mostrar
        else:
            username = "Usuario no encontrado"
            display_name = "Nombre no encontrado"

        # Extraer el texto del comentario
        comment_elem = comment.find("span", style="color: inherit; font-size: inherit; font-weight: inherit; font-family: var(--tux-web-font-body);")
        comment_text = comment_elem.get_text(strip=True) if comment_elem else "Comentario no encontrado"

        # Agregar los datos limpios a la lista
        cleaned_comments.append({
            "usuario": username,
            "comentario": comment_text
        })

    # Convertir la lista a JSON
    json_data = json.dumps(cleaned_comments, ensure_ascii=False, indent=4)

    # Guardar el JSON en un archivo
    with open("comentarios.json", 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print("Datos limpios guardados en 'comentarios.json'.")

if __name__ == "__main__":
    main()
