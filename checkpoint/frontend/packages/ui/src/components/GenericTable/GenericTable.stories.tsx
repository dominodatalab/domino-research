import * as React from 'react';
// also exported from '@storybook/react' if you can deal with breaking changes in 6.1
import { Story, Meta } from '@storybook/react';
import GenericTable, { GenericTableProps } from './GenericTable';

export default {
  title: 'Generic Table',
  component: GenericTable,
} as Meta;

const Template: Story<GenericTableProps> = (args) => <GenericTable {...args} />;

export const Default = Template.bind({});
Default.args = {
  data: [
    {
      id: '1',
      param1: 'undefined',
      param2: 'undefined',
      param3: 'undefined',
    },
    {
      id: '2',
      param1: 'undefined',
      param2: 'undefined',
      param3: 'undefined',
    },
    {
      id: '3',
      param1: 'undefined',
      param2: 'undefined',
      param3: 'undefined',
    },
  ],
};

export const Empty = Template.bind({});
Empty.args = {
  data: [],
};

export const Loading = Template.bind({});
Loading.args = {
  data: undefined,
};
