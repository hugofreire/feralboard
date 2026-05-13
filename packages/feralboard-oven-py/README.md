# FeralBoard Oven Simulator

Optional companion package for customers building oven-control software on top
of FeralBoard.

The package provides:

- Oven-domain state model
- FeralBoard-compatible serial frame simulation
- Interactive CLI for changing oven state during development
- Scenario helpers for demos and acceptance testing

It does not include firmware source or the production oven manager.

## Example

```python
from feralboard_oven import OvenSimulator

sim = OvenSimulator()
sim.set_temperature(180)
sim.set_door_closed(True)
print(sim.snapshot())
```

## Scenarios

```python
from feralboard_oven import door_open, oven_over_temperature, ready_oven

print(ready_oven().snapshot())
print(door_open(temperature_c=90).snapshot())
print(oven_over_temperature().snapshot())
```

## CLI

```bash
feralboard-oven-sim --serial /tmp/feralboard-sim
```

Use a PTY pair from `socat` when you want one process to act as the oven
manager and the simulator to act as the FeralBoard device.
