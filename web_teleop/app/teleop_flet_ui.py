import flet as ft
from flet import (
    Page, Container, Stack, CircleAvatar, Colors, alignment, app, border, Text,
    GestureDetector
)
import math
import threading
import websocket
import json
import time

# === Configuration ===
ROSBRIDGE_URI = "ws://localhost:9090"
CMD_VEL_TOPIC = "/cmd_vel"
CMD_VEL_TYPE = "geometry_msgs/msg/Twist"
MAX_LINEAR_SPEED = 0.5
MAX_ANGULAR_SPEED = 0.3
JOYSTICK_RADIUS = 120
KNOB_RADIUS = 40
UPDATE_INTERVAL = 0.05

# === Global control flags ===
joystick_state = {"x": 0.0, "y": 0.0, "active": False}
shutdown_event = threading.Event()
ws_connection = None  # We'll hold the connection here


def rosbridge_publisher():
    global ws_connection
    try:
        ws = websocket.WebSocket()
        ws.connect(ROSBRIDGE_URI)
        ws_connection = ws

        # Advertise message type
        advertise_msg = {
            "op": "advertise",
            "topic": CMD_VEL_TOPIC,
            "type": CMD_VEL_TYPE
        }
        ws.send(json.dumps(advertise_msg))

        while not shutdown_event.is_set():
            if joystick_state["active"]:
                dx = joystick_state["x"] / (JOYSTICK_RADIUS - KNOB_RADIUS)
                dy = joystick_state["y"] / (JOYSTICK_RADIUS - KNOB_RADIUS)
                dx = max(min(dx, 1.0), -1.0)
                dy = max(min(dy, 1.0), -1.0)
                linear_x = -dy * MAX_LINEAR_SPEED
                angular_z = dx * MAX_ANGULAR_SPEED
            else:
                linear_x = 0.0
                angular_z = 0.0

            msg = {
                "op": "publish",
                "topic": CMD_VEL_TOPIC,
                "msg": {
                    "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
                    "angular": {"x": 0.0, "y": 0.0, "z": angular_z}
                }
            }
            ws.send(json.dumps(msg))
            time.sleep(UPDATE_INTERVAL)

        # Send unadvertise when done
        unadv_msg = {
            "op": "unadvertise",
            "topic": CMD_VEL_TOPIC
        }
        ws.send(json.dumps(unadv_msg))
        ws.close()
        print("WebSocket closed cleanly.")

    except Exception as e:
        print("WebSocket error:", e)


def main(page: Page):
    page.title = "ROS2 Joystick Controller"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.bgcolor = Colors.BLACK

    knob = CircleAvatar(radius=KNOB_RADIUS, bgcolor=Colors.BLUE, content=Text(" "))

    def update_knob_position(x, y):
        knob.offset = ft.transform.Offset(x / JOYSTICK_RADIUS, y / JOYSTICK_RADIUS)
        knob.update()

    def on_pan_start(e):
        joystick_state["active"] = True

    def on_pan_update(e):
        x = e.local_x - JOYSTICK_RADIUS
        y = e.local_y - JOYSTICK_RADIUS
        dist = math.sqrt(x * x + y * y)
        if dist > (JOYSTICK_RADIUS - KNOB_RADIUS):
            scale = (JOYSTICK_RADIUS - KNOB_RADIUS) / dist
            x *= scale
            y *= scale
        joystick_state["x"] = x
        joystick_state["y"] = y
        update_knob_position(x, y)

    def on_pan_end(e):
        joystick_state["active"] = False
        joystick_state["x"] = 0.0
        joystick_state["y"] = 0.0
        update_knob_position(0, 0)

    def on_shutdown(e):
        print("Shutting down...")
        shutdown_event.set()

    # Shutdown hook (for browser close or ctrl+c)
    page.on_disconnect = on_shutdown
    page.on_window_event = lambda e: on_shutdown(e) if e.data == "close" else None

    joystick_pad = Container(
        width=JOYSTICK_RADIUS * 2,
        height=JOYSTICK_RADIUS * 2,
        bgcolor=Colors.with_opacity(0.2, Colors.WHITE),
        border=border.all(2, Colors.BLUE_GREY),
        border_radius=JOYSTICK_RADIUS,
        alignment=alignment.center,
        content=Stack([knob])
    )

    joystick = GestureDetector(
        content=joystick_pad,
        on_pan_start=on_pan_start,
        on_pan_update=on_pan_update,
        on_pan_end=on_pan_end
    )

    page.add(joystick)

    threading.Thread(target=rosbridge_publisher, daemon=True).start()


app(target=main, port=8550, view=ft.WEB_BROWSER)
