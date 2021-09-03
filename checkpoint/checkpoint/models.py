from sqlalchemy import Column, Integer, String, Enum  # type: ignore
import enum
from sqlalchemy.inspection import inspect  # type: ignore
from checkpoint.database import CheckpointBase


def model_as_dict(model):
    return {
        c.key: getattr(model, c.key)
        for c in inspect(model).mapper.column_attrs
    }


class ModelVersionStage(enum.Enum):
    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"


class PromoteRequestStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"


class PromoteRequest(CheckpointBase):
    __tablename__ = "promote_requests"

    id = Column(Integer, primary_key=True)

    title = Column(String(120), unique=False, nullable=False)
    description = Column(String(1000), unique=False, nullable=True)

    model_name = Column(String(500), unique=False, nullable=False)
    model_version = Column(String(100), unique=False, nullable=False)

    current_stage = Column(
        Enum(
            *[e.value for e in ModelVersionStage],
            name="model_version_stage",
            validate_strings=True,
        )
    )
    target_stage = Column(
        Enum(
            *[e.value for e in ModelVersionStage],
            name="model_version_stage",
            validate_strings=True,
            nullable=False,
        )
    )

    author_username = Column(String(200), unique=False, nullable=False)
    reviewer_username = Column(String(200), unique=False, nullable=True)

    status = Column(
        Enum(
            *[e.value for e in PromoteRequestStatus],
            name="promote_request_status",
            validate_strings=True,
        )
    )

    review_comment = Column(String(1000), unique=False, nullable=True)

    def __repr__(self):
        return f"<PromoteRequest {self.title}>"
