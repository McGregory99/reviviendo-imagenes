import io
import os
import replicate
from dotenv import load_dotenv
import requests

load_dotenv("backend/.env")

class ReplicateService:
    def __init__(self):
        self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

    def colorize_img(self, image_bytes: bytes, original_filename: str) -> tuple[bytes, str]:
        # 1) Enviamos los bytes directamente a Replicate (sin guardar en disco)
        output = self.client.run(
            "piddnad/ddcolor:ca494ba129e44e45f661d6ece83c4c98a9a7c774309beca01429b58fce8aa695",
            input={"image": io.BytesIO(image_bytes)}
        )

        # 2) Construimos el nombre del archivo de salida
        name, ext = original_filename.rsplit(".", 1)
        filename = f"{name}_colorized.{ext}"

        # 3) Descargamos los bytes de la imagen colorizada desde Replicate
        response = requests.get(str(output))
        return response.content, filename


    def img_to_vid(self, image_url: str, prompt: str) -> tuple[bytes, str]:
        # 1) Pasamos la URL pública de Supabase Storage directamente a Replicate
        output = self.client.run(
            "wan-video/wan-2.5-i2v-fast",
            input={"image": image_url, "prompt": prompt}
        )

        # 2) Construimos el nombre del archivo de salida
        base = image_url.split("/")[-1].rsplit(".", 1)[0]
        filename = f"{base}_video.mp4"

        # 3) Descargamos los bytes del video desde Replicate
        response = requests.get(str(output))
        return response.content, filename
