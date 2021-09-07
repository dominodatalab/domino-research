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
  GOT_STAGES: (state, action) => {
    return {
      ...state,
      stages: action.stages,
    };
  },
  GOT_REQUESTS: (state, action) => {
    return {
      ...state,
      requests: action.requests,
    };
  },
  SUBMIT_REQUEST_ERROR: (state, action) => {
    return {
      ...state,
      error: action.error,
    };
  },
  CLEAR_SUBMIT_REQUEST_ERROR: (state) => {
    return {
      ...state,
      error: undefined,
    };
  },
  GOT_REQUEST_DETAILS: (state, action) => {
    return {
      ...state,
      details: action.details,
    };
  },
  CLEAR_REQUEST_DETAILS: (state, action) => {
    return {
      ...state,
      details: undefined,
    };
  },
});
