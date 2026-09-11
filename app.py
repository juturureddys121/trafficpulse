import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse


SCENARIOS = {
    "medical": {
        "intent": "Medical triage",
        "risk_level": "High",
        "risk_score": 92,
        "sources": [
            "Emergency guidance protocol",
            "Medication history review",
            "Environmental risk factors",
        ],
        "actions": [
            {
                "title": "Escalate to emergency triage",
                "detail": "Urgent symptoms need immediate clinical review. Confirm exact symptom timing and whether airway or breathing is affected.",
                "tag": "Critical",
            },
            {
                "title": "Gather medication and allergy data",
                "detail": "Pull the patient profile for inhalers, prescriptions, and known allergies before clinical handoff.",
                "tag": "Verify",
            },
            {
                "title": "Check for environmental triggers",
                "detail": "Heat, smoke, asthma triggers, or missed medication might be amplifying the risk. Flag these to the responder.",
                "tag": "Context",
            },
        ],
    },
    "traffic": {
        "intent": "Traffic & commute routing",
        "risk_level": "Medium",
        "risk_score": 68,
        "sources": ["Live traffic feed", "Road closure alert", "ETA model"],
        "actions": [
            {
                "title": "Recommend shortest reliable route",
                "detail": "Reroute away from roadworks, accidents, and school-zone congestion based on the current traffic pattern.",
                "tag": "Route",
            },
            {
                "title": "Adjust departure timing",
                "detail": "Add a 10-15 minute buffer to avoid missed appointments and reduce stress during peak congestion.",
                "tag": "Schedule",
            },
            {
                "title": "Surface alternate transit options",
                "detail": "Offer rail, rideshare, or walking alternatives if the chosen route is still likely to stall.",
                "tag": "Backup",
            },
        ],
    },
    "weather": {
        "intent": "Weather & safety alert",
        "risk_level": "Medium",
        "risk_score": 74,
        "sources": ["Weather alert feed", "Local risk map", "Travel board"],
        "actions": [
            {
                "title": "Issue proactive safety guidance",
                "detail": "Warn the user about heat, storms, or air-quality conditions and recommend protective measures.",
                "tag": "Safety",
            },
            {
                "title": "Adjust the plan to local conditions",
                "detail": "Shift outdoor tasks, travel windows, or dosing schedules to avoid avoidable risk exposure.",
                "tag": "Adaptive",
            },
            {
                "title": "Prepare contingency logistics",
                "detail": "Translate the weather risk into a fallback route, shelter plan, or delayed schedule.",
                "tag": "Contingency",
            },
        ],
    },
    "news": {
        "intent": "Information triage",
        "risk_level": "Low",
        "risk_score": 55,
        "sources": ["News feed", "Official alert bulletin", "Relevant local sources"],
        "actions": [
            {
                "title": "Summarize what matters first",
                "detail": "Separate trustworthy alerts from noise so the user gets the key facts without overload.",
                "tag": "Summarize",
            },
            {
                "title": "Map relevance to their context",
                "detail": "Tie the event to their home area, travel pattern, or personal risk factors to prioritize action.",
                "tag": "Context",
            },
            {
                "title": "Recommend the next practical step",
                "detail": "Translate the alert into an immediate action such as checking the route, preparing supplies, or contacting support.",
                "tag": "Action",
            },
        ],
    },
    "general": {
        "intent": "General intent mapping",
        "risk_level": "Moderate",
        "risk_score": 61,
        "sources": ["User context", "System check", "Operational guidance"],
        "actions": [
            {
                "title": "Clarify the request",
                "detail": "Turn vague input into a precise goal by asking for location, timeline, constraints, and available resources.",
                "tag": "Clarify",
            },
            {
                "title": "Rank next steps by urgency",
                "detail": "Prioritize safety risks, time sensitivity, and downstream dependencies before actioning the task.",
                "tag": "Prioritize",
            },
            {
                "title": "Hand off to the right service layer",
                "detail": "Route to the appropriate system: emergency, transport, weather, medical, or logistics support.",
                "tag": "Handoff",
            },
        ],
    },
}


