import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from openai import OpenAI

app = FastAPI(title="AI $(echo $project | sed 's/ai-//' | tr '-' ' ' | sed 's/.*/\U&/' | tr -d ' ')", description="AI-powered solution")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", os.getenv("DEEPSEEK_API_KEY")))

class ProcessRequest(BaseModel):
    input: str
    context: Optional[str] = None
    options: Optional[dict] = None

class ProcessResponse(BaseModel):
    result: str
    confidence: float
    metadata: dict

@app.get("/")
async def root():
    return {"status": "healthy", "service": "$project"}

@app.post("/api/process", response_model=ProcessResponse)
async def process(request: ProcessRequest):
    prompt = f"""{request.input}
Context: {request.context or 'No additional context'}
Options: {json.dumps(request.options) if request.options else 'Default'}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a professional AI assistant. Provide accurate, helpful responses."},
                    {"role": "user", "content": prompt}]
    )
    
    return ProcessResponse(
        result=response.choices[0].message.content,
        confidence=0.95,
        metadata={"model": "gpt-4o", "tokens": response.usage.total_tokens}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
