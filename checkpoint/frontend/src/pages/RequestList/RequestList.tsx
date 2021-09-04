import * as React from 'react';
import { MultiSelector, RequestTable } from '@domino-research/ui';
import { PromoteRequest } from '@domino-research/ui/dist/utils/types';
import { Row, Col, Button } from 'antd';
import { Link } from 'react-router-dom';
import { useState } from 'react';

import OuterLayout from '../../components/OuterLayout';

export interface Props {
  data?: PromoteRequest[];
}

const Component: React.FC<Props> = ({ data }) => {
  const [modelFilter, setModelFilter] = useState<(string | number)[]>([]);
  const [statusFilter, setStatusFilter] = useState<(string | number)[]>([]);
  const [requests, setRequests] = useState<PromoteRequest[] | undefined>(undefined);
  React.useEffect(() => {
    if (data) {
      console.log('HERE');
      let filteredRequests: PromoteRequest[] = Object.assign([], data);
      if (modelFilter.length > 0) {
        filteredRequests = filteredRequests.filter((request) => modelFilter.includes(request.model_name));
      }

      if (statusFilter.length > 0) {
        filteredRequests = filteredRequests.filter((request) => {
          if (request.status === 'open') {
            return statusFilter.includes('Open');
          }
          if (request.status === 'closed' || request.status === 'approved') {
            return statusFilter.includes('Closed');
          }
          return false;
        });
      }
      // if (environmentFilter !== 'All environments') {
      //   tempEnvironments = tempEnvironments.map((env) => {
      //     env.deploymentCards = env?.deploymentCards?.filter(
      //       (deploymentCards) => deploymentCards?.deploymentName === environmentFilter,
      //     );
      //     return env;
      //   });
      // }
      setRequests(filteredRequests);
    } else {
      setRequests(undefined);
    }
  }, [modelFilter, statusFilter, data]);

  const modelOptions = Array.from(new Set(data?.map((request) => request.model_name) || []));
  return (
    <div>
      <OuterLayout>
        <Row gutter={[16, 24]} justify="space-between" align="middle" style={{ padding: '30px' }}>
          <Col>
            <MultiSelector
              placeholder="Model"
              data={modelOptions.map((model_name) => ({ displayName: model_name, value: model_name }))}
              onChangeValue={setModelFilter}
            />
            <span style={{ marginLeft: '10px' }}>
              <MultiSelector
                placeholder="Status"
                data={[
                  { displayName: 'Open', value: 'Open' },
                  { displayName: 'Closed', value: 'Closed' },
                ]}
                onChangeValue={setStatusFilter}
              />
            </span>
          </Col>
          <Col>
            <Button type="primary">
              <Link to="/checkpoint/requests/new">New Promote Request</Link>
            </Button>
          </Col>
          <Col span={24}>
            <RequestTable data={requests} />
          </Col>
        </Row>
      </OuterLayout>
    </div>
  );
};

export default Component;
