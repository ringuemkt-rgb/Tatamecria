"""Consent and purpose guards enforced before any capture starts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    participant_id: str
    protocol_version: str
    guardian_consent: bool
    child_assent_recorded: bool
    video_processing_allowed: bool
    redacted_video_storage_allowed: bool
    valid_until: date | None = None

    def allows_capture(self, today: date | None = None) -> bool:
        current = today or date.today()
        not_expired = self.valid_until is None or current <= self.valid_until
        return (
            self.guardian_consent
            and self.child_assent_recorded
            and self.video_processing_allowed
            and not_expired
        )


class ConsentGuard:
    """Reject capture when the documented consent does not cover the purpose."""

    @staticmethod
    def require_capture_permission(consent: ConsentRecord) -> None:
        if not consent.allows_capture():
            raise PermissionError("Capture is not permitted by the current consent record")


@dataclass(frozen=True, slots=True)
class AdultCaptureConsent:
    """Explicit permission for a consenting adult research demonstrator only."""

    participant_id: str
    is_adult: bool
    informed_consent: bool
    video_processing_allowed: bool
    valid_until: date | None = None

    def allows_capture(self, today: date | None = None) -> bool:
        current = today or date.today()
        return (
            self.is_adult
            and self.informed_consent
            and self.video_processing_allowed
            and (self.valid_until is None or current <= self.valid_until)
        )


class AdultConsentGuard:
    @staticmethod
    def require_capture_permission(consent: AdultCaptureConsent, participant_id: str) -> None:
        if consent.participant_id != participant_id or not consent.allows_capture():
            raise PermissionError("Adult demonstration capture was not authorized")
