export interface UserInfo {
  user: string;
  email: string;
}

export interface PromoteRequest {
  title: string;
  description?: string;
  model_name: string;
  model_version: string;
  target_stage: string;
  current_stage: string;
  id: number;
  author_username: string;
  reviewer_username?: string;
  review_comment?: string,
  status: string
}

export interface CreatePromoteRequest {
  title: string;
  description?: string;
  model_name: string;
  version_id: string;
  target_stage: string;
}

export interface Model {
  name: string;
}

export interface ModelVersion {
  model_name: string;
  id: string;
}

export interface RequestDetails {
  promote_request_id: number;
  challenger_version_details: VersionDetails;
  champion_version_details?: VersionDetails;
}

export interface VersionDetails {
  id: string;
  stage: string;
  tags: Record<string, string>,
  parameters: Record<string, any>,
  metrics: Record<string, number>,
}