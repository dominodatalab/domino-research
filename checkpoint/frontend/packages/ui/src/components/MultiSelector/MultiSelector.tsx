import * as React from 'react';
import { Select } from 'antd';

export interface DropdownProps {
  value: string | number;
  displayName: string;
}

const { Option } = Select;

export interface MultiSelectorProps {
  data: DropdownProps[];
  onChangeValue: (value: (string | number)[]) => void;
  placeholder?: string;
}

const MultiSelector: React.FC<MultiSelectorProps> = ({ data, onChangeValue, placeholder }) => {
  return (
    <Select
      mode="tags"
      style={{ width: '360px' }}
      onChange={onChangeValue}
      tokenSeparators={[',']}
      placeholder={placeholder}
    >
      {data?.map((dto) => (
        <Option key={`key_${dto.value}`} value={dto.value}>
          {dto.value}
        </Option>
      ))}
    </Select>
  );
};

export default React.memo(MultiSelector);