def classify_input(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    normalized = text.lower()

    if (
        "chest pain" in normalized
        or "shortness of breath" in normalized
        or "asthma" in normalized
        or "medication" in normalized
        or "inhaler" in normalized
        or "doctor" in normalized
        or "symptom" in normalized
        or "allergy" in normalized
    ):
        choice = "medical"
    elif (
        "traffic" in normalized
        or "commute" in normalized
        or "route" in normalized
        or "roadwork" in normalized
        or "accident" in normalized
        or "delay" in normalized
        or "train" in normalized
        or "flight" in normalized
    ):
        choice = "traffic"
    elif (
        "weather" in normalized
        or "storm" in normalized
        or "heat advisory" in normalized
        or "flood" in normalized
        or "rain" in normalized
        or "cold" in normalized
    ):
        choice = "weather"
    elif (
        "news" in normalized
        or "headline" in normalized
        or "alert" in normalized
        or "breaking" in normalized
        or "update" in normalized
    ):
        choice = "news"
    else:
        choice = "general"

    scenario = SCENARIOS[choice]
    return {
        "intent": scenario["intent"],
        "risk_level": scenario["risk_level"],
        "risk_score": scenario["risk_score"],
        "sources": scenario["sources"],
    }


def build_action_plan(analysis: dict[str, Any]) -> list[dict[str, str]]:
    if analysis["intent"] == "Medical triage":
        return [
            {
                "title": "Escalate to emergency triage",
                "detail": "Urgent symptoms need immediate clinical review. Confirm exact symptom timing and whether airway or breathing is affected.",
                "tag": "Critical",
            },
            {
                "title": "Gather medication and allergy data",
                "detail": "Pull the patient profile for inhalers, prescriptions, and known allergies before clinical handoff.",
                "tag": "Verify",
            },
            {
                "title": "Check for environmental triggers",
                "detail": "Heat, smoke, asthma triggers, or missed medication might be amplifying the risk. Flag these to the responder.",
                "tag": "Context",
            },
        ]

    if analysis["intent"] == "Traffic & commute routing":
        return [
            {
                "title": "Recommend shortest reliable route",
                "detail": "Reroute away from roadworks, accidents, and school-zone congestion based on the current traffic pattern.",
                "tag": "Route",
            },
            {
                "title": "Adjust departure timing",
                "detail": "Add a 10-15 minute buffer to avoid missed appointments and reduce stress during peak congestion.",
                "tag": "Schedule",
            },
            {
                "title": "Surface alternate transit options",
                "detail": "Offer rail, rideshare, or walking alternatives if the chosen route is still likely to stall.",
                "tag": "Backup",
            },
        ]

    if analysis["intent"] == "Weather & safety alert":
        return [
            {
                "title": "Issue proactive safety guidance",
                "detail": "Warn the user about heat, storms, or air-quality conditions and recommend protective measures.",
                "tag": "Safety",
            },
            {
                "title": "Adjust the plan to local conditions",
                "detail": "Shift outdoor tasks, travel windows, or dosing schedules to avoid avoidable risk exposure.",
                "tag": "Adaptive",
            },
            {
                "title": "Prepare contingency logistics",
                "detail": "Translate the weather risk into a fallback route, shelter plan, or delayed schedule.",
                "tag": "Contingency",
            },
        ]

    if analysis["intent"] == "Information triage":
        return [
            {
                "title": "Summarize what matters first",
                "detail": "Separate trustworthy alerts from noise so the user gets the key facts without overload.",
                "tag": "Summarize",
            },
            {
                "title": "Map relevance to their context",
                "detail": "Tie the event to their home area, travel pattern, or personal risk factors to prioritize action.",
                "tag": "Context",
            },
            {
                "title": "Recommend the next practical step",
                "detail": "Translate the alert into an immediate action such as checking the route, preparing supplies, or contacting support.",
                "tag": "Action",
            },
        ]

    return [
        {
            "title": "Clarify the request",
            "detail": "Turn vague input into a precise goal by asking for location, timeline, constraints, and available resources.",
            "tag": "Clarify",
        },
        {
            "title": "Rank next steps by urgency",
            "detail": "Prioritize safety risks, time sensitivity, and downstream dependencies before actioning the task.",
            "tag": "Prioritize",
        },
        {
            "title": "Hand off to the right service layer",
            "detail": "Route to the appropriate system: emergency, transport, weather, medical, or logistics support.",
            "tag": "Handoff",
        },
    ]


class AppHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            payload = {"status": "ok"}
            self._send_json(payload)
            return

        if parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        if parsed.path.startswith("/") and "." in parsed.path.rsplit("/", 1)[-1]:
            try:
                with open(parsed.path.lstrip("/"), "rb") as f:
                    content = f.read()
                self.send_response(200)
                if parsed.path.endswith(".css"):
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                elif parsed.path.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, "File not found")
                return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/analyze":
            self.send_error(404, "Not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        text = payload.get("input", "")
        analysis = classify_input(text)
        actions = build_action_plan(analysis)
        result = {
            **analysis,
            "actions": actions,
            "timestamp": "Just now",
        }
        self._send_json(result)

    def _send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "0.0.0.0", port: int | None = None) -> None:
    if port is None:
        port = int(os.environ.get("PORT", "8000"))

    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Serving HTTP on {host} port {port} (http://{host}:{port}/)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
