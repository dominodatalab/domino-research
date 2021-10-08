import * as React from 'react';
import { AppState } from '../../redux/state';
import {
  fetchModels,
  fetchVersions,
  fetchStages,
  submitRequest,
  clearSubmitRequestError,
} from '../../redux/actions/appActions';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import RequestForm from './RequestForm';
import { CreatePromoteRequest } from '../../utils/types';
import { History } from 'history';

const mapState = (state: AppState) => {
  return {
    models: state.app.models,
    versions: state.app.versions,
    stages: state.app.stages,
    error: state.app.error,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {
    fetchModels: () => dispatch(fetchModels()),
    fetchVersions: (model: string) => dispatch(fetchVersions(model)),
    fetchStages: () => dispatch(fetchStages()),
    onSubmit: (history: History, request: CreatePromoteRequest) => dispatch(submitRequest(history, request)),
    clearSubmitRequestError: () => dispatch(clearSubmitRequestError()),
  };
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const RequestFormVM: React.FC<Props> = ({
  models,
  versions,
  stages,
  error,
  fetchVersions,
  fetchModels,
  fetchStages,
  onSubmit,
  clearSubmitRequestError,
}) => {
  React.useEffect(() => {
    fetchModels();
    fetchStages();
    clearSubmitRequestError();
  }, []);
  return (
    <RequestForm
      error={error}
      models={models}
      versions={versions}
      stages={stages}
      fetchVersions={fetchVersions}
      onSubmit={onSubmit}
    />
  );
};

const ConnectedViewModel = connector(RequestFormVM);

export default ConnectedViewModel;
