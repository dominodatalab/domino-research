from checkpoint.app import db
import enum


class ModelVersionStage(enum.Enum):
    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"


class PromoteRequestStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"


class PromoteRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), unique=False, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=True)

    model_name = db.Column(db.String(500), unique=False, nullable=False)
    model_version = db.Column(db.String(100), unique=False, nullable=False)

    current_stage = db.Column(
        db.Enum(
            ModelVersionStage,
            name="model_version_stage",
            validate_strings=True,
        )
    )
    target_stage = db.Column(
        db.Enum(
            ModelVersionStage,
            name="model_version_stage",
            validate_strings=True,
            nullable=False,
        )
    )

    author_username = db.Column(db.String(200), unique=False, nullable=False)
    reviewer_username = db.Column(db.String(200), unique=False, nullable=True)

    status = db.Column(
        db.Enum(
            PromoteRequestStatus,
            name="promote_request_status",
            validate_strings=True,
        )
    )

    review_comment = db.Column(db.String(1000), unique=False, nullable=True)

    def __repr__(self):
        return f"<PromoteRequest {self.title}>"


if __name__ == "__main__":
    db.create_all()
    p = PromoteRequest(
        title="test",
        description="test desc",
        model_name="some_model",
        model_version="3",
        current_stage=ModelVersionStage.STAGING,
        target_stage=ModelVersionStage.PRODUCTION,
        author_username="josh",
    )

    db.session.add(p)
    db.session.commit()

    print(PromoteRequest.query.first().current_stage)
    print()
    db.drop_all()
