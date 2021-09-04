import * as React from 'react';
import { HelloWorld } from '@domino-research/ui';
import OuterLayout from '../../components/OuterLayout';

export interface Props {
  request_id?: string;
}

const ShowRequest: React.FC<Props> = ({ request_id }) => {
  return (
    <div>
      <OuterLayout>
        <p>Show Request</p>
        <HelloWorld name={`Request ${request_id}`} />
      </OuterLayout>
    </div>
  );
};

export default React.memo(ShowRequest);
