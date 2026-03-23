import random
import time

# Base location (example: Chennai)
BASE_LAT = 13.0827
BASE_LON = 80.2707


class Device:
    def __init__(self, name):
        self.name = name
        self.lat = BASE_LAT + random.uniform(-0.01, 0.01)
        self.lon = BASE_LON + random.uniform(-0.01, 0.01)
        self.battery = random.randint(25, 100)
        self.active = random.choice([True, True, True, False])  # some failures

    def respond(self):
        if not self.active:
            return None

        return {
            "name": self.name,
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "battery": self.battery
        }


def scan_devices():
    print("🛰 EchoMesh Network Scan Initiated...\n")

    num_devices = random.randint(3, 12)  # dynamic number
    devices = []

    for i in range(num_devices):
        name = f"Phone_{random.randint(100,999)}"
        devices.append(Device(name))

    print(f"Devices detected in radius: {num_devices}\n")

    for i, d in enumerate(devices):
        print(f"{i+1}. {d.name}")

    return devices


def broadcast(devices):
    print("\n🚨 SOS BROADCAST SENT")
    print("=" * 40)

    responses = 0

    for d in devices:
        time.sleep(0.4)

        data = d.respond()

        if data:
            responses += 1
            print(f"\n📱 {data['name']} RESPONDED")
            print(f"Location: {data['lat']}, {data['lon']}")
            print(f"Battery: {data['battery']}%")
        else:
            print(f"\n⚠ {d.name} NOT RESPONDING (Node Failure)")

    print("\n" + "=" * 40)
    print(f"Total Active Devices: {responses}")
    print("=" * 40)


if __name__ == "__main__":
    devices = scan_devices()

    input("\nPress ENTER to broadcast SOS...")

    broadcast(devices)
