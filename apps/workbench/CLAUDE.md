# Feralboard Workbench

Python GUI, device scripts, and E2E tests for the FeralBoard.

## What Matters

- Python runtime uses `.venv/`, created by `setup.sh` with `python3 -m venv --system-site-packages`
- GTK/PyGObject stays provided by apt/system Python
- Run Python entrypoints through `bash scripts/python.sh ...`
- Firmware lives in the monorepo at `../../hardware/firmware`
- Preferred firmware entrypoint is `sudo bash ../../scripts/firmware/flash.sh`

## Common Commands

```bash
# Install system deps + create/update .venv
sudo bash setup.sh

# Launch GUI
bash scripts/run.sh

# Run tests
bash scripts/python.sh tests/test_outputs_e2e.py
bash scripts/python.sh tests/test_inputs_e2e.py
bash scripts/python.sh -m pytest tests/ --port /dev/ttyAMA0

# Build/flash firmware
bash ../../scripts/firmware/flash.sh --build-only
sudo bash ../../scripts/firmware/flash.sh --flash-only
```

## Serial Ports

- `/dev/ttyAMA0` — runtime serial comms, 9600 baud
- `/dev/ttyAMA3` — serialUPDI flashing on Pi 5
- Do not point the GUI or serial library at `ttyAMA3`

## GUI Notes

- Wayland/Sway app launcher: `bash scripts/run.sh`
- IPC socket: `/tmp/feralboard-workbench.sock`
- Screenshot: `bash scripts/screenshot.sh`
- Send commands: `bash scripts/send.sh navigate outputs`

## Test Notes

- The GUI test page runs subprocesses with the active Python interpreter
- E2E tests expect the board on `/dev/ttyAMA0`
- `raspi-gpio` helper defaults to `192.168.0.142:5555`

## Kiosk Apps

- App manifests live in `kiosk_apps/*/app.json`
- Greeting apps use `"greeting"`
- Custom apps use `"page"` and load `gui/pages/<page>.py`
