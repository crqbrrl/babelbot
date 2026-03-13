"""
BabelBot - Robot Control Module
Handles: command dict → Cyberwave SDK → Unitree Go2 moves

DEV 1: This is YOUR file. Replace the placeholder functions
with real Cyberwave SDK calls based on what's available at the hackathon.

Cyberwave Python SDK docs: https://github.com/cyberwave-os/cyberwave-python
Unitree Go2 SDK: https://github.com/unitreerobotics/unitree_sdk2_python
"""

from cyberwave import Cyberwave
from config import CYBERWAVE_API_KEY, ROBOT_ASSET_ID, ENVIRONMENT_ID
import time

# ============================================================
# INITIALIZE CYBERWAVE
# ============================================================
cw = Cyberwave(api_key=CYBERWAVE_API_KEY)

# Create or connect to the Go2 digital twin
# Adjust the asset ID based on what Cyberwave provides at the hackathon
robot = None

def init_robot():
    """
    Initialize connection to the Unitree Go2 via Cyberwave.
    Call this once at startup.
    """
    global robot
    try:
        if ENVIRONMENT_ID:
            robot = cw.twin(ROBOT_ASSET_ID, environment_id=ENVIRONMENT_ID)
        else:
            robot = cw.twin(ROBOT_ASSET_ID)
        print(f"[ROBOT] Connected to {ROBOT_ASSET_ID}")
        print(f"[ROBOT] Twin UUID: {robot.uuid}")

        # List available joints to understand what we can control
        joints = robot.joints.list()
        print(f"[ROBOT] Available joints: {joints}")
        return True

    except Exception as e:
        print(f"[ROBOT] Connection error: {e}")
        print("[ROBOT] Running in MOCK mode (no real robot)")
        return False


# ============================================================
# COMMAND EXECUTION
# ============================================================
def execute(command: str, params: dict = None) -> str:
    """
    Execute a robot command.

    Args:
        command: One of the valid commands from config.py
        params: Optional parameters (distance, angle, etc.)

    Returns:
        Status message
    """
    if params is None:
        params = {}

    print(f"[ROBOT] Executing: {command} | params: {params}")

    if robot is None:
        return _mock_execute(command, params)

    try:
        return _real_execute(command, params)
    except Exception as e:
        print(f"[ROBOT] Execution error: {e}")
        return f"Error: {e}"


def _real_execute(command: str, params: dict) -> str:
    """
    Execute commands on the real robot via Cyberwave SDK.

    TODO (DEV 1): Adjust these based on the actual Go2 capabilities
    available through Cyberwave at the hackathon.

    The Cyberwave SDK provides:
        robot.edit_position(x=, y=, z=)
        robot.edit_rotation(yaw=)
        robot.joints.set("joint_name", angle)
        robot.joints.get("joint_name")
        robot.joints.list()
    """

    if command == "move_forward":
        distance = params.get("distance", 1.0)
        #robot.edit_position(x=distance)
        robot.client.mqtt.publish(
            f"cyberwave/twin/{robot.uuid}/command",
            {
                "source_type": "tele",
                "command": "move_forward",
                "data": {"linear_x": distance, "angular_z": 0.0},
                "timestamp": time.time(),
            },
        )
        return f"Moved forward {distance} units"

    elif command == "move_backward":
        distance = params.get("distance", 1.0)
        #robot.edit_position(x=-distance)
        robot.client.mqtt.publish(
            f"cyberwave/twin/{robot.uuid}/command",
            {
                "source_type": "tele",
                "command": "move_backward",
                "data": {"linear_x": distance, "angular_z": 0.0},
                "timestamp": time.time(),
            },
        )

        return f"Moved backward {distance} units"

    elif command == "turn_left":
        angle = params.get("angle", 90)
        #robot.edit_rotation(yaw=-angle)
        robot.client.mqtt.publish(
            f"cyberwave/twin/{robot.uuid}/command",
            {
                "source_type": "tele",
                "command": "turn_left",
                "data": {"linear_x": distance, "angular_z": 0.0},
                "timestamp": time.time(),
            },
        )
        
        return f"Turned left {angle} degrees"

    elif command == "turn_right":
        angle = params.get("angle", 90)
        #robot.edit_rotation(yaw=angle)
        robot.client.mqtt.publish(
            f"cyberwave/twin/{robot.uuid}/command",
            {
                "source_type": "tele",
                "command": "turn_right",
                "data": {"linear_x": distance, "angular_z": 0.0},
                "timestamp": time.time(),
            },
        )

        return f"Turned right {angle} degrees"

    elif command == "sit":
        # TODO: Check if Go2 has a sit command via Cyberwave
        # Might need to set specific joint angles
        # robot.joints.set("sit_pose", 1)
        return "Sitting down"

    elif command == "stand":
        # TODO: Same as sit — check available joint configs
        return "Standing up"

    elif command == "wave":
        # TODO: Animate a front leg wave
        # robot.joints.set("front_left_leg", 45)
        return "Waving"

    elif command == "dance":
        # TODO: Sequence of movements
        return "Dancing"

    elif command == "shake_hand":
        # TODO: Extend a paw
        return "Shaking hand"

    elif command == "stop":
        # Reset to neutral
        robot.edit_position(x=0, y=0, z=0)
        return "Stopped"

    return f"Unknown command: {command}"


def _mock_execute(command: str, params: dict) -> str:
    """
    Mock execution for testing without a real robot.
    Prints what would happen.
    """
    print(f"[MOCK ROBOT] Would execute: {command} with {params}")
    return f"[MOCK] {command} executed"


def get_robot_status() -> dict:
    """Get current robot state (for the UI)."""
    if robot is None:
        return {"connected": False, "mode": "mock"}

    try:
        joints = robot.joints.get_all()
        return {
            "connected": True,
            "uuid": robot.uuid,
            "joints": joints,
        }
    except Exception:
        return {"connected": True, "uuid": robot.uuid}


# ============================================================
# Quick test
# ============================================================
if __name__ == "__main__":
    print("Testing robot module...")
    connected = init_robot()
    print(f"Connected: {connected}")

    # Test commands
    print(execute("move_forward", {"distance": 2}))
    print(execute("turn_left", {"angle": 90}))
    print(execute("sit"))
    print(execute("dance"))
