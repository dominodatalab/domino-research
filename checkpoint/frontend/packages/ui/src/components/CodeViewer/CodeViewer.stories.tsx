import * as React from 'react';
// also exported from '@storybook/react' if you can deal with breaking changes in 6.1
import { Story, Meta } from '@storybook/react';
import CodeViewer, { CodeViewerProps } from './CodeViewer';

export default {
  title: 'Code Viewer',
  component: CodeViewer,
} as Meta;

const Template: Story<CodeViewerProps> = (args) => <CodeViewer {...args} />;
const timeStamp = new Date('January 1, 1970 00:00:00Z');
const multipleLines = (lines: number, withTimestamp = true) => {
  const logLine = [];
  for (let i = 1; i < lines; i++) {
    logLine.push({
      line: 'Hello Domino Data Lab',
      timestamp: withTimestamp ? timeStamp.toISOString() : null,
      tags: [
        { key: 'pod', value: 'feature-branch' },
        { key: 'container', value: 'wait' },
        { key: 'namespace', value: 'default' },
      ],
    });
  }
  return logLine;
};

export const Default = Template.bind({});
Default.args = {
  title: 'Code Viewer',
  logLines: multipleLines(50),
};

export const NoStampTime = Template.bind({});
NoStampTime.args = {
  title: 'Code Viewer',
  logLines: multipleLines(10, false),
};
