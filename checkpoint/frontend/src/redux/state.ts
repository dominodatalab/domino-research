import { PromoteRequest, Model, ModelVersion, RequestDetails } from '@domino-research/ui/dist/utils/types';

export interface AppState {
  app: RootState;
}

export interface RootState {
  requests?: PromoteRequest[];
  models?: Model[];
  stages?: string[];
  versions?: ModelVersion[];
  error?: string;
  details?: RequestDetails;
}
