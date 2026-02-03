
import tempfile
import os
from telegram_client import send_image
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Human Detection Bot API")

@app.post("/send/image")
async def send_image_endpoint(file: UploadFile = File(...)):
    # Guardar imagen temporalmente
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # Enviar a Telegram
    await send_image(
        temp_path,
        caption="🚨 Humano detectado"
    )

    # Limpiar
    os.remove(temp_path)

    return {"status": "ok"}