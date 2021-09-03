import * as React from 'react';
import { AppState } from '../../redux/state';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import Home from './Home';

const mapState = (state: AppState) => {
  return {
    name: state.app.user_info?.user,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {};
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const HomeVM: React.FC<Props> = ({ name }) => {
  React.useEffect(() => {
    console.log('Home set');
    // fetchProjects();
    // const projects_timer = setInterval(() => fetchProjects(), projects_refresh_interval_ms);
    return () => {
      console.log('Home clear');
      // clearInterval(projects_timer);
    };
  }, []);
  return <Home name={name || 'unknown'} />;
};

const ConnectedViewModel = connector(HomeVM);

export default ConnectedViewModel;
