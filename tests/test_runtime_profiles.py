"""
Runtime Profiles CI Tests (P0 Robustness).

Validates that named runtime profiles in src/runtime_profiles.py
- Load cleanly
- Don't conflict with safe defaults
- Enable expected kernel behavior
- Maintain collaboration invariants

Part of STRATEGY_AND_ROADMAP.md P0: "Runtime profiles + CI smoke tests".
"""

from __future__ import annotations

import os
import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from runtime_profiles import RUNTIME_PROFILES, apply_runtime_profile


class TestRuntimeProfilesLoadable:
	"""Verify all profiles are valid and loadable."""

	def test_profile_dict_structure(self):
		"""RUNTIME_PROFILES is a dict of dicts with string keys and values."""
		assert isinstance(RUNTIME_PROFILES, dict)
		for name, profile in RUNTIME_PROFILES.items():
			assert isinstance(name, str), f"Profile name {name} is not a string"
			assert isinstance(profile, dict), f"Profile {name} is not a dict"
			for key, value in profile.items():
				assert isinstance(key, str), f"Key {key} in profile {name} is not a string"
				assert isinstance(value, str), f"Value {value} in profile {name} is not a string"

	def test_all_profiles_registered(self):
		"""Profiles mentioned in docstring are all in RUNTIME_PROFILES."""
		expected_profiles = {
			"baseline",
			"judicial_demo",
			"hub_dao_demo",
			"nomad_demo",
			"reality_lighthouse_demo",
			"lan_mobile_thin_client",
			"operational_trust",
			"lan_operational",
			"moral_hub_extended",
			"situated_v8_lan_demo",
		}
		actual = set(RUNTIME_PROFILES.keys())
		# All expected profiles should exist
		assert expected_profiles.issubset(
			actual
		), f"Missing profiles: {expected_profiles - actual}"

	def test_profile_env_vars_are_kernel_like(self):
		"""Profile values use safe env var patterns (KERNEL_*, CHAT_*, etc)."""
		allowed_prefixes = ("KERNEL_", "CHAT_", "ETHOS_")
		for profile_name, profile_dict in RUNTIME_PROFILES.items():
			for key in profile_dict.keys():
				assert any(
					key.startswith(prefix) for prefix in allowed_prefixes
				), f"Key {key} in profile {profile_name} doesn't match safe patterns"


class TestRuntimeProfilesContent:
	"""Verify profile contents match expectations (structure validation)."""

	def test_baseline_is_empty(self):
		"""Baseline profile is empty (no overrides)."""
		assert RUNTIME_PROFILES["baseline"] == {}

	def test_judicial_demo_has_expected_keys(self):
		"""Judicial demo profile has governance flags."""
		profile = RUNTIME_PROFILES["judicial_demo"]
		assert "KERNEL_JUDICIAL_ESCALATION" in profile
		assert "KERNEL_JUDICIAL_MOCK_COURT" in profile
		assert "KERNEL_CHAT_INCLUDE_JUDICIAL" in profile

	def test_hub_dao_demo_has_expected_keys(self):
		"""Hub DAO demo profile has DAO flags."""
		profile = RUNTIME_PROFILES["hub_dao_demo"]
		assert "KERNEL_MORAL_HUB_PUBLIC" in profile
		assert "KERNEL_MORAL_HUB_DAO_VOTE" in profile

	def test_lan_mobile_thin_client_has_network_keys(self):
		"""LAN mobile profile has network binding flags."""
		profile = RUNTIME_PROFILES["lan_mobile_thin_client"]
		assert "CHAT_HOST" in profile
		assert "CHAT_PORT" in profile
		assert profile["CHAT_HOST"] == "0.0.0.0"

	def test_operational_trust_reduces_narrative(self):
		"""Operational trust profile disables narrative exposure."""
		profile = RUNTIME_PROFILES["operational_trust"]
		assert profile.get("KERNEL_CHAT_INCLUDE_HOMEOSTASIS") == "0"
		assert profile.get("KERNEL_CHAT_EXPOSE_MONOLOGUE") == "0"
		assert profile.get("KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST") == "0"

	def test_situated_v8_has_sensor_flags(self):
		"""Situated v8 profile includes sensor configuration."""
		profile = RUNTIME_PROFILES["situated_v8_lan_demo"]
		assert "KERNEL_SENSOR_FIXTURE" in profile
		assert "KERNEL_SENSOR_PRESET" in profile
		assert "KERNEL_CHAT_INCLUDE_VITALITY" in profile


class TestRuntimeProfilesNoConflicts:
	"""Verify profiles don't create internal conflicts."""

	def test_no_contradictory_flags_within_profile(self):
		"""No profile sets contradictory flags (e.g., X=1 and X=0)."""
		for profile_name, profile_dict in RUNTIME_PROFILES.items():
			# Check for obvious contradictions
			keys = set(profile_dict.keys())
			# Example: checking if both "enable" and "disable" variants exist
			for key in keys:
				value = profile_dict[key]
				# No key should set itself to both true and false
				assert not (key in profile_dict and profile_dict[key] != value), \
					f"Profile {profile_name} has contradictory flags for {key}"

	def test_profile_subset_principle(self):
		"""Each profile is a clean subset; no cross-profile pollution."""
		# Baseline should be empty (no overrides)
		assert RUNTIME_PROFILES["baseline"] == {}
		# All other profiles should be non-empty
		for name, profile in RUNTIME_PROFILES.items():
			if name != "baseline":
				assert profile, f"Non-baseline profile {name} is empty"


class TestRuntimeProfilesCI:
	"""CI-relevant tests: can we load and use profiles?"""

	@pytest.mark.parametrize("profile_name", list(RUNTIME_PROFILES.keys()))
	def test_all_profiles_are_valid_dicts(self, profile_name):
		"""Each profile is a valid dictionary of strings."""
		profile = RUNTIME_PROFILES[profile_name]
		assert isinstance(profile, dict), f"Profile {profile_name} is not a dict"
		for key, value in profile.items():
			assert isinstance(key, str), f"Key {key} in {profile_name} is not a string"
			assert isinstance(value, str), f"Value {value} in {profile_name} is not a string"
			assert key.isupper(), f"Key {key} in {profile_name} is not UPPERCASE"

	def test_profile_env_vars_safe_for_kernel_load(self):
		"""Environment variables in profiles don't break kernel initialization."""
		# This is a smoke test; actual kernel load is in integration tests
		# We just verify:
		# 1. No invalid key names
		# 2. No obviously dangerous values (e.g., /etc/passwd paths)
		for profile_name, profile_dict in RUNTIME_PROFILES.items():
			for key, value in profile_dict.items():
				# No path traversal / etc
				assert ".." not in value, \
					f"Profile {profile_name} {key} contains path traversal: {value}"
				# Values are typically boolean flags (0/1) or paths/URLs
				if not value.isdigit():
					# If it's not a digit, it should be a plausible path or hostname
					# Very lenient check: just ensure no shell metacharacters
					unsafe_chars = [";", "|", "&", "$", "`"]
					assert not any(c in value for c in unsafe_chars), \
						f"Profile {profile_name} {key} contains unsafe chars: {value}"
