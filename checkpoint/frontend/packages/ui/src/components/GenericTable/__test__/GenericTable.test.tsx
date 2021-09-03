import * as React from 'react';
import { render } from '@testing-library/react';

import GenericTable, { GenericTableProps } from '../GenericTable';

describe('MetricsTable', () => {
  let props: GenericTableProps;
  beforeEach(() => {
    props = {
      data: [
        {
          id: '1',
          param1: 'undefined',
          param2: 'undefined',
          param3: 'undefined',
        },
      ],
    };
  });
  describe('render()', () => {
    it('should render', () => {
      const { container } = render(<GenericTable {...props} />);
      expect(!!container).toBe(true);
      expect(container.getElementsByTagName('table').length).toBe(1);
    });
  });
});
