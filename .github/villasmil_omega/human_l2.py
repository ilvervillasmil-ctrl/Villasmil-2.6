"""
Villasmil-Ω — Human L2 regulation system (robust implementation)
"""

from typing import List, Dict, Optional
import time
import numpy as np


def compute_L2_enhanced(
    phi_C: float,
    theta_C: float,
    MC: float,
    CI: float,
    heart_rate: Optional[float] = None,
    hrv: Optional[float] = None,
    sleep_quality: Optional[float] = None,
    cortisol_level: Optional[float] = None,
    subjective_stress: Optional[float] = None,
    context: str = "normal",
    baseline_hr: float = 70.0,
    baseline_hrv: float = 50.0,
) -> Dict:
    """
    Compute enhanced L2 with multi-signal fusion.
    Returns dict with L2 (clamped [0,1]) and components breakdown.
    """
    L2_base = (
        0.40 * float(phi_C)
        + 0.30 * float(theta_C)
        + 0.15 * (1.0 - float(MC))
        + 0.15 * (1.0 - float(CI))
    )
    L2_base = max(0.0, min(1.0, L2_base))

    bio_adjustment = 0.0

    if heart_rate is not None:
        hr_deviation = (float(heart_rate) - float(baseline_hr)) / max(1.0, float(baseline_hr))
        if hr_deviation > 0.35:
            bio_adjustment += 0.20
        elif hr_deviation > 0.20:
            bio_adjustment += 0.10

    if hrv is not None:
        hrv_ratio = float(hrv) / max(1.0, float(baseline_hrv))
        if hrv_ratio < 0.70:
            bio_adjustment += 0.10

    if sleep_quality is not None and float(sleep_quality) < 0.50:
        bio_adjustment += 0.15

    if cortisol_level is not None and float(cortisol_level) > 0.70:
        bio_adjustment += 0.12

    bio_adjustment = min(bio_adjustment, 0.6)

    if subjective_stress is not None:
        stress_normalized = max(0.0, min(1.0, float(subjective_stress) / 10.0))
        L2_base = 0.70 * L2_base + 0.30 * stress_normalized
        L2_base = max(0.0, min(1.0, L2_base))

    context_multipliers = {
        "alone_safe": 1.0,
        "normal": 1.0,
        "public_event": 1.15,
        "high_stakes": 1.30,
        "family_event": 1.10,
    }
    context_mult = context_multipliers.get(context, 1.0)

    L2_final = (L2_base + bio_adjustment) * context_mult
    L2_final = max(0.0, min(1.0, L2_final))

    return {
        "L2": float(L2_final),
        "L2_base": float(L2_base),
        "bio_adjustment": float(bio_adjustment),
        "context_multiplier": float(context_mult),
        "components": {
            "phi_C": 0.40 * float(phi_C),
            "theta_C": 0.30 * float(theta_C),
            "MC_drop": 0.15 * (1.0 - float(MC)),
            "CI_drop": 0.15 * (1.0 - float(CI)),
        },
    }


class HysteresisDecisionSystem:
    """
    Hysteresis-based state transitions.
    States: OBSERVE (0), PREVENT (1), PROTECT (2)
    """

    def __init__(self, T1_up=0.30, T1_down=0.25, T2_up=0.70, T2_down=0.65):
        self.T1_up = float(T1_up)
        self.T1_down = float(T1_down)
        self.T2_up = float(T2_up)
        self.T2_down = float(T2_down)
        self.current_state = "OBSERVE"

    def evaluate(self, L2_current: float) -> Dict:
        previous_state = self.current_state
        L2_current = float(L2_current)

        if self.current_state == "OBSERVE":
            if L2_current >= self.T1_up:
                self.current_state = "PREVENT"

        elif self.current_state == "PREVENT":
            if L2_current >= self.T2_up:
                self.current_state = "PROTECT"
            elif L2_current < self.T1_down:
                self.current_state = "OBSERVE"

        elif self.current_state == "PROTECT":
            if L2_current < self.T2_down:
                self.current_state = "PREVENT"

        state_changed = previous_state != self.current_state

        return {
            "state": self.current_state,
            "state_code": {"OBSERVE": 0, "PREVENT": 1, "PROTECT": 2}[self.current_state],
            "state_changed": state_changed,
            "previous_state": previous_state,
            "L2": L2_current,
        }


