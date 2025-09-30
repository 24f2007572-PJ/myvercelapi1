from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the telemetry bundle sample
with open("q-vercel-latency.json") as f:
    telemetry = pd.DataFrame(json.load(f))

@app.route("/api/index", methods=["POST"])
def telemetry_endpoint():
    data = request.get_json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    response = {}

    for region in regions:
        df_region = telemetry[telemetry["region"] == region]
        if df_region.empty:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = df_region["latency_ms"]
        uptimes = df_region["uptime"]

        response[region] = {
            "avg_latency": latencies.mean(),
            "p95_latency": np.percentile(latencies, 95),
            "avg_uptime": uptimes.mean(),
            "breaches": (latencies > threshold).sum()
        }

    return jsonify(response)
from flask import Flask
from flask_cors import CORS
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

# Load telemetry JSON
TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(TELEMETRY_FILE, "r") as f:
    telemetry_data = json.load(f)

@app.post("/")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    response = {}
    for region in regions:
        region_data = [r for r in telemetry_data if r["region"] == region]
        if not region_data:
            response[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue

        latencies = np.array([r["latency_ms"] for r in region_data])
        uptimes = np.array([r["uptime_pct"] for r in region_data])

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(np.sum(latencies > threshold))
        }

    return JSONResponse(response)
