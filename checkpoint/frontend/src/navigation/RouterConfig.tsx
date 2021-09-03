import * as React from 'react';
import { Switch, Route } from 'react-router-dom';
import { Home, ProjectList } from '../pages';
import { ROOT, PROJECT_LIST } from './CONSTANTS';
import { default as usePageTracking } from '../util/usePageTracking';

export const RouterConfig: React.FC = () => {
  usePageTracking();
  return (
    <Switch>
      {/* List all public routes here */}
      <Route exact path={ROOT} component={Home} />
      {/* List all private/auth routes here */}
      {/* List a generic 404-Not Found route here */}
      <Route exact path={PROJECT_LIST} component={ProjectList} />
      <Route path="*">
        <div>404 not found.</div>
      </Route>
    </Switch>
  );
};
