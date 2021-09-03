import React from 'react';
import { render } from '@testing-library/react';

import OuterLayout from '../OuterLayout';

describe('<OuterLayout />', () => {
  it('should render correctly', () => {
    const { container } = render(<OuterLayout />);
    expect(container.querySelectorAll('.site-layout').length).toEqual(1);
  });
});
