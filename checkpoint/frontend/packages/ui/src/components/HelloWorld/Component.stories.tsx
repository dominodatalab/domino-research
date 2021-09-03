import * as React from 'react';
import { Story, Meta } from '@storybook/react';
import { Properties, default as Component } from './Component';

export default {
  title: 'Hello World',
  component: Component,
} as Meta;

const Template: Story<Properties> = (args) => <Component {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: 'John Doe',
};
