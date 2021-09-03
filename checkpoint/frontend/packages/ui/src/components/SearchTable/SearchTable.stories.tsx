import * as React from 'react';
import { Story, Meta } from '@storybook/react';
import SearchTable, { SearchTableProps } from './SearchTable';

export default {
  title: 'Search Table',
  component: SearchTable,
} as Meta;

const Template: Story<SearchTableProps> = (args) => <SearchTable {...args} />;

export const Default = Template.bind({});

Default.args = {
  onSearch: (val) => console.log(val),
};
