import React from 'react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { render } from '@testing-library/react';
import Breadcrumb from '../index';

const breadcrumb = [{ title: 'Breadcrumb 1' }, { url: '#', title: 'Breadcrumb 2' }];

describe('<BreadcrumbContainer />', () => {
  it('should render correctly', () => {
    const history = createMemoryHistory();
    const { container } = render(
      <Router history={history}>
        <Breadcrumb breadcrumb={breadcrumb} />
      </Router>,
    );
    expect(!!container).toBe(true);
  });
});
