import * as React from 'react';
import { Breadcrumb, Card } from 'antd';
import { Link } from 'react-router-dom';

export interface IBreadcrumb {
  url?: string;
  title: string;
}

export interface BreadcrumbProps {
  breadcrumb: IBreadcrumb[];
}

const BreadcrumbComponent: React.FC<BreadcrumbProps> = ({ breadcrumb }: BreadcrumbProps) => (
  <Card>
    <Breadcrumb>
      {breadcrumb.map(({ url, title }, index) => (
        <Breadcrumb.Item key={`item-${index}`}>{!!url ? <Link to={url}>{title}</Link> : title}</Breadcrumb.Item>
      ))}
    </Breadcrumb>
  </Card>
);

export default React.memo(BreadcrumbComponent);
