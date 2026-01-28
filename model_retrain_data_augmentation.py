if __name__ == "__main__":
    from ultralytics import YOLO
    import torch
    import os

    #Use previous weights to save time
    data_yaml = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\data.yaml"
    model_weights = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\runs\detect\card_detector3\weights\last.pt"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nUsing device: {device}")

    #Load previous model
    print("\nLoading YOLOv8 model from previous weights...")
    model = YOLO(model_weights)

    print("\nContinuing training with data augmentations...")

    model.train(
        data=data_yaml,
        epochs=100,          # longer training for small object learning
        imgsz=640,           # larger image size helps detect smaller cards
        batch=16,
        device=device,
        name="card_detector_finetune_aug",
        #DATA AUGMENTATION
        augment=True,         # enable augmentations
        mosaic=True,          # combine 4 images into 1 (multi-scale learning)
        mixup=True,           # blend 2 images together
        flipud=0.5,           # vertical flip 50% of time
        fliplr=0.5,           # horizontal flip 50% of time
        hsv_h=0.015,          # hue change
        hsv_s=0.7,            # saturation change
        hsv_v=0.4,            # brightness/value change
        degrees=15.0,         # random rotation
        translate=0.2,        # translation
        scale=0.5,            # random scale
        shear=0.2,            # shear
    )

   #Validating model
    print("\n fine-tuned model performance...")
    results = model.val()
    print(results)

    #Testing on test set for accuracy 
    test_path = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\data\archive\test\images"
    print("\n Running predictions on test images...")
    model.predict(
        source=test_path,
        conf=0.35,    # lower confidence threshold to catch smaller cards
        save=True,
        show=False,
    )

    print("\nDone! Predictions saved in:")
    print(os.path.abspath("runs/detect/predict"))