import * as React from 'react';
import { AppState } from '../../redux/state';
import { fetchModels, fetchVersions } from '../../redux/actions/appActions';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import RequestForm from './RequestForm';

const mapState = (state: AppState) => {
  return {
    models: state.app.models,
    versions: state.app.versions,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {
    fetchModels: () => dispatch(fetchModels()),
    fetchVersions: (model: string) => dispatch(fetchVersions(model)),
  };
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const RequestFormVM: React.FC<Props> = ({ models, versions, fetchVersions, fetchModels }) => {
  React.useEffect(() => {
    console.log('Home set');
    fetchModels();
    return () => {
      console.log('Home clear');
    };
  }, []);
  return <RequestForm models={models} versions={versions} fetchVersions={fetchVersions} />;
};

const ConnectedViewModel = connector(RequestFormVM);

export default ConnectedViewModel;
