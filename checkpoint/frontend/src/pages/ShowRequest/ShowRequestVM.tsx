import * as React from 'react';
import { AppState } from '../../redux/state';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import ShowRequest from './ShowRequest';
import { useParams } from 'react-router-dom';

const mapState = (state: AppState) => {
  return {
    requests: state.app.requests,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {};
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

interface Params {
  request_id?: string;
}

const ShowRequestVM: React.FC<Props> = ({ requests }) => {
  const { request_id } = useParams<Params>();
  React.useEffect(() => {
    console.log('Home set');
    // fetchProjects();
    // const projects_timer = setInterval(() => fetchProjects(), projects_refresh_interval_ms);
    return () => {
      console.log('Home clear');
      // clearInterval(projects_timer);
    };
  }, []);
  return <ShowRequest request_id={request_id} />;
};

const ConnectedViewModel = connector(ShowRequestVM);

export default ConnectedViewModel;
