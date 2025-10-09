# 🏍️ Raffles Site - Sistema de Rifas de Motos

Sistema completo de rifas con Django, PostgreSQL y Wompi para pagos.

## 🚀 Características

- Sistema de autenticación con verificación por email
- Rifas de motos con imágenes
- Carrito de compras y sistema de tickets  
- Integración con Wompi para pagos
- Panel administrativo con Jazzmin
- Diseño responsive con efectos holográficos

## 🛠️ Tecnologías

- **Backend:** Django 4.2, PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript
- **Pagos:** Wompi
- **Email:** Gmail SMTP
- **Deploy:** Railway

## 📦 Instalación

1. Clonar repositorio
2. Crear entorno virtual: `python -m venv env`
3. Activar entorno: `source env/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y configurar variables
6. Migrar base de datos: `python manage.py migrate`
7. Ejecutar: `python manage.py runserver`

## 🔧 Variables de Entorno

Ver archivo `.env.example` para todas las variables requeridas.

## 📄 Licencia

MIT License
