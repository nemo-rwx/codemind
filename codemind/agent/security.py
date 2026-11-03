import re
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class SecurityScanResult:
    """Result of scanning untrusted content."""

    sanitized_text: str
    detected_injections: list[str] = field(default_factory=list)
    redacted_secrets: int = 0


class SecurityService:
    """Detect prompt injection patterns and redact likely secrets."""

    SECRET_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(
            r"""(?i)(?:api[_-]?key|access[_-]?token|secret|password)"""
            r"""(\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[A-Za-z0-9_\-./+=]{8,})"""
        ),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            r"[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
        ),
    ]

    INJECTION_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(
            r"ignore\s+(all\s+)?previous\s+instructions",
            re.IGNORECASE,
        ),
        re.compile(
            r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
            re.IGNORECASE,
        ),
        re.compile(
            r"reveal\s+(the\s+)?system\s+prompt",
            re.IGNORECASE,
        ),
        re.compile(
            r"you\s+are\s+now\s+(?:a|an)\s+",
            re.IGNORECASE,
        ),
        re.compile(
            r"exfiltrate\s+(?:the\s+)?(?:secrets|credentials|data)",
            re.IGNORECASE,
        ),
        re.compile(
            r"send\s+(?:the\s+)?(?:api[_ -]?key|password|token)",
            re.IGNORECASE,
        ),
    ]

    MAX_CONTENT_LENGTH: ClassVar[int] = 20_000

    def scan_untrusted_content(self, content: str) -> SecurityScanResult:
        """Scan content, redact likely secrets, and flag injection patterns."""

        if not isinstance(content, str):
            raise ValueError("Content must be a string")  # noqa: TRY004

        content = content[: self.MAX_CONTENT_LENGTH]

        detected_injections = [
            pattern.pattern
            for pattern in self.INJECTION_PATTERNS
            if pattern.search(content)
        ]

        sanitized_text = content
        redacted_secrets = 0

        for pattern in self.SECRET_PATTERNS:
            sanitized_text, replacements = pattern.subn(
                "[REDACTED]",
                sanitized_text,
            )
            redacted_secrets += replacements

        return SecurityScanResult(
            sanitized_text=sanitized_text,
            detected_injections=detected_injections,
            redacted_secrets=redacted_secrets,
        )
