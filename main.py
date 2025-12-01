"""
I.   Introducción (Configuración y Contexto)
II.  Requerimientos (Librerías, Autenticación y Reglas)
III. Planteamiento del Data-Set (Pre-procesamiento y Normalización)
IV.  Aprendizaje (Modelo Transformer BERT - Transfer Learning)
V.   Comprobación (Diagnóstico de Validación)
VI.  Evaluación (Métricas y Lógica de Negocio)
VII. Despliegue (Ejecución y Acciones de API)
"""

#  SECCIÓN II: REQUERIMIENTOS

#  2.1 Determinación de Requisitos (Librerías de Software)
import os
import sys
import pickle
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from transformers import pipeline

# --- 2.1 Definición del Dominio (Configuración de Sensibilidad) ---

# Umbral 3: Borra Odio (1), Malos (2) y Regulares (3). Tolerancia Cero.
UMBRAL_TOXICIDAD = 3      
BORRAR_REALMENTE = True  

# --- 2.2 Requisitos Funcionales: Sistema Experto (Base de Reglas) ---
PALABRAS_PROHIBIDAS = [
    "basura", "estupido", "idiota", "imbecil", "muérete", 
    "asco", "retrasado", "tonto", "inutil", 
    "ctm", "mierda", "cagada", "maldita", "fucking",
    "gay", "maricon", "cabro", "sao", "apestoso", "horrible"
]


#  SECCIÓN II : AUTENTICACIÓN
#  2.2 Gestión de Credenciales y Seguridad OAuth 2.0

def get_authenticated_service():
    """
    Establece conexión segura.
    Scope: force-ssl (Permisos de administración y moderación).
    """
    credentials = None
    token_file = 'token_final.pickle' # Persistencia de sesión
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                print("ERROR CRÍTICO: No se encontró 'client_secret.json' ")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            credentials = flow.run_local_server(port=8080)
        
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)


#  SECCIÓN IV: APRENDIZAJE

#  4.1 Planteamiento del Modelo (Deep Learning - Transfer Learning)
print("--- CARGANDO MODELO BERT (Transfer Learning) ---")
classifier = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')


#  SECCIÓN III: PLANTEAMIENTO DEL DATA-SET Y PRE-PROCESAMIENTO

#  3.2 Normalización y Filtrado de Datos
def analizar_toxicidad(texto):
    """
    Procesa el texto crudo y aplica el modelo híbrido.
    Input: Texto Raw -> Normalización -> Inferencia.
    """
    texto_lower = texto.lower()
    
    # Capa 1: Filtrado Determinista (Reglas)
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto_lower:
            return True, f"REGLA ACTIVA: Palabra prohibida '{palabra}'", 1.0

    # Capa 2: Filtrado Probabilístico (IA)
    try:
        resultado = classifier(texto[:512])[0]
        estrellas = int(resultado['label'].split()[0])
        score = resultado['score']
        
        # Lógica de Decisión (Evaluación)
        if estrellas <= UMBRAL_TOXICIDAD:
            return True, f"MODELO BERT: Detectó {estrellas} Estrellas (Umbral {UMBRAL_TOXICIDAD})", score
        else:
            return False, f"LIMPIO: {estrellas} Estrellas", score
    except:
        return False, "NEUTRO (Error de formato)", 0.0


#  SECCIÓN VII: DESPLIEGUE (Función de Acción)
#  7.2 Deploy del Sistema (Lógica de Borrado Robusta)

def borrar_comentario_seguro(youtube, comment_id):
    """ Intenta borrar permanentemente, si falla, rechaza (oculta). """
    try:
        # Intento 1: Delete
        youtube.comments().delete(id=comment_id).execute()
        print("   🗑️ ACCIÓN: ELIMINADO (Delete exitoso)")
    except Exception as e:
        print(f"   ⚠️ Falló Delete ({e}). Intentando Plan B...")
        try:
            # Intento 2: SetModerationStatus (Rejected)
            youtube.comments().setModerationStatus(
                id=comment_id, moderationStatus='rejected'
            ).execute()
            print("    ACCIÓN: RECHAZADO (Moderación exitosa)")
        except Exception as e2:
            print(f"   ❌ ERROR CRÍTICO API: {e2}")


#  SECCIÓN V: COMPROBACIÓN (Diagnóstico)

def ejecutar_diagnostico():
    print("\n" + "="*50)
    print("--- AUTO-DIAGNÓSTICO DEL SISTEMA ---")
    casos = [("Este video es excelente", False), ("Eres una basura apestosa", True)]
    for txt, esperado in casos:
        res, _, _ = analizar_toxicidad(txt)
        status = "OK" if res == esperado else "FAIL"
        print(f"Test: '{txt[:15]}...' -> {'TÓXICO' if res else 'LIMPIO'} [{status}]")
    print("="*50 + "\n")


#  SECCIÓN VI: EVALUACIÓN Y EJECUCIÓN PRINCIPAL

def main():
    ejecutar_diagnostico() # Validación previa
    
    # 3.3 Data-Set de Pruebas (Streaming)
    video_id = input("INGRESE ID DEL VIDEO: ").strip()
    if not video_id: return

    try:
        youtube = get_authenticated_service()
        print(f"\n>>> INICIANDO MODERACIÓN EN VIDEO: {video_id}")
        
        request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, textFormat="plainText", maxResults=20
        )
        
        while request:
            response = request.execute()
            for item in response['items']:
                comment_id = item['snippet']['topLevelComment']['id'].strip()
                text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                
                # 5.1 Aplicación del Modelo
                es_toxico, motivo, confianza = analizar_toxicidad(text)
                
                print(f"Usuario: {author} | Dice: \"{text[:30]}...\"")
                
                # 6.1 Evaluación de Métricas
                if es_toxico:
                    print(f"❌ [TOXICO] -> {motivo} | Confianza: {confianza:.2f}")
                    if BORRAR_REALMENTE:
                        borrar_comentario_seguro(youtube, comment_id)
                    else:
                        print("   (Simulación)")
                else:
                    print(f"✅ [APROBADO] -> Contenido Seguro")
                print("-" * 40)

            if 'nextPageToken' in response:
                request = youtube.commentThreads().list(
                    part="snippet", videoId=video_id, textFormat="plainText",
                    pageToken=response['nextPageToken'], maxResults=20
                )
            else:
                break
    except Exception as e:
        print(f"ERROR DE EJECUCIÓN: {e}")

if __name__ == '__main__':
    main()