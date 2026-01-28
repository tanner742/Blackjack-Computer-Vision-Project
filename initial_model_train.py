if __name__ == "__main__":
    from ultralytics import YOLO
    import torch
    import os

    data_yaml = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\data.yaml"
    model_name = "yolov8s.pt"  

    model = YOLO(model_name)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n Using device: {device}")

    model.train(
        data=data_yaml,
        epochs=50,
        imgsz=416,
        batch=16,
        device=device,
        name="card_detector",
    )

    print("\n Validating model performance...")
    results = model.val()
    print(results)

    test_path = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\test\images"
    print("\n Running predictions on test images...")
    model.predict(
        source=test_path,
        conf=0.5,
        save=True,
        show=False,
    )

    print("\n Done! Predictions saved in:")
    print(os.path.abspath("runs/detect/predict"))