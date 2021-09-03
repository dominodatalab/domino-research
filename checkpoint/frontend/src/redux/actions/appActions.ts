// You can use CONSTANTS.js file for below definitions of constants and import here.
import { ThunkDispatch } from 'redux-thunk';
import { AppState } from '../state';
import { UserInfo } from '@domino-research/ui/dist/utils/types';
import { AnyAction } from 'redux';

export const API_ERROR = 'API_ERROR';

export const APIError = (error: string): AnyAction => ({
  type: API_ERROR,
  error: error,
});

export const FETCH_USER_INFO = 'FETCH_USER_INFO';

export const GOT_USER_INFO = 'GOT_USER_INFO';

export const gotUserInfo = (user_info: UserInfo): AnyAction => ({
  type: GOT_USER_INFO,
  user_info: user_info,
});

export const fetchUserInfo = () => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    const response = await fetch('/oauth2/userinfo');
    console.log(response);
    if (response.status === 401) {
      dispatch(Unauthorized());
    } else if (response.status === 200) {
      try {
        dispatch(gotUserInfo(await response.json()));
      } catch {}
    }
  };
};

export const UNAUTHORIZED = 'UNAUTHORIZED';

export const Unauthorized = (): AnyAction => ({
  type: UNAUTHORIZED,
});
