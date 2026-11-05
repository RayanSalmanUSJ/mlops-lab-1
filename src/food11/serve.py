import os
import io
import mlflow
import torch
from fastapi import FastAPI, UploadFile, File
from PIL import Image
from torchvision import transforms

# Read tracking URI from environment, defaulting to local server
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(tracking_uri)

# Load the model via MLflow's PyFunc wrapper using the alias
model = mlflow.pyfunc.load_model("models:/food11@champion")

app = FastAPI()

# Recreate the exact same transformations used during training
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Process the uploaded file
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Transform and convert to numpy array (MLflow PyFunc requirement)
    input_tensor = transform(image).unsqueeze(0).numpy()

    # Run inference
    predictions = model.predict(input_tensor)
    
    # Convert raw output logits into probabilities
    probs = torch.nn.functional.softmax(torch.tensor(predictions[0]), dim=0)
    confidence, predicted_class = torch.max(probs, 0)
    
    return {
        "category": predicted_class.item(),
        "confidence": confidence.item()
    }