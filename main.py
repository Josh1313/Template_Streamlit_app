
import streamlit as st
from streamlit_option_menu import option_menu
from utils.streamlit_style import hide_streamlit_style
from utils.analytics import inject_google_analytics
import os
from dotenv import load_dotenv
# Importar las páginas al principio
from app_pages import home, account, chat, files, model_selector, newpage

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Template", page_icon=":robot_face:")

hide_streamlit_style()

# Inyectar Google Analytics (opcional)
inject_google_analytics()


# Clase para manejar múltiples aplicaciones
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        """Agrega una nueva página a la aplicación."""
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        """Ejecuta la aplicación y maneja la navegación."""
        # Menú de opciones en la barra lateral
        with st.sidebar:
            # Obtener los títulos de las páginas dinámicamente
            page_titles = [app["title"] for app in self.apps]
            app = option_menu(
                menu_title='Template 🤖',
                options=page_titles,# Títulos dinámicos
                default_index=1,
                menu_icon=":robot_face:",
                icons=['house-fill', 'person-circle', 'chat-fill', 'file-earmark-text-fill', 'gear-fill', 'plus-circle-fill'],# Iconos de Bootstrap
                orientation="vertical",# horizontal o vertical
                styles={
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        # Navegación entre páginas
        for app_data in self.apps:
            if app_data["title"] == app:
                app_data["function"]()  # Ejecuta la función asociada a la página

# Ejecutar la aplicación
if __name__ == "__main__":
    # Crear una instancia de MultiApp
    multi_app = MultiApp()

    # Agregar páginas dinámicamente con nombres personalizados
    multi_app.add_app("Inicio", home.app)  # Nombre personalizado: "Inicio"
    multi_app.add_app("Mi Cuenta", account.app)  # Nombre personalizado: "Mi Cuenta"
    multi_app.add_app("Chatbot", chat.app)  # Nombre personalizado: "Chatbot"
    multi_app.add_app("Archivos", files.app)  # Nombre personalizado: "Archivos"
    multi_app.add_app("Modelos", model_selector.app)  # Nombre personalizado: "Modelos"
    multi_app.add_app("Nueva Página", newpage.app)  # Nombre personalizado: "Nueva Página"

    # Ejecutar la aplicación
    multi_app.run()