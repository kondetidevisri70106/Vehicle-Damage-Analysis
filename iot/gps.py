"""
GPS reader with NMEA 0183 parsing.
Works with any serial GPS module (NEO-6M, NEO-8M, BN-880, etc.)
or falls back to a simulator if no hardware is connected.
"""

import time
import threading
import random
from datetime import datetime, timezone

try:
    import serial
    import serial.tools.list_ports
    _SERIAL_AVAILABLE = True
except ImportError:
    _SERIAL_AVAILABLE = False


# ============================================================
# NMEA parsing
# ============================================================

def _nmea_checksum_ok(sentence: str) -> bool:
    """Verify the *XX checksum at the end of an NMEA sentence."""
    if "*" not in sentence:
        return False
    body, _, checksum = sentence.partition("*")
    body = body.lstrip("$")
    calc = 0
    for ch in body:
        calc ^= ord(ch)
    try:
        return calc == int(checksum.strip()[:2], 16)
    except ValueError:
        return False


def _dm_to_decimal(dm: str, direction: str) -> float | None:
    """
    Convert NMEA degrees/minutes format to decimal degrees.
    Example: '4807.038', 'N'  ->  48.1173
    """
    if not dm or not direction:
        return None
    try:
        dot = dm.index(".")
        deg = float(dm[:dot - 2])
        minutes = float(dm[dot - 2:])
        dec = deg + minutes / 60.0
        if direction in ("S", "W"):
            dec = -dec
        return round(dec, 6)
    except (ValueError, IndexError):
        return None


def parse_gpgga(sentence: str) -> dict | None:
    """
    Parse $GPGGA / $GNGGA (fix data).
    Format:
      $GPGGA,hhmmss.ss,ddmm.mmmm,N,dddmm.mmmm,E,fix,sats,hdop,alt,M,...
    """
    if not sentence.startswith(("$GPGGA", "$GNGGA")):
        return None
    if not _nmea_checksum_ok(sentence):
        return None

    parts = sentence.split(",")
    if len(parts) < 10:
        return None

    try:
        fix_quality = int(parts[6]) if parts[6] else 0
        num_sats = int(parts[7]) if parts[7] else 0
        hdop = float(parts[8]) if parts[8] else None
        altitude = float(parts[9]) if parts[9] else None
    except ValueError:
        return None

    lat = _dm_to_decimal(parts[2], parts[3])
    lon = _dm_to_decimal(parts[4], parts[5])

    return {
        "lat": lat,
        "lon": lon,
        "fix_quality": fix_quality,          # 0 = no fix, 1 = GPS, 2 = DGPS
        "num_satellites": num_sats,
        "hdop": hdop,
        "altitude_m": altitude,
        "raw_time": parts[1],
    }


def parse_gprmc(sentence: str) -> dict | None:
    """
    Parse $GPRMC / $GNRMC (recommended minimum).
    Format:
      $GPRMC,hhmmss.ss,A,ddmm.mmmm,N,dddmm.mmmm,E,speed,course,ddmmyy,...
    """
    if not sentence.startswith(("$GPRMC", "$GNRMC")):
        return None
    if not _nmea_checksum_ok(sentence):
        return None

    parts = sentence.split(",")
    if len(parts) < 10:
        return None

    try:
        speed_knots = float(parts[7]) if parts[7] else 0.0
        course = float(parts[8]) if parts[8] else 0.0
    except ValueError:
        speed_knots = 0.0
        course = 0.0

    lat = _dm_to_decimal(parts[3], parts[4])
    lon = _dm_to_decimal(parts[5], parts[6])

    return {
        "lat": lat,
        "lon": lon,
        "status": parts[2],                  # 'A' = active, 'V' = void
        "speed_knots": speed_knots,
        "speed_kph": round(speed_knots * 1.852, 2),
        "course_deg": course,
        "date": parts[9],
    }


# ============================================================
# GPS reader
# ============================================================

