from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os
from app.services.replicate_service import ReplicateService
from app.services.supabase_service import SupabaseService

app = FastAPI(title="Reviviendo Imagenes")

# Instanciamos el servicio una sola vez
replicate_service = ReplicateService()
supabase_service = SupabaseService()
security = HTTPBearer()

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase_service.get_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get('/')
def root():
    return {"message": "Hello World"}

@app.get('/health')
def health():
    return {"message": "healthy"}

@app.post('/colorize')
async def colorize(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    # 1) Leemos los bytes de la imagen subida (sin guardar en disco)
    image_bytes = await file.read()

    # 2) Llamamos a Replicate y obtenemos los bytes de la imagen colorizada
    result_bytes, filename = replicate_service.colorize_img(image_bytes, file.filename)

    # 3) Subimos la imagen colorizada a Supabase Storage
    storage_path = f"{current_user.id}/{filename}"
    public_url = supabase_service.upload_file(storage_path, result_bytes, "image/jpeg")

    # 4) Guardamos la transformación en la tabla transformations
    transformation_id = supabase_service.save_colorization(current_user.id, file.filename, public_url)

    return {"image_url": public_url, "transformation_id": transformation_id}
    
@app.post('/generate-video')
async def generate_video(colorized_url: str = Form(...), prompt: str = Form(...), current_user = Depends(get_current_user), transformation_id: str = Form(...)):
    # 1) Pasamos la URL pública de la imagen a Replicate y obtenemos los bytes del video
    result_bytes, filename = replicate_service.img_to_vid(colorized_url, prompt)

    # 2) Subimos el video a Supabase Storage
    storage_path = f"{current_user.id}/{filename}"
    public_url = supabase_service.upload_file(storage_path, result_bytes, "video/mp4")

    # 3) Actualizamos la transformación con la URL del video
    supabase_service.save_video(transformation_id, public_url)

    return {"video_url": public_url}

@app.get('/transformations')
def get_transformations(current_user = Depends(get_current_user)):
    return supabase_service.get_transformations(current_user.id)
