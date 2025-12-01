# Sistema Híbrido de Moderación de Comentarios en YouTube "

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Transformers%20BERT-orange?style=for-the-badge)
![API](https://img.shields.io/badge/YouTube-Data%20API%20v3-red?style=for-the-badge&logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## I. INTRODUCCIÓN
Este proyecto implementa un **Agente Inteligente de Moderación** capaz de filtrar automáticamente la sección de comentarios de videos de YouTube en tiempo real.

1.  **Filtrado Determinista (Reglas):** Un diccionario local (Blacklist) para la eliminación inmediata de insultos explícitos y lenguaje soez.
2.  **Filtrado Probabilístico (Deep Learning):** Un modelo **Transformer BERT Multilingüe** que analiza la semántica y el sentimiento del texto para detectar toxicidad contextual, odio sutil o sarcasmo agresivo.

El sistema utiliza la **YouTube Data API v3** bajo el protocolo OAuth 2.0 para garantizar permisos administrativos seguros (lectura y eliminación) sobre el canal del usuario.

## II. REQUERIMIENTOS

### 2.1 Requisitos de Software
* **Lenguaje:** Python 3.9 o superior.
* **Gestión de Dependencias:** `pip`.
* **Entorno:** Visual Studio Code (recomendado) o Terminal.

### 2.2 Librerías Clave
* `google-api-python-client`: Interfaz para la API de YouTube.
* `transformers` (Hugging Face): Pipeline de inferencia para el modelo NLP.
* `torch`: Backend de cálculo tensorial para la IA.

--- 

## III. ESTRUCTURA DEL PROYECTO 
 PROYECTO_IA
├── 📄 main.py                 Lógica de autenticación, IA y filtrado.

├── 📄 requirements.txt        Lista de dependencias del entorno.

├── 📄 client_secret.json      (NO INCLUIDO) Credenciales OAuth 2.0 de Google.

├── 📄 token.pickle            (AUTOGENERADO) Token de sesión cifrado.

├── 📄 .gitignore              Configuración de seguridad (excluye claves).

└── 📄 README.md               Documentación técnica del sistema.

---

## IV. PLANTEAMIENTO DEL APRENDIZAJE (DATA-SET)

El proyecto utiliza la técnica de Transfer Learning (Aprendizaje por Transferencia):
Modelo Base: nlptown/bert-base-multilingual-uncased-sentiment.Entrenamiento: 
El modelo ha sido pre-entrenado con el Multilingual Amazon Reviews Corpus (millones de registros en 6 idiomas).

Pre-procesamiento:Tokenización: Conversión de texto a vectores numéricos (embeddings).Truncamiento: Límite de 512 tokens por comentario para eficiencia computacional.
Validación: Se utiliza un esquema de In-the-wild Testing (Pruebas en entorno real) usando datos en vivo (Data Streaming) de la API de YouTube.

## V. INSTALACIÓN Y CONFIGURACIÓN: Por razones de seguridad informática, las credenciales (client_secret.json) NO se incluyen en este repositorio. 

Siga estos pasos para configurar su entorno:

1. Clonar el repositorio: git clone ...

2. Instalar dependencias: pip install -r requirements.txt

3. Configuración de Credenciales Google Cloud 
Para replicar el entorno de ejecución, siga estos pasos exactos:

1.  **Crear Proyecto y Habilitar API:**
    * Ingrese a Google Cloud Console.
    * Cree un Nuevo Proyecto llamado `...` .
    * Vaya a "APIs y Servicios" > "Biblioteca".
    * Busque **"YouTube Data API v3"** y haga clic en **HABILITAR**.

2.  **Configurar Pantalla de Consentimiento (OAuth):**
    * Vaya a "Pantalla de consentimiento de OAuth".
    * Seleccione **User Type: Externo** y cree.
    * Llene los datos obligatorios (Nombre de app, correos de soporte).
    * **IMPORTANTE (Test Users):** En la sección "Usuarios de prueba", agregue su propio correo de Gmail. *Sin esto, la API bloqueará el acceso por seguridad.*

3.  **Definir Permisos (Scopes):**
    * En la pestaña "Acceso a los datos", agregue manualmente el permiso sensible:
    * `https://www.googleapis.com/auth/youtube.force-ssl`
    * *(Este permiso es obligatorio para ejecutar acciones de ELIMINACIÓN de comentarios).*

4.  **Generar la Llave (JSON):**
    * Vaya a "Clientes" > "Crear Clientes" > **"ID de cliente de OAuth"**.
    * Tipo de Aplicación: **Aplicación de escritorio**.
    * Descargue el archivo `.json` generado.
    * **REQUISITO:** Cambie el nombre del archivo descargado a `client_secret.json` y muévalo a la carpeta principal del proyecto.


## VI. EJECUCIÓN Y PRUEBAS

* Para iniciar el agente de moderación:
python main.py

* El sistema solicitará el ID del Video (la cadena de 11 caracteres después de v= en la URL).

 Ejemplo: Para youtube.com/watch?v=dQw4w9WgXcQ, el ID es dQw4w9WgXcQ.

* Se abrirá el navegador para autorizar los permisos de administración (la primera vez).
* El sistema analizará comentario por comentario.

 Ejemplo de Salida (Log):Plaintext--- MODERANDO VIDEO dQw4w9WgXcQ ---

Usuario: JuanPerez | Comentario: "Este video me ayudó mucho, gracias"
 [OK] -> Limpio (5 estrellas)

Usuario: Troll_01 | Comentario: "Eres una basura, muérete"
 [TOXICO] -> PALABRA PROHIBIDA: 'basura'
    ELIMINADO (Acción API: DELETE)

Usuario: Hater_X | Comentario: "Tu contenido da pena ajena, retírate"
 [TOXICO] -> IA DETECTÓ ODIO (1 estrella - Confianza: 0.98)
    ELIMINADO (Acción API: DELETE)


## VII. EVALUACIÓN Y DESEMPEÑO
El sistema utiliza métricas de confianza (Confidence Score) para la toma de decisiones:

Umbral de Toxicidad: $\le$ 1 Estrella.

Precisión: El modelo híbrido minimiza los falsos positivos, permitiendo críticas negativas válidas (2-3 estrellas) mientras elimina agresiones directas.Latencia: < 500ms por comentario en inferencia CPU.






