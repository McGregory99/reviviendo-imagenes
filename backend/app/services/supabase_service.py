import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv('backend/.env')

class SupabaseService:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL")
        self.key: str = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.url, self.key)

    def get_user(self, token: str):
        return self.client.auth.get_user(token).user

    def upload_file(self, path: str, file_bytes: bytes, content_type: str) -> str:
        self.client.storage.from_("media").upload(
            path, file_bytes, {"content-type": content_type, "upsert": "true"}
        )
        return self.client.storage.from_("media").get_public_url(path)    

    def save_colorization(self, user_id: str, original_filename: str, colorized_url: str) -> str:
        result = self.client.table("transformations").insert({
            "user_id": user_id,
            "original_filename": original_filename,
            "colorized_url": colorized_url,
        }).execute()
        return result.data[0]["id"]   

    def save_video(self, transformation_id: str, video_url: str) -> str:
        result = self.client.table("transformations").update({
            "video_url": video_url
        }).eq("id", transformation_id).execute()

    def get_transformations(self, current_user_id: str):
        return self.client.table("transformations").select("*").eq("user_id", current_user_id).execute().data