# Audio Extractor API 🎵

Una API REST construida con FastAPI para extraer audio de archivos de video usando FFmpeg.

## 🚀 Características

- **Extracción de audio**: Convierte archivos de video a audio en múltiples formatos
- **Formatos soportados**: MP3, WAV, OGG, AAC, FLAC
- **API REST**: Interfaz simple y documentada
- **Validaciones**: Verificación de tipo de archivo y tamaño
- **Limpieza automática**: Gestión de archivos temporales
- **Logging**: Sistema de logs detallado
- **Configuración flexible**: Variables de entorno

## 📋 Requisitos

### Sistema
- Python 3.7+
- FFmpeg instalado y accesible desde PATH

### Instalación de FFmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
Descargar desde [FFmpeg oficial](https://ffmpeg.org/download.html) y agregar al PATH

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/audio-extractor-api.git
cd audio-extractor-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional)**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🚀 Uso

### Iniciar el servidor
```bash
python app.py
```

El servidor estará disponible en `http://localhost:8001`

### 🎯 Interfaz Web
Abre tu navegador y ve a: **http://localhost:8001**

La interfaz web te permite:
- ✅ **Arrastrar y soltar** archivos de video
- ✅ **Seleccionar formato** de audio (MP3, WAV, OGG, AAC, FLAC)
- ✅ **Vista previa** del video antes de extraer
- ✅ **Descarga automática** del audio extraído
- ✅ **Barra de progreso** durante el procesamiento

### 📡 API REST

#### 1. Interfaz web
```http
GET /
```

#### 2. Extraer audio
```http
POST /extract-audio
Content-Type: multipart/form-data

file: [archivo_video]
format: mp3  # opcional, por defecto mp3
```

**Formatos soportados**: `mp3`, `wav`, `ogg`, `aac`, `flac`

#### 3. Estado del servidor
```http
GET /health
```

#### 4. Limpiar archivos temporales
```http
GET /cleanup/{file_id}
```

### Ejemplo con curl
```bash
curl -X POST "http://localhost:8001/extract-audio" \
  -H "accept: audio/mpeg" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@video.mp4" \
  -F "format=mp3" \
  --output audio.mp3
```

### Ejemplo con Python
```python
import requests

url = "http://localhost:8001/extract-audio"
files = {"file": open("video.mp4", "rb")}
data = {"format": "mp3"}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("audio.mp3", "wb") as f:
        f.write(response.content)
    print("Audio extraído exitosamente")
else:
    print(f"Error: {response.text}")
```

## ⚙️ Configuración

### Variables de entorno (.env)
```bash
# Servidor
HOST=0.0.0.0
PORT=8001

# Procesamiento de archivos
MAX_FILE_SIZE=524288000  # 500MB
TEMP_DIR=temp_files

# FFmpeg
FFMPEG_TIMEOUT=300  # 5 minutos

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/audio_extractor.log
```

### Estructura del proyecto
```
audio-extractor-api/
├── app.py              # Aplicación principal
├── config.py           # Configuración
├── requirements.txt    # Dependencias
├── .env.example       # Ejemplo de variables de entorno
├── .gitignore         # Archivos a ignorar en git
├── README.md          # Este archivo
├── static/            # Archivos estáticos
│   └── index.html     # Interfaz web
├── temp_files/        # Archivos temporales (creado automáticamente)
└── logs/              # Logs de la aplicación (creado automáticamente)
```

## 📊 Límites y restricciones

- **Tamaño máximo de archivo**: 500MB (configurable)
- **Timeout de FFmpeg**: 5 minutos (configurable)
- **Tipos de archivo soportados**: Todos los formatos de video comunes
- **Formatos de salida**: MP3, WAV, OGG, AAC, FLAC

## 🔒 Seguridad

- Validación de tipos de archivo
- Límites de tamaño
- Limpieza automática de archivos temporales
- Timeout para prevenir procesos colgados
- CORS configurado

## 🐛 Solución de problemas

### Error: "FFmpeg no encontrado"
- Verificar que FFmpeg esté instalado: `ffmpeg -version`
- Asegurarse de que esté en el PATH del sistema

### Error: "Archivo demasiado grande"
- Ajustar `MAX_FILE_SIZE` en `.env`
- Verificar espacio en disco disponible

### Error: "Timeout en procesamiento"
- Aumentar `FFMPEG_TIMEOUT` en `.env`
- Verificar recursos del sistema

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🚀 Despliegue

### Docker (próximamente)
```bash
docker build -t audio-extractor .
docker run -p 8001:8001 audio-extractor
```

### Heroku/Railway/etc
1. Configurar buildpack de Python
2. Instalar buildpack de FFmpeg
3. Configurar variables de entorno
4. Deploy

## 📈 Roadmap

- [x] ~~Interfaz web opcional~~ ✅ **Completado**
- [ ] Soporte para Docker
- [ ] Procesamiento en lotes
- [ ] Autenticación API
- [ ] Métricas y monitoreo
- [ ] Soporte para más formatos de salida

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) por el framework web
- [FFmpeg](https://ffmpeg.org/) por el procesamiento de media
- Comunidad de código abierto por las herramientas utilizadas