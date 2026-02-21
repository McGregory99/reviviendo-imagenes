import os
import replicate
from dotenv import load_dotenv
import requests

load_dotenv("backend/.env")

class ReplicateService:
    def __init__(self):
        self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

    def colorize_img(self, image_path: str) -> str:
        # 1) Abrimos la imagen original en modo binario para enviarla a Replicate
        image = open(image_path, "rb")
        input = {
            "image": image
        }

        # 2) Llamamos al modelo de colorización y esperamos el resultado
        output = self.client.run(
            "piddnad/ddcolor:ca494ba129e44e45f661d6ece83c4c98a9a7c774309beca01429b58fce8aa695",
            input=input
        )
        # 3) Construimos el nombre del archivo de salida
        filename = os.path.basename(image_path).replace(".", "_colorized.")
        output_path = f"backend/temp/{filename}"

        # 4) Descargamos la imagen resultante desde la URL que devuelve Replicate
        response = requests.get(str(output))

        # 5) Guardamos la imagen colorizada en local
        with open(output_path, "wb") as f:
            f.write(response.content)        
        return output_path

    def img_to_vid(self, image_path: str, prompt: str) -> str:
        # 1) Abrimos la imagen original en modo binario para enviarla a Replicate
        image = open(image_path, "rb")
        input = {
            "image": image,
            "prompt": prompt
        }

        # 2) Llamamos al modelo de video y esperamos el resultado
        output = self.client.run(
            "wan-video/wan-2.5-i2v-fast",
            input=input
        )

        # 3) Construimos el nombre del archivo de salida
        filename = os.path.splitext(os.path.basename(image_path))[0] + "_video.mp4"
        output_path = f"backend/temp/{filename}"

        # 4) Descargamos el video resultante desde la URL que devuelve Replicate
        response = requests.get(str(output))

        # 5) Guardamos el video en local
        with open(output_path, "wb") as f:
            f.write(response.content)        
        return output_path
