import * as React from 'react';
// import s from './Component.module.scss';
import { Typography } from 'antd';

const { Title } = Typography;

export interface Properties {
  name: string;
}

const Component: React.FC<Properties> = ({ name }) => {
  return <Title>Hello {name}!</Title>;
};

export default React.memo(Component);
