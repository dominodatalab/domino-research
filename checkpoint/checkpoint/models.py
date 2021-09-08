from sqlalchemy import Column, Integer, String, Enum, DateTime
from checkpoint.database import CheckpointBase
from checkpoint.types import ModelVersionStage, PromoteRequestStatus


class PromoteRequest(CheckpointBase):

    UPDATEABLE_FIELDS = {"review_comment", "status"}

    VALID_STATUS_UPDATE_VALUES = {
        PromoteRequestStatus.APPROVED.value,
        PromoteRequestStatus.CLOSED.value,
    }

    __tablename__ = "promote_requests"

    id = Column(Integer, primary_key=True)

    title = Column(String(120), unique=False, nullable=False)
    description = Column(String(1000), unique=False, nullable=True)

    created_at = Column(DateTime(1000), unique=False, nullable=False)
    closed_at = Column(DateTime(1000), unique=False, nullable=True)

    model_name = Column(String(500), unique=False, nullable=False)
    version_id = Column(String(100), unique=False, nullable=False)

    target_stage = Column(
        Enum(
            ModelVersionStage,
            name="model_version_stage",
            validate_strings=True,
            nullable=False,
        )
    )

    static_champion_version_id = Column(
        String(100), unique=False, nullable=True
    )

    author_username = Column(String(200), unique=False, nullable=False)
    reviewer_username = Column(String(200), unique=False, nullable=True)

    status = Column(
        Enum(
            PromoteRequestStatus,
            name="promote_request_status",
            validate_strings=True,
        )
    )

    review_comment = Column(String(1000), unique=False, nullable=True)

    def __repr__(self):
        return f"<PromoteRequest {self.title}>"
