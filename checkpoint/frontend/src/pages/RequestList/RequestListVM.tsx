import * as React from 'react';
import { AppState } from '../../redux/state';
import { fetchRequests } from '../../redux/actions/appActions';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import RequestList from './RequestList';

const mapState = (state: AppState) => {
  return {
    requests: state.app.requests,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {
    fetchRequests: () => dispatch(fetchRequests()),
  };
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const RequestListVM: React.FC<Props> = ({ requests, fetchRequests }) => {
  React.useEffect(() => {
    console.log('Home set');
    fetchRequests();
    return () => {
      console.log('Home clear');
    };
  }, []);
  return <RequestList data={requests} />;
};

const ConnectedViewModel = connector(RequestListVM);

export default ConnectedViewModel;
