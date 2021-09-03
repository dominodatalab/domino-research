import * as React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import CodeViewer, { CodeViewerProps } from '../CodeViewer';

describe('CodeViewer', () => {
  let props: CodeViewerProps;
  beforeEach(() => {
    props = {
      title: 'Code Viewer',
      logLines: [
        {
          line: 'Hello Domino Data Lab',
          timestamp: new Date('January 1, 1970 00:00:00Z').toISOString(),
          tags: [
            { key: 'pod', value: 'feature-branch' },
            { key: 'container', value: 'wait' },
            { key: 'namespace', value: 'default' },
          ],
        },
      ],
    };
  });
  describe('render()', () => {
    it('should render', () => {
      const { container } = render(<CodeViewer {...props} />);
      expect(!!container).toBe(true);
      expect(container.getElementsByClassName('codeViewerContainer').length).toBe(1);
    });
  });
});
