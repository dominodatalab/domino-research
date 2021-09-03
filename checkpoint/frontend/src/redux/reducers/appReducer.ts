import { createReducer } from 'typesafe-actions';
import { RootState } from '../state';

const initialState = {
  intercom_initialized: false,
} as RootState;

export const appReducer = createReducer(initialState, {
  UNAUTHORIZED: (state) => {
    window.location.href = window.location.protocol + '//' + window.location.host + '/oauth2/sign_in';
    const result = {
      ...state,
    };
    delete result['user_info'];
    return result;
  },
  GOT_USER_INFO: (state, action) => {
    if (window.Intercom && !state.intercom_initialized) {
      window.Intercom('boot', {
        app_id: 'oqmqjpo9',
        email: action.user_info.email,
        name: action.user_info.user,
      });
      return {
        ...state,
        user_info: action.user_info,
        intercom_initialized: true,
      };
    }
    return {
      ...state,
      user_info: action.user_info,
    };
  },
  API_ERROR: (state) => {
    return state;
  },
});
