from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry JSON file
TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(TELEMETRY_FILE, "r") as f:
    telemetry_data = json.load(f)

@app.post("/api/index")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("region", [])         # e.g. ["apac", "emea"]
    services = body.get("service", [])       # optional filter, e.g. ["checkout", "support"]
    threshold = body.get("latency_ms", 180)  # default threshold

    response = {}

    for region in regions:
        # Filter by region (and service if provided)
        region_data = [r for r in telemetry_data if r["region"] == region]
        if services:
            region_data = [r for r in region_data if r["service"] in services]

        if not region_data:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue

        latencies = np.array([r["latency_ms"] for r in region_data])
        uptimes = np.array([r["uptime_pct"] for r in region_data])

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(np.sum(latencies > threshold)),
            "samples": len(region_data),
        }

    return JSONResponse(response)
