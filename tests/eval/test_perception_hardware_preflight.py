from __future__ import annotations

from scripts.eval import perception_hardware_preflight as preflight


def test_collect_preflight_ready_when_all_device_classes_present(monkeypatch) -> None:
    def _fake_run(command: str):
        if "AudioEndpoint" in command and "microphone|mic|input" in command:
            return [{"Status": "OK", "Class": "AudioEndpoint", "FriendlyName": "USB Microphone"}]
        if "AudioEndpoint" in command:
            return [{"Status": "OK", "Class": "AudioEndpoint", "FriendlyName": "Headset Output"}]
        return [{"Status": "OK", "Class": "Camera", "FriendlyName": "USB Webcam"}]

    monkeypatch.setattr(preflight, "_run_powershell_json", _fake_run)
    report = preflight.collect_preflight()
    assert report["preflight_ready"] is True
    assert report["summary"]["camera_count"] == 1
    assert report["summary"]["microphone_count"] == 1


def test_collect_preflight_not_ready_without_camera(monkeypatch) -> None:
    def _fake_run(command: str):
        if "AudioEndpoint" in command and "microphone|mic|input" in command:
            return [{"Status": "OK", "Class": "AudioEndpoint", "FriendlyName": "USB Microphone"}]
        if "AudioEndpoint" in command:
            return [{"Status": "OK", "Class": "AudioEndpoint", "FriendlyName": "Headset Output"}]
        return []

    monkeypatch.setattr(preflight, "_run_powershell_json", _fake_run)
    report = preflight.collect_preflight()
    assert report["preflight_ready"] is False
    assert report["summary"]["camera_count"] == 0
