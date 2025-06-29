# functions/Eventos/images.py
from firebase_admin import firestore, storage # Importa storage para eliminar archivos
from google.cloud.storage import Blob # Para trabajar con blobs y extraer la ruta

db = firestore.client()

def get_images(request):
    """Obtiene una lista de URLs de imágenes de la colección 'eventImages' de Firestore."""
    try:
        images_ref = db.collection('eventImages')
        docs = images_ref.order_by('uploadedAt', direction=firestore.Query.DESCENDING).stream() # Ordenar por fecha de subida
        image_list = []
        for doc in docs:
            image_data = doc.to_dict()
            image_list.append({
                "id": doc.id,
                "url": image_data.get("url"),
                "fileName": image_data.get("fileName"),
                "uploadedAt": image_data.get("uploadedAt").isoformat() if image_data.get("uploadedAt") else None # Convertir a string para JSON
            })
        return image_list, 200
    except Exception as e:
        print(f"Error fetching images: {e}")
        return {"error": str(e)}, 500

def delete_image(request):
    """
    Elimina una imagen de la colección 'eventImages' de Firestore y de Firebase Storage.
    Recibe el ID del documento de Firestore de la imagen a eliminar.
    """
    request_json = request.get_json(silent=True)
    if request_json and 'id' in request_json:
        image_doc_id = request_json['id']
    else:
        return {"error": "Image ID is required in the request body."}, 400

    try:
        image_ref_firestore = db.collection('eventImages').document(image_doc_id)
        image_doc = image_ref_firestore.get()

        if not image_doc.exists:
            return {"error": "Image not found in Firestore."}, 404

        image_data = image_doc.to_dict()
        storage_url = image_data.get("url")
        file_name = image_data.get("fileName")

        if not storage_url or not file_name:
            return {"error": "Image data (URL or fileName) is missing in Firestore document."}, 500

        # 1. Eliminar de Firebase Storage
        bucket = storage.bucket() # Obtiene el bucket por defecto de Firebase Admin SDK
        # Construye la ruta del blob en Storage
        # Asumiendo que tus imágenes están en 'event_images/{file.name}'
        blob_path = f"event_images/{file_name}"
        blob = bucket.blob(blob_path)

        if blob.exists(): # Verifica si el blob existe antes de intentar eliminar
            blob.delete()
            print(f"Archivo '{blob_path}' eliminado de Storage.")
        else:
            print(f"Advertencia: Archivo '{blob_path}' no encontrado en Storage, solo se eliminará la referencia de Firestore.")

        # 2. Eliminar el documento de Firestore
        image_ref_firestore.delete()
        print(f"Documento '{image_doc_id}' eliminado de Firestore.")

        return {"message": "Image deleted successfully."}, 200
    except Exception as e:
        print(f"Error deleting image: {e}")
        return {"error": f"Failed to delete image: {str(e)}"}, 500