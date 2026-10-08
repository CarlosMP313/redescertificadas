REDCER WEB V2.2 — Flask + SQLite

CAMBIOS PRINCIPALES
- Menú individual: Inicio / Nosotros / Servicios / Certificaciones / Clientes / Contacto.
- Proyectos cambia a CLIENTES.
- Configuración central: textos, misión, visión, historia, experiencia, medios de Inicio/Nosotros/Certificaciones/Contacto, redes sociales y mostrar/ocultar recomendaciones.
- Servicios: 17 servicios iniciales, icono configurable y foto/video por servicio.
- Certificaciones: carga de foto o video de cada marca/certificación, sin descripciones obligatorias.
- Clientes: logo, foto y agradecimiento/semblanza editable.
- Equipo: personas destacadas con fotografía y semblanza.
- Recomendaciones: comentarios con 1–5 estrellas y mostrar/ocultar sección.
- Solicitudes de contacto se guardan en SQLite.
- Los cambios del administrador se guardan permanentemente en instance/redcer.db.

INSTALACIÓN
1. Instala Python 3.10 o superior.
2. Doble clic en INSTALAR_REDCER.bat (primera vez).
3. Doble clic en INICIAR_REDCER.bat para posteriores arranques.
4. Sitio: http://127.0.0.1:5000
5. Admin: http://127.0.0.1:5000/admin/login

Usuario inicial: admin
Contraseña inicial: REDCER2026!

IMPORTANTE: cambia la contraseña desde el panel después del primer acceso.


CATALOGO DE SERVICIOS REDCER
- Detección de incendio
- Control de acceso
- Seguridad física
- Seguridad lógica
- Enfriamiento
- Confort
- Precisión
- Paneles fotovoltaicos
- Plantas de emergencia
- Sistemas de alimentación ininterrumpida (UPS)
- Redes Eléctricas
- Iluminación
- Tierras físicas y pararrayos
- Video vigilancia
- Domótica
- Networking
- Cableado estructurado

Estos servicios aparecen automáticamente en la página SERVICIOS y en el formulario de CONTACTO; se pueden editar desde el panel administrador.


V2.8: Se agregó formulario público de recomendaciones en Contacto con calificación de 1 a 5 estrellas. El administrador puede editar, publicar, ocultar o eliminar comentarios desde Recomendaciones.


V2.9: Nuevo módulo 'Logos e identidad' para cambiar el logo principal desde Administración y ajustar su tamaño/visualización sin recomprimir el archivo.