class RateOfChangeAnalyzer:
    """
    Track L2 history and compute velocity (dL2/dt).
    Velocity returned is in units L2 change per minute ("per_min").
    """

    def __init__(self, window_size: int = 5):
        self.history: List[float] = []
        self.timestamps: List[float] = []
        self.window_size = int(window_size)

    def add_measurement(self, L2: float, timestamp: Optional[float] = None):
        if timestamp is None:
            timestamp = time.time()
        self.history.append(float(L2))
        self.timestamps.append(float(timestamp))
        if len(self.history) > self.window_size:
            self.history.pop(0)
            self.timestamps.pop(0)

    def compute_velocity(self) -> Dict:
        if len(self.history) < 2:
            return {
                "velocity": 0.0,
                "acceleration": 0.0,
                "trend": "INSUFFICIENT_DATA",
                "recent_L2": self.history[-1] if self.history else None,
            }

        velocities = np.gradient(np.array(self.history), np.array(self.timestamps))
        vel_per_sec = float(velocities[-1])
        vel_per_min = vel_per_sec * 60.0

        if len(velocities) >= 2:
            acceleration = float(velocities[-1] - velocities[-2])
        else:
            acceleration = 0.0

        if vel_per_min > 6.0:
            trend = "RISING_FAST"
        elif vel_per_min > 1.2:
            trend = "RISING_SLOW"
        elif vel_per_min < -6.0:
            trend = "FALLING_FAST"
        elif vel_per_min < -1.2:
            trend = "FALLING_SLOW"
        else:
            trend = "STABLE"

        return {
            "velocity": vel_per_min,
            "acceleration": acceleration * 60.0,
            "trend": trend,
            "recent_L2": self.history[-1] if self.history else None,
        }

    def adjust_threshold_for_velocity(self, T1_base: float, velocity_per_min: float) -> float:
        T1_base = float(T1_base)
        v = float(velocity_per_min)
        if v > 6.0:
            return T1_base * 0.75
        elif v > 3.0:
            return T1_base * 0.85
        elif v < -6.0:
            return T1_base * 1.10
        else:
            return T1_base


