import * as React from 'react';
import { AppState } from '../../redux/state';
import { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from 'redux';
import { connect, ConnectedProps } from 'react-redux';
import { GenericTableProps } from '@domino-research/ui/dist/components/GenericTable/GenericTable';
import ProjectList from './ProjectList';

const mapState = (state: AppState) => {
  const data: GenericTableProps[] = [];
  return {
    name: state.app.user_info?.user,
    data,
  };
};

const mapDispatchToProps = (dispatch: ThunkDispatch<AppState, void, AnyAction>) => {
  return {};
};

const connector = connect(mapState, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

type Props = PropsFromRedux;

const ProjectListVM: React.FC<Props> = ({ data }) => {
  React.useEffect(() => {
    console.log('Home set');
    // fetchProjects();
    // const projects_timer = setInterval(() => fetchProjects(), projects_refresh_interval_ms);
    return () => {
      console.log('Home clear');
      // clearInterval(projects_timer);
    };
  }, []);
  return <ProjectList data={data || undefined} />;
};

const ConnectedViewModel = connector(ProjectListVM);

export default ConnectedViewModel;
