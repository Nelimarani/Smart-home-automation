"""
Smart Home Automation System
A Flask web app that simulates controlling home appliances (lights, fan, AC, etc.)
remotely through a dashboard — the software layer of an IoT automation system.

In a full hardware deployment, each toggle below would publish an MQTT message
to a broker, which a microcontroller (e.g., ESP8266/Arduino) subscribes to and
uses to physically switch a relay connected to the appliance.
"""

from flask import Flask, render_template, jsonify, request
import datetime

app = Flask(__name__)

# In-memory device state (in production this would live in a database
# and be synced with real devices via MQTT)
devices = {
    "living_room_light": {"name": "Living Room Light", "status": False, "room": "Living Room"},
    "bedroom_light":     {"name": "Bedroom Light",      "status": False, "room": "Bedroom"},
    "fan":               {"name": "Fan",                "status": False, "room": "Living Room"},
    "ac":                {"name": "Air Conditioner",    "status": False, "room": "Bedroom"},
    "main_door_lock":    {"name": "Main Door Lock",     "status": True,  "room": "Entrance"},
}

activity_log = []


def log_activity(device_id, new_status):
    """Keep a simple activity log, similar to what a real automation
    dashboard would show for auditing device changes."""
    activity_log.insert(0, {
        "device": devices[device_id]["name"],
        "status": "ON" if new_status else "OFF",
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    })
    # keep only the last 10 events
    del activity_log[10:]


@app.route("/")
def index():
    return render_template("index.html", devices=devices, log=activity_log)


@app.route("/toggle/<device_id>", methods=["POST"])
def toggle_device(device_id):
    """Flip a device's ON/OFF state.
    This is the function that, in the hardware version of this project,
    would publish an MQTT message like: mqtt_client.publish(device_id, payload)
    """
    if device_id in devices:
        devices[device_id]["status"] = not devices[device_id]["status"]
        log_activity(device_id, devices[device_id]["status"])
        return jsonify({"success": True, "status": devices[device_id]["status"]})
    return jsonify({"success": False, "error": "Device not found"}), 404


@app.route("/voice-command", methods=["POST"])
def voice_command():
    """Simulates a voice-controlled command, e.g. 'turn on the fan'.
    A real voice integration (Google Assistant / Alexa skill) would call
    this same endpoint after parsing the spoken command into an intent."""
    command = request.json.get("command", "").lower()
    action_taken = None

    for device_id, device in devices.items():
        if device["name"].lower() in command:
            if "on" in command:
                devices[device_id]["status"] = True
                action_taken = f"Turned ON {device['name']}"
            elif "off" in command:
                devices[device_id]["status"] = False
                action_taken = f"Turned OFF {device['name']}"
            if action_taken:
                log_activity(device_id, devices[device_id]["status"])
            break

    if action_taken:
        return jsonify({"success": True, "message": action_taken})
    return jsonify({"success": False, "message": "Sorry, I couldn't understand that command."})


if __name__ == "__main__":
    app.run(debug=True)