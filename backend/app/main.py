from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.services.replicate_service import ReplicateService

app = FastAPI(title="Reviviendo Imagenes")

# Instanciamos el servicio una sola vez
replicate_service = ReplicateService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montamos la carpeta temp para poder acceder a los archivos
os.makedirs("backend/temp", exist_ok=True)
app.mount("/temp", StaticFiles(directory="backend/temp"), name="temp")

@app.get('/')
def root():
    return {"message": "Hello World"}

@app.get('/health')
def health():
    return {"message": "healthy"}

@app.post('/colorize')
async def colorize(file: UploadFile = File(...)):
    # 1) Guardamos la imagen subida por el usuario
    upload_path = f"backend/temp/{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(file.file.read())
    
    # 2) Llamamos al servicio de Replicate
    output_path = replicate_service.colorize_img(upload_path)

    # 3) Devolvemos la imagen colorizada al frontend
    return {"image_url": f"/temp/{os.path.basename(output_path)}"}
    
@app.post('/generate-video')
async def generate_video(colorized_url: str = Form(...), prompt: str = Form(...)):
    # 1) Construir el nombre del fichero
    filename = os.path.basename(colorized_url)
    upload_path = f"backend/temp/{filename}"
    
    # 2) Llamamos al servicio de Replicate
    video_path = replicate_service.img_to_vid(upload_path, prompt)

    # 3) Devolvemos la imagen colorizada al frontend
    return {"video_url": f"/temp/{os.path.basename(video_path)}"}
