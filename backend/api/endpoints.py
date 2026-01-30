from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
import traceback
import sys
import os

# Add parent directory to path so execution module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from execution.transcribe_video import get_transcription
from execution.extract_topics import extract_topics
from execution.research_topics import research_topics
from execution.generate_script import generate_video_script

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class VideoRequest(BaseModel):
    url: str

class TranscriptRequest(BaseModel):
    transcript_text: str

class TopicsRequest(BaseModel):
    topics: list[str]

class GenerateRequest(BaseModel):
    transcript_text: str
    research: str

# In-memory store per semplicità (in prod usare DB/Redis)
job_store = {}


# ============ STEP-BY-STEP ENDPOINTS ============

@router.post("/step/transcribe")
async def step_transcribe(request: VideoRequest):
    """Step 1: Trascrizione video YouTube"""
    try:
        logger.info(f"[Step] Starting transcription for: {request.url}")
        transcript_data = get_transcription(request.url)
        logger.info(f"[Step] Transcription complete. Length: {len(transcript_data['text'])} chars")
        return {
            "success": True,
            "data": transcript_data,
            "next_step": "extract_topics"
        }
    except Exception as e:
        logger.error(f"[Step] Transcription error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


@router.post("/step/extract-topics")
async def step_extract_topics(request: TranscriptRequest):
    """Step 2: Estrazione topics dalla trascrizione"""
    try:
        logger.info(f"[Step] Extracting topics from transcript ({len(request.transcript_text)} chars)")
        topics = extract_topics(request.transcript_text)
        logger.info(f"[Step] Topics extracted: {topics}")
        return {
            "success": True,
            "data": topics,
            "next_step": "research"
        }
    except Exception as e:
        logger.error(f"[Step] Topic extraction error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


@router.post("/step/research")
async def step_research(request: TopicsRequest):
    """Step 3: Ricerca approfondita sui topics"""
    try:
        logger.info(f"[Step] Researching topics: {request.topics}")
        research_report = research_topics(request.topics)
        logger.info(f"[Step] Research complete. Length: {len(research_report)} chars")
        return {
            "success": True,
            "data": research_report,
            "next_step": "generate_script"
        }
    except Exception as e:
        logger.error(f"[Step] Research error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


@router.post("/step/generate-script")
async def step_generate_script(request: GenerateRequest):
    """Step 4: Generazione script finale"""
    try:
        logger.info(f"[Step] Generating script from transcript and research")
        final_script = generate_video_script(request.transcript_text, request.research)
        logger.info(f"[Step] Script generation complete. Length: {len(final_script)} chars")
        return {
            "success": True,
            "data": final_script,
            "next_step": "completed"
        }
    except Exception as e:
        logger.error(f"[Step] Script generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ============ LEGACY ENDPOINTS (per compatibilità) ============

@router.post("/process-video")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(len(job_store) + 1)
    job_store[job_id] = {"step": "queued", "logs": []}
    
    background_tasks.add_task(run_full_pipeline, job_id, request.url)
    
    return {"job_id": job_id, "status": "queued"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_store[job_id]

def run_full_pipeline(job_id: str, url: str):
    try:
        logger.info(f"[Job {job_id}] Starting transcription...")
        job_store[job_id]["step"] = "transcribing"
        transcript_data = get_transcription(url)
        job_store[job_id]["transcript"] = transcript_data
        
        logger.info(f"[Job {job_id}] Starting topic extraction...")
        job_store[job_id]["step"] = "extracting_topics"
        topics = extract_topics(transcript_data["text"])
        job_store[job_id]["topics"] = topics
        
        logger.info(f"[Job {job_id}] Starting research...")
        job_store[job_id]["step"] = "researching"
        research_report = research_topics(topics)
        job_store[job_id]["research"] = research_report
        
        logger.info(f"[Job {job_id}] Starting script generation...")
        job_store[job_id]["step"] = "generating_script"
        final_script = generate_video_script(transcript_data["text"], research_report)
        job_store[job_id]["final_script"] = final_script
        
        job_store[job_id]["step"] = "completed"
        logger.info(f"[Job {job_id}] Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        logger.error(traceback.format_exc())
        job_store[job_id]["step"] = "error"
        job_store[job_id]["error"] = str(e)
