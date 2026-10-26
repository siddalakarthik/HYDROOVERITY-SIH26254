"""Fail-closed process configuration. Secrets are never included in errors."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from .contact_policy import ContactTestPolicy

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    database_url: SecretStr
    origin: str = "https://localhost:8443"
    hmac_key: SecretStr
    development: bool = True
    mail_directory: Path
    pool_size: int = Field(default=5, ge=1, le=20)
    # No environment activation: operator/privacy review is still required.
    contact_test_policy: ContactTestPolicy | None = None
    science_catalogue_path: Path | None = ROOT / "data/samples/m06"
    science_catalogue_sha256: str | None = Field(
        default="1921fae430c22f2c05c74862e5e1dfe65bffbb9d936171eb637ca61325ca097a",
        pattern=r"^[0-9a-f]{64}$",
    )

    @model_validator(mode="after")
    def release_boundary(self) -> "Settings":
        url = urlsplit(self.origin)
        if url.scheme != "https" or url.path or url.query or url.fragment or url.username:
            raise ValueError("A single HTTPS origin without path is required")
        if (
            "__SET_" in self.database_url.get_secret_value()
            or not self.database_url.get_secret_value().startswith("postgresql+psycopg://")
        ):
            raise ValueError("PostgreSQL psycopg connection required")
        if (
            self.hmac_key.get_secret_value().startswith("__SET_")
            or len(self.hmac_key.get_secret_value()) < 32
        ):
            raise ValueError("A private random HMAC key of at least 32 characters is required")
        if self.mail_directory.resolve().is_relative_to(ROOT):
            raise ValueError("Private authentication delivery must be outside the repository")
        if not self.development:
            raise ValueError(
                "Public release disabled pending delivery/shared-rate/operations review"
            )
        if url.hostname not in {"localhost", "127.0.0.1"}:
            raise ValueError("M03 supports private loopback development only")
        return self

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_url=os.environ["HYDRO_DATABASE_URL"],
            hmac_key=os.environ["HYDRO_HMAC_KEY"],
            origin=os.environ.get("HYDRO_ORIGIN", "https://localhost:8443"),
            mail_directory=Path(os.environ["HYDRO_PRIVATE_MAIL_DIR"]),
            development=os.environ.get("HYDRO_ENV", "development") == "development",
            **(
                {"science_catalogue_path": os.environ["HYDRO_SCIENCE_CATALOGUE"]}
                if "HYDRO_SCIENCE_CATALOGUE" in os.environ
                else {}
            ),
            **(
                {"science_catalogue_sha256": os.environ["HYDRO_SCIENCE_CATALOGUE_SHA256"]}
                if "HYDRO_SCIENCE_CATALOGUE_SHA256" in os.environ
                else {}
            ),
        )
