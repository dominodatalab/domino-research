import * as React from 'react';
import { render } from '@testing-library/react';

import { default as Component, Props } from '../Component';

describe('Component', () => {
  let props: Props;

  beforeEach(() => {
    props = {
      name: 'John Doe',
    };
  });

  describe('render()', () => {
    it('should render', () => {
      const { container } = render(<Component {...props} />);
      expect(!!container).toBe(true);
      expect(container.getElementsByClassName('ant-typography').length).toBe(1);
      expect(container.getElementsByClassName('ant-typography')[0].textContent).toBe('Hello John Doe!');
    });
  });
});
