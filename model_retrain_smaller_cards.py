if __name__ == "__main__":
    from ultralytics import YOLO
    import torch
    import os

    
    data_yaml = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\data.yaml"
    model_weights = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\runs\detect\card_detector_finetune_aug\weights\best.pt"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n Using device: {device}")

    
    print("\n Loading YOLOv8 model from previous weights...")
    model = YOLO(model_weights)

   
    print("\n Continuing training with data augmentations for small cards...")
    model.train(
        data=data_yaml,
        epochs=150,           # longer training for small object learning
        imgsz=720,            # increase image size to make small cards more visible
        batch=12,             # reduce batch to fit larger imgsz in GPU memory
        device=device,
        name="card_detector_finetune_small_cards",
        #DATA AUGMENTATION
        augment=True,         
        mosaic=True,          # combine 4 images into 1 (multi-scale)
        mixup=True,           
        flipud=0.5,          
        fliplr=0.5,          
        hsv_h=0.015,         
        hsv_s=0.7,           
        hsv_v=0.4,           
        degrees=15.0,        
        translate=0.2,       
        scale=0.3,           # reduce scale to simulate smaller cards
        shear=0.2,           
    )

    
    print("\n Validating fine-tuned model performance...")
    results = model.val()
    print(results)

    
    test_path = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\test\images"
    print("\n Running predictions on test images...")
    model.predict(
        source=test_path,
        conf=0.25,   # lower confidence threshold to catch smaller cards
        save=True,
        show=False,
    )

    print("\n Done! Predictions saved in:")
    print(os.path.abspath("runs/detect/predict"))