class GPS:
    """
    Blocking GPS reader.

    Two modes:
      - Hardware: pass a serial port (auto-detect if None)
      - Simulator: pass simulated=True or leave port unset on unsupported OS
    """

    def __init__(self, port: str | None = None, baud: int = 9600,
                 simulated: bool = False, timeout: float = 2.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.simulated = simulated or not _SERIAL_AVAILABLE
        self.ser = None
        self._lock = threading.Lock()

        # Latest fix state
        self._last_fix = {
            "lat": None,
            "lon": None,
            "fix_quality": 0,
            "num_satellites": 0,
            "hdop": None,
            "altitude_m": None,
            "speed_kph": None,
            "course_deg": None,
            "timestamp": None,
        }

        if not self.simulated:
            self._open_serial()

    # ---------------- serial setup ----------------

    def _open_serial(self):
        if not _SERIAL_AVAILABLE:
            print("[GPS] pyserial not installed — running simulated.")
            self.simulated = True
            return

        port = self.port or self._autodetect_port()
        if port is None:
            print("[GPS] No serial GPS found — running simulated.")
            self.simulated = True
            return

        try:
            self.ser = serial.Serial(port, self.baud, timeout=self.timeout)
            self.port = port
            print(f"[GPS] Opened {port} @ {self.baud} baud")
        except serial.SerialException as e:
            print(f"[GPS] Failed to open {port}: {e} — running simulated.")
            self.simulated = True
            self.ser = None

    @staticmethod
    def _autodetect_port():
        """Try to find an obvious GPS device on the current OS."""
        if not _SERIAL_AVAILABLE:
            return None
        ports = list(serial.tools.list_ports.comports())
        # Heuristic: look for common GPS vendor strings
        for p in ports:
            desc = (p.description or "").lower()
            if any(k in desc for k in ("gps", "gnss", "u-blox", "ublox")):
                return p.device
        # On Linux, /dev/ttyUSB0 and /dev/ttyACM0 are common
        import platform
        if platform.system() == "Linux":
            for p in ("/dev/ttyUSB0", "/dev/ttyACM0"):
                import os
                if os.path.exists(p):
                    return p
        return None

    # ---------------- reading ----------------

    def read(self) -> dict:
        """Return the latest GPS fix. Blocks briefly on hardware mode."""
        if self.simulated:
            return self._read_simulated()
        return self._read_hardware()

    def _read_hardware(self) -> dict:
        """Read NMEA lines until a valid GGA or RMC is parsed."""
        if self.ser is None:
            return self._empty_fix()

        deadline = time.time() + self.timeout
        while time.time() < deadline:
            try:
                line = self.ser.readline().decode("ascii", errors="ignore").strip()
            except serial.SerialException as e:
                print(f"[GPS] serial error: {e}")
                return self._empty_fix()

            if not line:
                continue

            gga = parse_gpgga(line)
            if gga:
                self._update_fix(gga)
                continue

            rmc = parse_gprmc(line)
            if rmc:
                self._update_fix(rmc)

        return dict(self._last_fix)

    def _read_simulated(self) -> dict:
        """Generate plausible GPS readings around a fixed Indian location."""
        with self._lock:
            # Start near Mumbai and drift slightly each call
            if self._last_fix["lat"] is None:
                base_lat, base_lon = 19.0760, 72.8777
            else:
                base_lat = self._last_fix["lat"]
                base_lon = self._last_fix["lon"]

            lat = round(base_lat + random.uniform(-0.0005, 0.0005), 6)
            lon = round(base_lon + random.uniform(-0.0005, 0.0005), 6)

            self._last_fix.update({
                "lat": lat,
                "lon": lon,
                "fix_quality": 1,
                "num_satellites": random.randint(8, 13),
                "hdop": round(random.uniform(0.7, 1.5), 2),
                "altitude_m": round(random.uniform(10, 40), 1),
                "speed_kph": round(random.uniform(0, 5), 2),
                "course_deg": round(random.uniform(0, 360), 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return dict(self._last_fix)

    def _update_fix(self, parsed: dict):
        """Merge a parsed sentence into the latest-fix state."""
        with self._lock:
            for k, v in parsed.items():
                if v is not None:
                    self._last_fix[k] = v
            self._last_fix["timestamp"] = datetime.now(timezone.utc).isoformat()

    def _empty_fix(self) -> dict:
        return {
            "lat": None, "lon": None,
            "fix_quality": 0, "num_satellites": 0,
            "hdop": None, "altitude_m": None,
            "speed_kph": None, "course_deg": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ---------------- convenience ----------------

    def has_fix(self) -> bool:
        return self._last_fix["lat"] is not None and self._last_fix["lon"] is not None

    def close(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ============================================================
# CLI test
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Read GPS data (hardware or simulated)")
    parser.add_argument("--port", default=None, help="Serial port, e.g. COM3 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--simulated", action="store_true", help="Force simulator")
    args = parser.parse_args()

    gps = GPS(port=args.port, baud=args.baud, simulated=args.simulated)

    print("Reading GPS — Ctrl+C to stop.")
    try:
        while True:
            fix = gps.read()
            status = "FIX" if fix["lat"] is not None else "NO FIX"
            print(f"[{status}] lat={fix['lat']} lon={fix['lon']} "
                  f"sats={fix['num_satellites']} hdop={fix['hdop']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        gps.close()