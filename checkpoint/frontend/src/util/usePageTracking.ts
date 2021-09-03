import { useEffect } from 'react';

const usePageTracking = (): void => {
  useEffect(() => {
    window.Intercom('update');
  });
};

export default usePageTracking;
