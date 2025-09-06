# System Monitoring API

A simple FastAPI application that tracks system observations, manages incident reports, and calculates uptime metrics.

## Features

- Generate random system observations (success/failure)
- Assign problem reports to failed observations  
- Link investigation reports to incidents
- Calculate total uptime, downtime, and reported time
- RESTful API with automatic documentation

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dignacz/observation-monitoring.git
   cd observation-monitoring
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Open the UI in your browser:**
   - **Main UI (Interactive API docs):** http://127.0.0.1:8000/docs
   - **Alternative docs:** http://127.0.0.1:8000/redoc
   
   The FastAPI docs provide a beautiful interface where you can test all endpoints directly!

## Using the API UI

1. **Go to:** http://127.0.0.1:8000/docs
2. **Generate test data:** Use the `POST /observations/generate` endpoint with:
   ```json
   {
     "start_time": "2024-01-01T00:00:00",
     "end_time": "2024-01-01T12:00:00",
     "base_name": "health_check"
   }
   ```
3. **View your data:** Use `GET /observations` to see the generated observations
4. **Try other endpoints:** Generate problem reports, calculate metrics, etc.

## Example Usage

1. **Generate test data:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/observations/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "start_time": "2024-01-01T00:00:00",
       "end_time": "2024-01-01T12:00:00", 
       "base_name": "health_check"
     }'
   ```

2. **View observations:**
   ```bash
   curl "http://127.0.0.1:8000/observations"
   ```

3. **Generate problem reports:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/observations/generate_problem_reports"
   ```

4. **Get downtime metrics:**
   ```bash
   curl "http://127.0.0.1:8000/total_downtime_time/?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59"
   ```

## API Endpoints

- `POST /observations/generate` - Generate random observations
- `GET /observations` - Get all observations
- `GET /observations/{id}` - Get specific observation
- `POST /observations/generate_problem_reports` - Assign problem reports
- `POST /observations/assign_investigations` - Assign investigation reports
- `GET /total_downtime_time/` - Calculate downtime
- `GET /total_observation_time/` - Calculate uptime  
- `GET /total_reported_time/` - Calculate reported incident time

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **HTTPX** - Async HTTP client

Perfect for demonstrating API development, async programming, and system monitoring concepts.