# 🚀 APPrendiz - Sistema de Gestión de Etapa Productiva

**APPrendiz** es una plataforma web desarrollada para el **SENA** que optimiza el seguimiento de los contratos de aprendizaje. Permite la gestión centralizada de aprendices, instructores, empresas y bitácoras de seguimiento.

---

## 📋 Características Principales

* **Gestión de Roles:** Sistema inteligente que diferencia entre **Instructores/Administradores** (Panel de Control) y **Aprendices** (Perfil Personal).
* **Automatización de Accesos:** Creación automática de usuarios al registrar aprendices (Usuario y Contraseña = Documento de Identidad).
* **Módulo de Aprendices:** CRUD completo (Crear, Leer, Actualizar, Eliminar) con fichas técnicas detalladas.
* **Seguridad:** Protección de rutas, encriptación de contraseñas y manejo de sesiones seguras.
* **Interfaz Moderna:** Diseño responsivo utilizando Bootstrap 5 y personalización CSS.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.12, Django 5.x
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Base de Datos:** SQLite (Entorno de desarrollo)
* **Control de Versiones:** Git & GitHub

---

## ⚙️ Instalación y Configuración

Si deseas correr este proyecto en tu máquina local, sigue estos pasos:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
    cd proyecto_sena
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # En Windows
    # source venv/bin/activate  # En Mac/Linux
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Realizar migraciones:**
    ```bash
    python manage.py migrate
    ```

5.  **Crear superusuario (Administrador):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Ejecutar el servidor:**
    ```bash
    python manage.py runserver
    ```

---

## 👥 Autores

* **Daniel** - *Desarrollador Full Stack*
* Proyecto formativo para el **SENA**.

---

Made with Django.