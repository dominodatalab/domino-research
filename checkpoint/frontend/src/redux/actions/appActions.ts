// You can use CONSTANTS.js file for below definitions of constants and import here.
import { ThunkDispatch } from 'redux-thunk';
import { AppState } from '../state';
import { PromoteRequest, CreatePromoteRequest } from '@domino-research/ui/dist/utils/types';
import { AnyAction } from 'redux';
import { History } from 'history';

export const API_ERROR = 'API_ERROR';

export const FETCH_MODELS = 'FETCH_MODELS';

export const GOT_MODELS = 'GOT_MODELS';

export const gotModels = (models: string[]): AnyAction => ({
  type: GOT_MODELS,
  models: models,
});

export const fetchModels = () => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    const response = await fetch('http://localhost:5000/checkpoint/api/models');
    if (response.status === 200) {
      try {
        dispatch(gotModels(await response.json()));
      } catch {}
    } else {
      console.error(response);
    }
  };
};

export const FETCH_VERSIONS = 'FETCH_VERSIONS';

export const GOT_VERSIONS = 'GOT_VERSIONS';

export const gotVersions = (versions: string[]): AnyAction => ({
  type: GOT_VERSIONS,
  versions: versions,
});

export const fetchVersions = (model: string) => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    const response = await fetch(`http://localhost:5000/checkpoint/api/models/${model}/versions`);
    if (response.status === 200) {
      try {
        dispatch(gotVersions(await response.json()));
      } catch {}
    } else {
      console.error(response);
    }
  };
};

export const FETCH_REQUESTS = 'FETCH_REQUESTS';

export const GOT_REQUESTS = 'GOT_REQUESTS';

export const gotRequests = (requests: PromoteRequest[]): AnyAction => ({
  type: GOT_REQUESTS,
  requests: requests,
});

export const fetchRequests = () => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    const response = await fetch(`http://localhost:5000/checkpoint/api/requests`);
    if (response.status === 200) {
      try {
        dispatch(gotRequests(await response.json()));
      } catch {}
    } else {
      console.error(response);
    }
  };
};

export const FETCH_STAGES = 'FETCH_STAGES';

export const GOT_STAGES = 'GOT_STAGES';

export const gotStages = (stages: string[]): AnyAction => ({
  type: GOT_STAGES,
  stages: stages,
});

export const fetchStages = () => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    const response = await fetch(`http://localhost:5000/checkpoint/api/stages`);
    if (response.status === 200) {
      try {
        dispatch(gotStages(await response.json()));
      } catch {}
    } else {
      console.error(response);
    }
  };
};

export const SUBMIT_REQUEST = 'SUBMIT_REQUEST';

export const SUBMIT_REQUEST_ERROR = 'SUBMIT_REQUEST_ERROR';

export const gotSubmitRequestError = (error: string): AnyAction => ({
  type: SUBMIT_REQUEST_ERROR,
  error: error,
});

export const CLEAR_SUBMIT_REQUEST_ERROR = 'CLEAR_SUBMIT_REQUEST_ERROR';

export const clearSubmitRequestError = (): AnyAction => ({
  type: CLEAR_SUBMIT_REQUEST_ERROR,
});

export const submitRequest = (history: History, request: CreatePromoteRequest) => {
  return async (dispatch: ThunkDispatch<AppState, void, AnyAction>): Promise<void> => {
    try {
      const response = await fetch(`http://localhost:5000/checkpoint/api/requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (response.status === 201) {
        const data = await response.json();
        console.log(data);
        history.push(`/checkpoint/requests/${data.id}`);
        console.log('SUCCESS');
      } else {
        dispatch(
          gotSubmitRequestError(
            `Error submitting request (${response.status}: ${response.statusText}): ${await response.text()}`,
          ),
        );
      }
    } catch (error) {
      console.error(error);
    }
  };
};
