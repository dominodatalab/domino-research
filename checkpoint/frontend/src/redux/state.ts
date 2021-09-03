import { UserInfo } from '@domino-research/ui/dist/utils/types';

export interface AppState {
  app: RootState;
}

export interface RootState {
  user_info?: UserInfo;
  intercom_initialized: boolean;
}
