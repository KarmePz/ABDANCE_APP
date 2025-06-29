import { useState, useEffect } from "react";
import { ref, uploadBytesResumable, getDownloadURL, deleteObject } from "firebase/storage";
import { collection, addDoc, getDocs, deleteDoc, doc } from "firebase/firestore";
import { storage, db } from "../firebase-config"; // Asegúrate de que db se exporte también

interface ImageManagerModalProps {
  onClose: () => void;
  onSelectImage: (url: string) => void;
}

interface StoredImage {
  id: string; // ID del documento en Firestore
  url: string;
  fileName: string;
}

export default function ImageManagerModal({
  onClose,
  onSelectImage,
}: ImageManagerModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [images, setImages] = useState<StoredImage[]>([]);
  const [loadingImages, setLoadingImages] = useState(true);
  //const endpointUrl = import.meta.env.VITE_API_URL_DEV; // Usar si decides cargar imágenes desde el backend

  // Función para obtener imágenes de Firestore
  const fetchImages = async () => {
    setLoadingImages(true);
    try {
      // Opción 1: Obtener desde Firestore (recomendado para galería gestionada)
      const querySnapshot = await getDocs(collection(db, "eventImages"));
      const imagesList: StoredImage[] = querySnapshot.docs.map((doc) => ({
        id: doc.id,
        url: doc.data().url,
        fileName: doc.data().fileName,
      }));
      setImages(imagesList);

      // Opción 2: Listar directamente de Firebase Storage (más complejo de gestionar sin Firestore)
      // const listRef = ref(storage, 'event_images/');
      // const res = await listAll(listRef);
      // const urls = await Promise.all(res.items.map(itemRef => getDownloadURL(itemRef)));
      // setImages(urls.map(url => ({ id: url, url, fileName: url.split('/').pop() || '' })));
    } catch (error) {
      console.error("Error al cargar imágenes:", error);
      alert("Error al cargar imágenes. Intenta de nuevo.");
    } finally {
      setLoadingImages(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    } else {
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Por favor selecciona un archivo.");
      return;
    }

    setIsUploading(true);
    const storageRef = ref(storage, `event_images/${file.name}`); // Ruta en Storage
    const uploadTask = uploadBytesResumable(storageRef, file);

    uploadTask.on(
      "state_changed",
      (snapshot) => {
        const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        setUploadProgress(progress);
      },
      (error) => {
        console.error("Error al subir imagen:", error);
        alert("Error al subir imagen.");
        setIsUploading(false);
      },
      async () => {
        try {
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
          console.log("Archivo disponible en", downloadURL);

          // Guardar la referencia en Firestore
          await addDoc(collection(db, "eventImages"), {
            url: downloadURL,
            fileName: file.name,
            uploadedAt: new Date(),
          });
          alert("Imagen subida y registrada correctamente.");
          setFile(null); // Limpiar input
          setUploadProgress(0);
          setIsUploading(false);
          fetchImages(); // Recargar la lista de imágenes
        } catch (firestoreError) {
          console.error("Error al guardar referencia en Firestore:", firestoreError);
          alert("Imagen subida, pero hubo un error al registrarla.");
          setIsUploading(false);
        }
      }
    );
  };

  const handleDeleteImage = async (image: StoredImage) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar "${image.fileName}"?`)) {
      return;
    }

    try {
      // 1. Eliminar de Firebase Storage
      const imageRef = ref(storage, `event_images/${image.fileName}`); // Asegúrate que el path sea el correcto
      await deleteObject(imageRef);
      console.log("Archivo eliminado de Storage.");

      // 2. Eliminar de Firestore
      await deleteDoc(doc(db, "eventImages", image.id));
      console.log("Documento eliminado de Firestore.");

      alert("Imagen eliminada correctamente.");
      fetchImages(); // Recargar la lista de imágenes
    } catch (error) {
      console.error("Error al eliminar imagen:", error);
      alert("Error al eliminar imagen.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-xl p-8 w-full max-w-3xl shadow-lg relative text-base sm:text-lg">
        <h2 className="text-xl font-bold mb-4 text-center text-[#1D094E]">
          Gestionar Imágenes de Eventos
        </h2>

        {/* Sección de Subida de Imagen */}
        <div className="mb-6 p-4 border border-gray-300 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-[#1D094E]">
            Subir Nueva Imagen
          </h3>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="mb-3 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[#EDE9FE] file:text-[#1D094E] hover:file:bg-[#DBD8FF]"
          />
          {isUploading && (
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-3">
              <div
                className="bg-[#1D094E] h-2.5 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              ></div>
              <p className="text-sm text-gray-600 mt-1">Subiendo: {uploadProgress.toFixed(1)}%</p>
            </div>
          )}
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="bg-green-600 text-white px-5 py-2 rounded-full hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? "Subiendo..." : "Subir Imagen"}
          </button>
        </div>

        {/* Sección de Galería de Imágenes */}
        <div className="mb-6 p-4 border border-gray-300 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-[#1D094E]">
            Imágenes Existentes
          </h3>
          {loadingImages ? (
            <p className="text-center text-gray-600">Cargando imágenes...</p>
          ) : images.length === 0 ? (
            <p className="text-center text-gray-600">No hay imágenes subidas aún.</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-80 overflow-y-auto p-2">
              {images.map((img) => (
                <div
                  key={img.id}
                  className="relative group border border-gray-200 rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                >
                  <img
                    src={img.url}
                    alt={img.fileName}
                    className="w-full h-32 object-cover"
                    onClick={() => onSelectImage(img.url)}
                  />
                  <div className="absolute top-1 right-1 bg-black bg-opacity-60 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleDeleteImage(img)}
                      className="text-white text-sm hover:text-red-400"
                      title="Eliminar imagen"
                    >
                      X
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 p-2 truncate" title={img.fileName}>
                    {img.fileName}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-4 mt-6">
          <button
            onClick={onClose}
            className="rounded-full px-4 py-2 font-semibold bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}