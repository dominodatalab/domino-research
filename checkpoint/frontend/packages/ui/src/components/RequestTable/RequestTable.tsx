import * as React from 'react';
import { Table } from 'antd';
import { ColumnsType } from 'antd/es/table';
import { PromoteRequest } from '../../utils/types';
import { useHistory } from 'react-router-dom';

export interface RequestTableProps {
  data?: PromoteRequest[];
}

const columns: ColumnsType<PromoteRequest> = [
  {
    key: 'title',
    title: 'Title',
    dataIndex: 'title',
  },
  {
    key: 'model',
    title: 'Model',
    dataIndex: 'model_name',
  },
  {
    key: 'version',
    title: 'Version',
    dataIndex: 'version_id',
  },
  {
    key: 'author',
    title: 'Author',
    dataIndex: 'author_username',
  },
  {
    key: 'target',
    title: 'Target Stage',
    dataIndex: 'target_stage',
  },
  {
    key: 'status',
    title: 'Status',
    dataIndex: 'status',
  },
];

const RequestTable: React.FC<RequestTableProps> = ({ data }) => {
  const history = useHistory();
  return (
    <Table<PromoteRequest>
      bordered
      loading={data === undefined}
      columns={columns}
      dataSource={data}
      rowKey="id"
      onRow={(record) => {
        return {
          onClick: (e) => {
            e.preventDefault();
            history.push(`/checkpoint/requests/${record.id}`);
          },
        };
      }}
    />
  );
};

export default RequestTable;
