import * as React from 'react';
import { Switch, Route } from 'react-router-dom';
import { RequestList, ShowRequest, RequestForm } from '../pages';
import { REQUEST_LIST, REQUEST_FORM, SHOW_REQUEST } from './CONSTANTS';

export const RouterConfig: React.FC = () => {
  return (
    <Switch>
      {/* List all public routes here */}
      <Route exact path={REQUEST_FORM} component={RequestForm} />
      <Route exact path={SHOW_REQUEST} component={ShowRequest} />
      <Route exact path={REQUEST_LIST} component={RequestList} />
      {/* List all private/auth routes here */}
      {/* List a generic 404-Not Found route here */}
      <Route path="*">
        <div>404 not found.</div>
      </Route>
    </Switch>
  );
};
