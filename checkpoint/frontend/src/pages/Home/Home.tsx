import * as React from 'react';
import { HelloWorld } from '@domino-research/ui';
import OuterLayout from '../../components/OuterLayout';

export interface HomeProps {
  name: string;
}

const Home: React.FC<HomeProps> = ({ name }) => {
  return (
    <div>
      <OuterLayout>
        <HelloWorld name={'Requests'} />
      </OuterLayout>
    </div>
  );
};

export default React.memo(Home);
