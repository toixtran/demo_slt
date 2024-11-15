from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sign_language_translator as slt
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

model = slt.models.ConcatenativeSynthesis(
    text_language="en", sign_language="pk-sl", sign_format="video"
)

model.sign_format = slt.SignFormatCodes.LANDMARKS
model.sign_embedding_model = "mediapipe-world"

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate/")
async def translate(text: str = Form(...)):
    try:
        sign = model.translate(text)
        gif_filename = f"static/{text.replace(' ', '_')}.gif"
        sign.save_animation(gif_filename, overwrite=True)
        return JSONResponse(content={"gif_path": f"/static/{text.replace(' ', '_')}.gif"})
    
    except Exception as e:
        return JSONResponse(content={"error": f"Error: {str(e)}"}, status_code=500)
