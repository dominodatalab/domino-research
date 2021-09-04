import { createReducer } from 'typesafe-actions';
import { RootState } from '../state';

const initialState = {
  requests: undefined,
  models: undefined,
  versions: undefined,
} as RootState;

export const appReducer = createReducer(initialState, {
  API_ERROR: (state) => {
    return state;
  },
  GOT_MODELS: (state, action) => {
    return {
      ...state,
      models: action.models,
    };
  },
  GOT_VERSIONS: (state, action) => {
    return {
      ...state,
      versions: action.versions,
    };
  },
  GOT_REQUESTS: (state, action) => {
    return {
      ...state,
      requests: action.requests,
    };
  },
});
