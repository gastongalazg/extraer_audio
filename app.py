from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import uuid
from pathlib import Path
import shutil
import logging
from dotenv import load_dotenv

from config import config

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE) if config.LOG_FILE else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audio Extractor API",
    description="API para extraer audio de archivos de video usando FFmpeg",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


class AudioExtractor:
    """Clase para manejar la extracción de audio de videos"""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
    
    def is_video_file(self, content_type: str) -> bool:
        """Verificar si el archivo es un video"""
        return content_type in config.ALLOWED_VIDEO_TYPES or content_type.startswith("video/")
    
    def is_supported_format(self, format: str) -> bool:
        """Verificar si el formato de audio es soportado"""
        return format.lower() in config.SUPPORTED_FORMATS
    
    def get_audio_codec(self, format: str) -> str:
        """Obtener codec de audio para el formato especificado"""
        return config.SUPPORTED_FORMATS.get(format.lower(), "libmp3lame")
    
    def generate_file_paths(self, file_id: str, filename: str, format: str) -> tuple[Path, Path]:
        """Generar rutas para archivos de entrada y salida"""
        input_path = self.temp_dir / f"{file_id}_input{Path(filename).suffix}"
        output_path = self.temp_dir / f"{file_id}_output.{format}"
        return input_path, output_path
    
    def save_uploaded_file(self, file: UploadFile, input_path: Path) -> None:
        """Guardar archivo subido en disco"""
        try:
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"Archivo guardado: {input_path}")
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            raise HTTPException(status_code=500, detail="Error al guardar archivo")
    
    def extract_audio_with_ffmpeg(self, input_path: Path, output_path: Path, format: str) -> None:
        """Extraer audio usando FFmpeg"""
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",  # Sin video
            "-acodec", self.get_audio_codec(format),
            "-y",   # Sobrescribir archivo de salida
            str(output_path)
        ]
        
        try:
            logger.info(f"Ejecutando comando FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.FFMPEG_TIMEOUT)
            
            if result.returncode != 0:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error al extraer audio: {result.stderr}"
                )
                
            if not output_path.exists():
                raise HTTPException(
                    status_code=500, 
                    detail="Error al generar archivo de audio"
                )
                
            logger.info(f"Audio extraído exitosamente: {output_path}")
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error en subprocess: {e}")
            raise HTTPException(status_code=500, detail="Error en procesamiento de audio")
        except subprocess.TimeoutExpired:
            logger.error("Timeout en FFmpeg")
            raise HTTPException(status_code=500, detail="Timeout en procesamiento de audio")
    
    def cleanup_file(self, file_path: Path) -> None:
        """Limpiar archivo temporal"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Archivo limpiado: {file_path}")
        except Exception as e:
            logger.warning(f"Error al limpiar archivo {file_path}: {e}")


# Instancia del extractor
audio_extractor = AudioExtractor(config.TEMP_DIR)


@app.post("/extract-audio")
async def extract_audio(file: UploadFile = File(...), format: str = "mp3"):
    """
    Extraer audio de un archivo de video
    
    Args:
        file: Archivo de video subido
        format: Formato de audio de salida (mp3, wav, ogg, aac, flac)
    
    Returns:
        FileResponse: Archivo de audio extraído
    """
    # Validaciones
    if not audio_extractor.is_video_file(file.content_type):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un video"
        )
    
    if not audio_extractor.is_supported_format(format):
        raise HTTPException(
            status_code=400, 
            detail=f"Formato no soportado. Formatos válidos: {', '.join(config.SUPPORTED_FORMATS.keys())}"
        )
    
    # Validar tamaño del archivo
    if file.size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {config.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )
    
    # Generar ID único para el archivo
    file_id = str(uuid.uuid4())
    logger.info(f"Iniciando extracción de audio para archivo: {file.filename} (ID: {file_id})")
    
    # Generar rutas de archivos
    input_path, output_path = audio_extractor.generate_file_paths(
        file_id, file.filename, format
    )
    
    try:
        # Guardar archivo subido
        audio_extractor.save_uploaded_file(file, input_path)
        
        # Extraer audio
        audio_extractor.extract_audio_with_ffmpeg(input_path, output_path, format)
        
        # Retornar archivo
        return FileResponse(
            path=str(output_path),
            filename=f"{Path(file.filename).stem}.{format}",
            media_type=f"audio/{format}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado durante extracción: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    finally:
        # Limpiar archivo de entrada
        audio_extractor.cleanup_file(input_path)


@app.get("/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """
    Limpiar archivos temporales después de la descarga
    
    Args:
        file_id: ID del archivo a limpiar
    
    Returns:
        dict: Mensaje de confirmación
    """
    try:
        files_cleaned = 0
        for file_path in config.TEMP_DIR.glob(f"{file_id}_*"):
            if file_path.exists():
                file_path.unlink()
                files_cleaned += 1
        
        logger.info(f"Limpieza completada para ID {file_id}: {files_cleaned} archivos eliminados")
        return {"message": f"Archivos limpiados: {files_cleaned}"}
        
    except Exception as e:
        logger.error(f"Error durante limpieza: {e}")
        return {"message": "Error durante limpieza", "error": str(e)}


@app.get("/health")
async def health_check():
    """Endpoint para verificar estado del servidor"""
    return {"status": "healthy", "service": "audio-extractor"}


@app.get("/")
async def root():
    """Servir interfaz web"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {
            "name": "Audio Extractor API",
            "version": "1.0.0",
            "description": "API para extraer audio de archivos de video usando FFmpeg",
            "endpoints": {
                "POST /extract-audio": "Extraer audio de un video",
                "GET /cleanup/{file_id}": "Limpiar archivos temporales",
                "GET /health": "Estado del servidor"
            },
            "supported_formats": list(config.SUPPORTED_FORMATS.keys())
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)