import { PromoteRequest } from '@domino-research/ui/dist/utils/types';

export interface AppState {
  app: RootState;
}

export interface RootState {
  requests?: PromoteRequest[];
  models?: string[];
  versions?: string[];
}
