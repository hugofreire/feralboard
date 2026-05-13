"""Named oven simulator scenarios for demos and customer evaluation."""

from __future__ import annotations

from .simulator import OvenSimulator


def ready_oven(*, temperature_c: float = 25.0) -> OvenSimulator:
    """Oven ready: door closed, no faults, ambient temperature."""
    sim = OvenSimulator()
    sim.set_door_closed(True)
    sim.set_temperature(temperature_c)
    sim.clear_faults()
    return sim


def door_open(*, temperature_c: float = 80.0) -> OvenSimulator:
    """Oven with door open."""
    sim = ready_oven(temperature_c=temperature_c)
    sim.set_door_closed(False)
    return sim


def oven_over_temperature(*, temperature_c: float = 265.0) -> OvenSimulator:
    """Oven over-temperature alarm."""
    sim = ready_oven(temperature_c=temperature_c)
    sim.set_fault("oven_over_temperature", True)
    return sim


def motor_over_temperature(*, temperature_c: float = 120.0) -> OvenSimulator:
    """Motor over-temperature alarm."""
    sim = ready_oven(temperature_c=temperature_c)
    sim.set_fault("motor_over_temperature", True)
    return sim


def electric_protection_trip(*, temperature_c: float = 25.0) -> OvenSimulator:
    """Electric protection fault."""
    sim = ready_oven(temperature_c=temperature_c)
    sim.set_fault("electric_protection", True)
    return sim
