import * as React from 'react';
import { useEffect } from 'react';
import { fetchUserInfo } from 'redux/actions/appActions';
import { user_info_refresh_interval_ms } from 'config';
import { ThunkDispatch } from 'redux-thunk';
import { AppState } from '../../redux/state';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { RouterConfig } from '../../navigation/RouterConfig';

const mapState = () => {
  return {};
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {
    fetchUserInfo: () => dispatch(fetchUserInfo()),
  };
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const Root: React.FC<Props> = ({ fetchUserInfo }) => {
  useEffect(() => {
    console.log('Root set');
    fetchUserInfo();
    const user_info_timer = setInterval(() => fetchUserInfo(), user_info_refresh_interval_ms);
    return () => {
      console.log('Root clear');
      clearInterval(user_info_timer);
    };
  });
  return (
    <BrowserRouter>
      <RouterConfig />
    </BrowserRouter>
  );
};

const ConnectedRoot = connector(Root);

export default ConnectedRoot;
