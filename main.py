from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import random
import httpx

app = FastAPI()

# === Models ===

class Observation(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    name: str
    status: str  # "Success" or "Failed"

class ObservationUpdate(Observation):
    problem_report: Optional[str] = None
    investigation_report: Optional[str] = None

class GenerateRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    base_name: str

# === In-memory store ===
observations_db: List[ObservationUpdate] = []
investigation_reports_db: List[dict] = []

# === Helpers ===

def generate_problem_report_id():
    return f"PR-{uuid.uuid4().hex[:6].upper()}"

def generate_observations(start: datetime, end: datetime, base_name: str) -> List[ObservationUpdate]:
    observations = []
    current_time = start
    counter = 1

    while current_time < end:
        duration = timedelta(minutes=random.randint(5, 15))
        obs_end = current_time + duration
        if obs_end > end:
            break

        status = "Success" if random.choice([True, False]) else "Failed"

        observation = ObservationUpdate(
            id=str(uuid.uuid4()),
            start_time=current_time,
            end_time=obs_end,
            name=f"{base_name}_{counter}",
            status=status
        )

        observations.append(observation)
        current_time = obs_end
        counter += 1

    return observations

# === API ROUTES ===

@app.post("/observations/generate", response_model=List[ObservationUpdate])
def generate_and_store_observations(req: GenerateRequest):
    global observations_db
    observations_db = generate_observations(req.start_time, req.end_time, req.base_name)
    return observations_db

@app.get("/observations", response_model=List[Observation])
def load_observations():
    return [Observation(**obs.dict()) for obs in observations_db]

@app.get("/observations/full", response_model=List[ObservationUpdate])
def get_observations_full():
    return observations_db

@app.get("/observations/{obs_id}", response_model=Observation)
def get_observation(obs_id: str):
    obs = next((o for o in observations_db if o.id == obs_id), None)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return Observation(**obs.dict())

@app.put("/observations/{obs_id}/update_problem_report", response_model=ObservationUpdate)
def update_observation(obs_id: str, problem_report_ticket: str):
    for obs in observations_db:
        if obs.id == obs_id:
            if obs.status == "Success":
                raise HTTPException(status_code=400, detail="Cannot add a problem report to a successful observation")
            obs.problem_report = problem_report_ticket
            return obs
    raise HTTPException(status_code=404, detail="Observation not found")

@app.delete("/observations/{obs_id}/remove_problem_report", response_model=ObservationUpdate)
def remove_problem_report_ticket(obs_id: str):
    for obs in observations_db:
        if obs.id == obs_id:
            obs.problem_report = None
            return obs
    raise HTTPException(status_code=404, detail="Observation not found")

@app.post("/observations/generate_problem_reports", response_model=List[ObservationUpdate])
def assign_problem_reports():
    for obs in observations_db:
        if obs.status == "Success":
            obs.problem_report = None
        else:
            obs.problem_report = generate_problem_report_id() if random.random() < 0.5 else None
    return observations_db

@app.post("/observations/assign_investigations", response_model=dict)
def assign_investigation_reports():
    global investigation_reports_db

    def random_datetime():
        now = datetime.now()
        days_back = random.randint(0, 365)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        return now - timedelta(days=days_back, hours=hours_offset, minutes=minutes_offset)

    lorem_ipsum_texts = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
        "Excepteur sint occaecat cupidatat non proident.",
        "Curabitur pretium tincidunt lacus. Nulla gravida orci a odio.",
        "Praesent placerat risus quis eros.",
        "Vestibulum commodo felis quis tortor.",
        "Ut aliquam sollicitudin leo.",
        "Cras iaculis ultricies nulla."
    ]

    def generate_reports(n=20):
        reports = []
        for _ in range(n):
            start = random_datetime()
            end = start + timedelta(hours=random.randint(1, 72))
            report = {
                "id": f"INV-{uuid.uuid4().hex[:6].upper()}",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "investigation": random.choice(lorem_ipsum_texts)
            }
            reports.append(report)
        return reports

    #Store the generated reports globally
    investigation_reports_db = generate_reports(20)

    assigned = 0
    for obs in observations_db:
        if obs.problem_report:
            if random.random() < 0.6:
                selected = random.choice(investigation_reports_db)
                obs.investigation_report = selected["id"]
                assigned += 1
            else:
                obs.investigation_report = None

    return {
        "message": f"✅ Investigation reports dynamically generated and randomly assigned to {assigned} observations."
    }



# === TOTAL TIME CALCULATIONS ===

FASTAPI_1_URL = "http://127.0.0.1:8000"

async def calculate_total_downtime(start_time: datetime, end_time: datetime):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_1_URL}/observations/full")
        observations = response.json()

    return sum(
        (datetime.fromisoformat(obs["end_time"]) - datetime.fromisoformat(obs["start_time"])).total_seconds()
        for obs in observations
        if obs["status"] == "Failed" and start_time <= datetime.fromisoformat(obs["start_time"]) <= end_time
    )

async def calculate_total_observed_time(start_time: datetime, end_time: datetime):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_1_URL}/observations/full")
        observations = response.json()

    return sum(
        (datetime.fromisoformat(obs["end_time"]) - datetime.fromisoformat(obs["start_time"])).total_seconds()
        for obs in observations
        if obs["status"] == "Success" and start_time <= datetime.fromisoformat(obs["start_time"]) <= end_time
    )

async def calculate_total_reported_time(start_time: datetime, end_time: datetime):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_1_URL}/observations/full")
        observations = response.json()

    return sum(
        (datetime.fromisoformat(obs["end_time"]) - datetime.fromisoformat(obs["start_time"])).total_seconds()
        for obs in observations
        if obs["status"] == "Failed" and obs.get("problem_report") and start_time <= datetime.fromisoformat(obs["start_time"]) <= end_time
    )


@app.get("/total_downtime_time/")
async def get_total_downtime_time(start_time: datetime, end_time: datetime):
    total = await calculate_total_downtime(start_time, end_time)
    return {"total_downtime_time_seconds": total}

@app.get("/total_observation_time/")
async def get_total_observation_time(start_time: datetime, end_time: datetime):
    total = await calculate_total_observed_time(start_time, end_time)
    return {"total_observation_time_seconds": total}

@app.get("/total_reported_time/")
async def get_total_reported_time(start_time: datetime, end_time: datetime):
    total = await calculate_total_reported_time(start_time, end_time)
    return {"total_reported_time_seconds": total}


