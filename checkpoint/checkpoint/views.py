from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PromoteRequestView:
    id: int
    status: str
    title: str
    description: str
    model_name: str
    version_id: str
    target_stage: str
    author_username: str
    reviewer_username: str
    review_comment: str


@dataclass
class VersionDetailsView:
    id: str
    stage: str
    metrics: Dict[str, Any]
    parameters: Dict[str, Any]
    tags: Dict[str, str]


@dataclass
class PromoteRequestDetailsView:
    promote_request_id: int
    challenger_version_details: VersionDetailsView
    champion_version_details: Optional[VersionDetailsView]
