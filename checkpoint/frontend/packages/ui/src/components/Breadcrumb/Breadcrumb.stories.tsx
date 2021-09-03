import * as React from 'react';
import { Story, Meta } from '@storybook/react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import Breadcrumb, { BreadcrumbProps } from './Breadcrumb';

export default {
  title: 'Breadcrumb',
  component: Breadcrumb,
} as Meta;

const Template: Story<BreadcrumbProps> = (args) => {
  const history = createMemoryHistory();
  return (
    <Router history={history}>
      <Breadcrumb {...args} />
    </Router>
  );
};

export const Default = Template.bind({});

Default.args = {
  breadcrumb: [
    {
      url: 'https://docs.polarisml.com/en/latest/usage/quickstart.html',
      title: 'Breadcrumb 1',
    },
    {
      url: 'https://docs.polarisml.com/en/latest/usage/quickstart.html',
      title: 'Breadcrumb 2',
    },
    {
      url: 'https://docs.polarisml.com/en/latest/usage/quickstart.html',
      title: 'Breadcrumb 3',
    },
  ],
};
