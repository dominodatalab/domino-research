import * as React from 'react';
import { Input } from 'antd';

export interface SearchTableProps {
  onSearch: (value: string) => void;
  width?: number;
}

const { Search } = Input;

const SearchTable: React.FC<SearchTableProps> = ({ onSearch, width }) => (
  <Search placeholder="Search" onSearch={onSearch} style={{ width: width || 300 }} />
);

export default React.memo(SearchTable);
