from io import BytesIO
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = FastAPI(title="Document Converter API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"service": "document-converter", "docs": "/docs", "health": "/health"}

@app.post("/convert/txt-to-pdf")
async def txt_to_pdf(file: UploadFile = File(...)):
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=415, detail="Only .txt files are supported.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Maximum upload size is 5 MB.")

    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    margin = 48
    y = height - margin
    line_height = 14
    max_chars = 95

    for paragraph in content.splitlines() or [""]:
        wrapped = [paragraph[i:i + max_chars] for i in range(0, max(len(paragraph), 1), max_chars)]
        for line in wrapped:
            if y < margin:
                pdf.showPage()
                y = height - margin
            pdf.drawString(margin, y, line)
            y -= line_height

    pdf.save()
    output.seek(0)
    output_name = filename.rsplit(".", 1)[0] + ".pdf"
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
