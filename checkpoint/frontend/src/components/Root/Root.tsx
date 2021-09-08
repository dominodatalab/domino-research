import * as React from 'react';
import { useEffect } from 'react';
import { connect, ConnectedProps } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { RouterConfig } from '../../navigation/RouterConfig';

const mapState = () => {
  return {};
};

const mapDispatchToProps = () => {
  return {};
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const Root: React.FC<Props> = ({}) => {
  useEffect(() => {
    console.log('Root set');
    return () => {
      console.log('Root clear');
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
