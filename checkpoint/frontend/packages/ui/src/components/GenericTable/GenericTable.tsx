import * as React from 'react';
import { Table } from 'antd';
import { ColumnsType } from 'antd/es/table';

export interface GenericTableData {
  id?: string;
  param1: string;
  param2: string;
  param3: string;
}

export interface GenericTableProps {
  data?: GenericTableData[];
}

const columns: ColumnsType<GenericTableData> = [
  {
    key: 'param1',
    title: 'param1',
    dataIndex: 'param1',
  },
  {
    key: 'param2',
    title: 'param2',
    dataIndex: 'param2',
  },
  {
    key: 'param3',
    title: 'param3',
    dataIndex: 'param3',
  },
];

const GenericTable: React.FC<GenericTableProps> = ({ data }) => (
  <Table<GenericTableData>
    bordered
    loading={data === undefined}
    columns={columns}
    dataSource={data}
    title={() => 'Generic Table'}
    rowKey="id"
  />
);

export default React.memo(GenericTable);
