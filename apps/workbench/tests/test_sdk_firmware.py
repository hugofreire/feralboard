"""Non-hardware tests for SDK firmware HEX deployment helpers."""

import subprocess

import pytest

from feralboard_sdk.firmware import (
    FirmwareDeployer,
    FirmwareDeploymentError,
    HexValidationError,
    deploy_firmware_hex,
    validate_intel_hex,
)


VALID_HEX = ":0100000000FF\n:00000001FF\n"


def write_hex(tmp_path, content=VALID_HEX):
    path = tmp_path / "release.hex"
    path.write_text(content, encoding="ascii")
    return path


def test_validate_intel_hex_accepts_basic_release_hex(tmp_path):
    hex_path = write_hex(tmp_path)

    assert validate_intel_hex(hex_path) == hex_path.resolve()


def test_validate_intel_hex_rejects_bad_checksum(tmp_path):
    hex_path = write_hex(tmp_path, ":010000000000\n:00000001FF\n")

    with pytest.raises(HexValidationError, match="checksum"):
        validate_intel_hex(hex_path)


def test_deploy_hex_dry_run_returns_avrdude_sequence(tmp_path):
    hex_path = write_hex(tmp_path)

    result = deploy_firmware_hex(
        hex_path,
        port="/dev/ttyTEST",
        dry_run=True,
        avrdude="/usr/bin/avrdude",
    )

    assert result.dry_run is True
    assert result.port == "/dev/ttyTEST"
    assert len(result.commands) == 3
    assert result.commands[0][-2:] == ("-U", "fuse5:w:0xC1:m")
    assert f"flash:w:{hex_path.resolve()}:i" in result.commands[1]
    assert "fuse5:w:0xC9:m" in result.commands[2]


def test_deploy_hex_executes_commands_with_injected_runner(tmp_path):
    hex_path = write_hex(tmp_path)
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    deployer = FirmwareDeployer(avrdude="avrdude-test", runner=runner)
    result = deployer.deploy_hex(hex_path, port="/dev/ttyTEST")

    assert result.dry_run is False
    assert [call[0][0] for call in calls] == ["avrdude-test"] * 3
    assert all(call[1]["check"] is True for call in calls)
    assert all(call[1]["capture_output"] is True for call in calls)


def test_deploy_hex_raises_when_runner_fails(tmp_path):
    hex_path = write_hex(tmp_path)

    def runner(command, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=command,
            stderr="avrdude failed",
        )

    deployer = FirmwareDeployer(avrdude="avrdude-test", runner=runner)

    with pytest.raises(FirmwareDeploymentError, match="avrdude failed"):
        deployer.deploy_hex(hex_path, port="/dev/ttyTEST")