class TemporalPatternDetector:
    """
    Detect patterns over a 24h window.
    """

    def __init__(self):
        self.history_24h: List[Dict] = []

    def add_datapoint(self, L2: float, timestamp: Optional[float] = None):
        if timestamp is None:
            timestamp = time.time()
        current_time = float(timestamp)
        self.history_24h.append({"L2": float(L2), "time": current_time})
        cutoff_time = current_time - 86400.0
        self.history_24h = [dp for dp in self.history_24h if dp["time"] >= cutoff_time]

    def detect_patterns(self) -> Dict:
        if len(self.history_24h) < 5:
            return {
                "pattern": "INSUFFICIENT_DATA",
                "patterns": ["INSUFFICIENT_DATA"],
                "num_datapoints": len(self.history_24h),
            }

        L2_values = [dp["L2"] for dp in self.history_24h]
        max_L2 = max(L2_values)
        min_L2 = min(L2_values)
        avg_L2 = sum(L2_values) / len(L2_values)
        range_L2 = max_L2 - min_L2

        patterns = []

        if range_L2 > 0.50 and max_L2 > 0.70 and min_L2 < 0.30:
            patterns.append("OSCILLATION_RISK")

        recent_n = min(5, len(L2_values))
        recent_5 = L2_values[-recent_n:]
        if len(recent_5) >= 2 and all(
            recent_5[i] <= recent_5[i + 1] for i in range(len(recent_5) - 1)
        ):
            patterns.append("SUSTAINED_ESCALATION")

        if avg_L2 > 0.60:
            patterns.append("CHRONIC_ELEVATION")

        n = len(L2_values)
        quarter = max(1, n // 4)
        q1_avg = sum(L2_values[:quarter]) / quarter
        q4_avg = sum(L2_values[-quarter:]) / quarter
        if q4_avg > q1_avg + 0.20:
            patterns.append("BASELINE_SHIFT_UP")

        return {
            "patterns": patterns if patterns else ["NORMAL"],
            "max_L2_24h": max_L2,
            "min_L2_24h": min_L2,
            "avg_L2_24h": avg_L2,
            "range_L2_24h": range_L2,
            "num_datapoints": n,
        }


class VillasmilOmegaHumanL2System:
    """
    Integrated system combining compute, velocity, hysteresis and pattern detection.
    """

    def __init__(self, person_id: str, baseline_config: Optional[Dict] = None):
        self.person_id = person_id
        if baseline_config is None:
            baseline_config = {
                "T1_up": 0.30,
                "T1_down": 0.25,
                "T2_up": 0.70,
                "T2_down": 0.65,
                "baseline_hr": 70,
                "baseline_hrv": 50,
            }
        self.config = baseline_config
        self.decision_system = HysteresisDecisionSystem(
            T1_up=self.config["T1_up"],
            T1_down=self.config["T1_down"],
            T2_up=self.config["T2_up"],
            T2_down=self.config["T2_down"],
        )
        self.velocity_analyzer = RateOfChangeAnalyzer(window_size=5)
        self.pattern_detector = TemporalPatternDetector()
        self.full_history: List[Dict] = []

    def process_measurement(
        self,
        phi_C: float,
        theta_C: float,
        MC: float,
        CI: float,
        heart_rate: Optional[float] = None,
        hrv: Optional[float] = None,
        sleep_quality: Optional[float] = None,
        subjective_stress: Optional[float] = None,
        context: str = "normal",
        timestamp: Optional[float] = None,
    ) -> Dict:
        if timestamp is None:
            timestamp = time.time()

        L2_result = compute_L2_enhanced(
            phi_C=phi_C,
            theta_C=theta_C,
            MC=MC,
            CI=CI,
            heart_rate=heart_rate,
            hrv=hrv,
            sleep_quality=sleep_quality,
            subjective_stress=subjective_stress,
            context=context,
            baseline_hr=self.config["baseline_hr"],
            baseline_hrv=self.config["baseline_hrv"],
        )
        L2_current = float(L2_result["L2"])

        self.velocity_analyzer.add_measurement(L2_current, timestamp)
        velocity_info = self.velocity_analyzer.compute_velocity()

        T1_adjusted = self.velocity_analyzer.adjust_threshold_for_velocity(
            self.config["T1_up"], velocity_info["velocity"]
        )

        original_T1 = self.decision_system.T1_up
        self.decision_system.T1_up = T1_adjusted
        decision = self.decision_system.evaluate(L2_current)
        self.decision_system.T1_up = original_T1

        self.pattern_detector.add_datapoint(L2_current, timestamp)
        patterns = self.pattern_detector.detect_patterns()

        interventions = self._generate_interventions(
            decision["state"], velocity_info["trend"], patterns["patterns"]
        )

        result = {
            "timestamp": timestamp,
            "person_id": self.person_id,
            "L2": L2_current,
            "L2_breakdown": L2_result,
            "state": decision["state"],
            "state_code": decision["state_code"],
            "state_changed": decision["state_changed"],
            "velocity": velocity_info["velocity"],
            "trend": velocity_info["trend"],
            "T1_adjusted": T1_adjusted,
            "patterns_24h": patterns,
            "interventions": interventions,
            "alerts": self._generate_alerts(decision, velocity_info, patterns),
        }

        self.full_history.append(result)
        return result

    def _generate_interventions(self, state: str, trend: str, patterns: List[str]) -> List[str]:
        base_interventions = {
            "OBSERVE": [
                "Continue normal monitoring",
                "Maintain current activities",
            ],
            "PREVENT": [
                "Take 5-minute breathing break",
                "Go for short walk (10-15 min)",
                "Practice grounding exercise (5-4-3-2-1)",
                "Reduce caffeine intake",
                "Check: When did you last eat/sleep?",
            ],
            "PROTECT": [
                "⚠️ IMMEDIATE: Remove yourself from stressful situation",
                "⚠️ Contact support person NOW",
                "⚠️ Activate crisis protocol",
                "Practice intensive grounding (ice, cold water)",
                "Do NOT make important decisions in this state",
            ],
        }
        interventions = list(base_interventions.get(state, []))
        if trend == "RISING_FAST":
            interventions.insert(0, "⚡ ALERT: Rapid escalation detected - act NOW")
        if "OSCILLATION_RISK" in patterns:
            interventions.append(
                "📊 Pattern: Emotional oscillation detected - consider mood stabilization techniques"
            )
        if "CHRONIC_ELEVATION" in patterns:
            interventions.append(
                "📊 Pattern: Chronic stress - schedule rest day or professional consultation"
            )
        return interventions

    def _generate_alerts(self, decision: Dict, velocity: Dict, patterns: Dict) -> List[Dict]:
        alerts = []
        if decision["state"] == "PROTECT":
            alerts.append(
                {
                    "level": "CRITICAL",
                    "message": f'L₂ = {decision["L2"]:.2f} - CRISIS THRESHOLD REACHED',
                }
            )
        if velocity["trend"] == "RISING_FAST":
            alerts.append(
                {
                    "level": "WARNING",
                    "message": f'Rapid escalation: {velocity["velocity"]:.3f}/min',
                }
            )
        if "SUSTAINED_ESCALATION" in patterns.get("patterns", []):
            alerts.append(
                {
                    "level": "WARNING",
                    "message": "Sustained upward trend over 24h - intervention recommended",
                }
            )
        return alerts

    def get_summary_report(self) -> Dict:
        if not self.full_history:
            return {"error": "No data available"}
        recent = self.full_history[-1]
        last_24h = [
            h for h in self.full_history if h["timestamp"] > time.time() - 86400
        ]
        return {
            "person_id": self.person_id,
            "current_status": {
                "L2": recent["L2"],
                "state": recent["state"],
                "trend": recent["trend"],
            },
            "last_24h_summary": {
                "measurements": len(last_24h),
                "avg_L2": float(np.mean([h["L2"] for h in last_24h])) if last_24h else 0.0,
                "max_L2": max([h["L2"] for h in last_24h]) if last_24h else 0.0,
                "time_in_protect": sum(1 for h in last_24h if h["state"] == "PROTECT"),
                "time_in_prevent": sum(1 for h in last_24h if h["state"] == "PREVENT"),
            },
            "patterns": recent["patterns_24h"],
            "recommended_actions": recent["interventions"],
        }
