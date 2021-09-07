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
  model_version: string;
  target_stage: string;
}

export interface Model {
  name: string;
}

export interface ModelVersion {
  model_name: string;
  id: string;
}