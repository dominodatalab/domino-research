import * as React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SearchTable, { SearchTableProps } from '../SearchTable';

describe('StatusTag', () => {
  let props: SearchTableProps;
  beforeEach(() => {
    props = {
      onSearch: (val) => console.log(val),
    };
  });
  describe('render()', () => {
    it('should render', () => {
      const { container } = render(<SearchTable {...props} />);
      expect(!!container).toBe(true);
    });
  });
});
