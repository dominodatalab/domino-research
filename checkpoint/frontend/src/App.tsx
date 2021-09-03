import * as React from 'react';
import { Provider } from 'react-redux';
import { store } from './redux/store';
import { Root } from 'components';

const App: React.FC = () => (
  <>
    <div>
      <Provider store={store}>
        <Root />
      </Provider>
    </div>
  </>
);

export default App;
