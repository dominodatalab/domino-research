import * as React from 'react';
import { SearchTable, GenericTable } from '@domino-research/ui';
import { GenericTableProps } from '@domino-research/ui/dist/components/GenericTable/GenericTable';
import { Row, Col, Button } from 'antd';

import OuterLayout from '../../components/OuterLayout';

export interface Props {
  data?: GenericTableProps[];
}

const Component: React.FC<Props> = () => {
  return (
    <div>
      <OuterLayout>
        <Row gutter={[16, 24]} justify="space-between" align="middle">
          <Col>
            <SearchTable onSearch={() => console.log('From SearchTable')} />
          </Col>
          <Col>
            <Button disabled type="primary">
              New Project
            </Button>
          </Col>
          <Col span={24}>
            <GenericTable data={[]} />
          </Col>
        </Row>
      </OuterLayout>
    </div>
  );
};

export default React.memo(Component);
