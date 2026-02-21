from app.services.replicate_service import ReplicateService

def main():
    replicate_service = ReplicateService()
    # replicate_service.colorize_img("./backend/byn8.jpg")
    # replicate_service.colorize_img("./byn9.jpg")
    replicate_service.img_to_vid(
        "./backend/temp/byn8_colorized.jpg",
        "A girl drinking a cup a tea"
    )

if __name__ == "__main__":
    main()