import * as React from 'react';
import OuterLayout from '../../components/OuterLayout';
import { Row, Col, PageHeader, Card, Tag, Table, Input, Button, Form, Select, Typography } from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import { PromoteRequest, RequestDetails, CreateReview } from '@domino-research/ui/dist/utils/types';
import s from './ShowRequest.module.scss';
import { useHistory } from 'react-router-dom';
import { History } from 'history';

const { Text, Paragraph } = Typography;

export interface Props {
  request_id?: string;
  request?: PromoteRequest;
  details?: RequestDetails;
  onSubmit: (history: History, request_id: string, request: CreateReview) => void;
}

const getColor = (stage: string | undefined): string => {
  if (stage) {
    switch (stage.toLowerCase()) {
      case 'production': {
        return 'success';
      }
      case 'staging': {
        return 'warning';
      }
      default: {
        return 'default';
      }
    }
  } else {
    return 'default';
  }
};

const metricsColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Challenger',
    dataIndex: 'challenger',
    key: 'challenger',
  },
  {
    title: 'Champion',
    dataIndex: 'champion',
    key: 'champion',
  },
  {
    title: 'Change',
    dataIndex: 'change',
    key: 'change',
  },
];

const paramsColumns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Challenger',
    dataIndex: 'challenger',
    key: 'challenger',
  },
  {
    title: 'Champion',
    dataIndex: 'champion',
    key: 'champion',
  },
];

interface MetricDiff {
  name: string;
  champion?: string;
  challenger?: string;
  change?: string;
}

const diffMetrics = (challenger?: Record<string, number>, champion?: Record<string, number>): MetricDiff[] => {
  if (!champion) {
    champion = {};
  }
  if (!challenger) {
    challenger = {};
  }
  const keys = Array.from(new Set(Object.keys(champion).concat(Object.keys(challenger)))).sort();
  const result = [];
  for (const key of keys) {
    let change = undefined;
    if (champion[key] != null && challenger[key] != null) {
      change = (champion[key] - challenger[key]).toFixed(4);
    }

    let champion_value = undefined;
    if (champion[key] != null) {
      champion_value = champion[key].toFixed(4);
    }

    let challenger_value = undefined;
    if (challenger[key] != null) {
      challenger_value = challenger[key].toFixed(4);
    }

    result.push({
      name: key,
      champion: champion_value,
      challenger: challenger_value,
      change: change,
    });
  }
  return result;
};

interface ParameterDiff {
  name: string;
  champion?: string;
  challenger?: string;
}

// eslint-disable-next-line
const diffParams = (challenger?: Record<string, any>, champion?: Record<string, any>): ParameterDiff[] => {
  if (!champion) {
    champion = {};
  }
  if (!challenger) {
    challenger = {};
  }
  const keys = Array.from(new Set(Object.keys(champion).concat(Object.keys(challenger)))).sort();
  const result = [];
  for (const key of keys) {
    let champion_value = undefined;
    if (champion[key] != null) {
      champion_value = champion[key] + '';
    }

    let challenger_value = undefined;
    if (challenger[key] != null) {
      challenger_value = challenger[key] + '';
    }

    result.push({
      name: key,
      champion: champion_value,
      challenger: challenger_value,
    });
  }
  return result;
};

const ShowRequest: React.FC<Props> = ({ request_id, details, request, onSubmit }) => {
  const history = useHistory();
  const metricData = diffMetrics(
    details?.challenger_version_details.metrics,
    details?.champion_version_details?.metrics,
  );
  const metricRowSelection = details?.champion_version_details
    ? metricData.filter((diff) => diff.challenger != diff.champion).map((diff) => diff.name)
    : [];
  const paramData = diffParams(
    details?.challenger_version_details.parameters,
    details?.champion_version_details?.parameters,
  );
  const paramRowSelection = details?.champion_version_details
    ? paramData.filter((diff) => diff.challenger != diff.champion).map((diff) => diff.name)
    : [];

  const handleSubmit = (values: CreateReview) => {
    console.log(values);
    if (request_id) {
      onSubmit(history, request_id, values);
    }
  };

  let state = undefined;
  switch (request?.status) {
    case 'open': {
      state = <Tag color="default">Open</Tag>;
      break;
    }
    case 'closed': {
      state = <Tag color="error">Closed</Tag>;
      break;
    }
    case 'approved': {
      state = <Tag color="success">Approved</Tag>;
      break;
    }
    case undefined: {
      break;
    }
  }

  return (
    <div>
      <OuterLayout>
        <Row justify="space-between" align="middle" style={{ marginTop: '20px' }}>
          <Col lg={{ span: 16, offset: 4 }} xs={{ span: 24, offset: 0 }}>
            <PageHeader className="site-page-header" title={`#${request_id}: ${request?.title}`} />
            <Row>
              <Col span={9}>
                <Card size="small">
                  <span>Version {details?.challenger_version_details.id}</span>
                  <Tag style={{ float: 'right' }} color={getColor(details?.challenger_version_details.stage)}>
                    {details?.challenger_version_details.stage}
                  </Tag>
                </Card>
              </Col>
              <Col span={6} style={{ textAlign: 'center' }}>
                <Tag color="processing">
                  <ArrowRightOutlined style={{ color: '#1890ff', marginRight: '10px' }} />
                  is replacing
                  <ArrowRightOutlined style={{ color: '#1890ff', marginLeft: '10px' }} />
                </Tag>
              </Col>
              <Col span={9}>
                <Card size="small">
                  {details?.champion_version_details ? (
                    <>
                      <span>Version {details?.champion_version_details?.id}</span>
                      <Tag style={{ float: 'right' }} color={getColor(details?.champion_version_details?.stage)}>
                        {details?.champion_version_details?.stage}
                      </Tag>
                    </>
                  ) : (
                    <>
                      <Text type="secondary" italic>
                        No model in this stage.
                      </Text>
                      <Tag style={{ float: 'right' }} color={getColor(request?.target_stage)}>
                        {request?.target_stage}
                      </Tag>
                    </>
                  )}
                </Card>
              </Col>
            </Row>
            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
              <Col lg={{ span: 16 }} xs={{ span: 24 }}>
                <Card title="Description" style={{ height: '100%' }}>
                  {/* prettier-ignore */}
                  <pre style={{ maxHeight: '400px', overflow: 'auto' }}>
                    {request?.description == undefined || request?.description == '' ? (
                      <Paragraph disabled italic>
                        No description provided.
                      </Paragraph>
                    ) : (
                      <Paragraph>{request?.description}</Paragraph>
                    )}
                  </pre>
                </Card>
              </Col>
              <Col lg={{ span: 8 }} xs={{ span: 24 }}>
                <Card title="Details" style={{ height: '100%' }}>
                  <p>
                    <strong>Model: </strong>
                    {request?.model_name}
                  </p>
                  <p>
                    <strong>Author: </strong>
                    {request?.author_username}
                  </p>
                  <p>
                    <strong>Created: </strong>
                    {request && new Date(request?.created_at_epoch * 1000).toLocaleString('en-US')}
                  </p>
                </Card>
              </Col>
            </Row>
            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
              <Col xl={{ span: 14 }} xs={{ span: 24 }}>
                <Card title="Metrics" style={{ height: '100%' }} bodyStyle={{ padding: '0px' }}>
                  <Table
                    dataSource={metricData}
                    pagination={false}
                    columns={metricsColumns}
                    rowSelection={{ selectedRowKeys: metricRowSelection }}
                    className={s.diffTable}
                    rowKey="name"
                  />
                </Card>
              </Col>
              <Col xl={{ span: 10 }} xs={{ span: 24 }}>
                <Card title="Parameters" style={{ height: '100%' }} bodyStyle={{ padding: '0px' }}>
                  <Table
                    dataSource={paramData}
                    pagination={false}
                    columns={paramsColumns}
                    rowSelection={{ selectedRowKeys: paramRowSelection }}
                    className={s.diffTable}
                    rowKey="name"
                  />
                </Card>
              </Col>
            </Row>
            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
              <Col lg={{ span: 16, offset: 4 }} xs={{ span: 24, offset: 0 }}>
                <Card title="Review" style={{ height: '100%' }} extra={state}>
                  {request?.status == 'open' && (
                    <Form name="review" labelCol={{ span: 3 }} wrapperCol={{ span: 21 }} onFinish={handleSubmit}>
                      <Form.Item label="Comment" name="review_comment">
                        <Input.TextArea autoSize={{ minRows: 5 }} />
                      </Form.Item>
                      <Form.Item label="Action" name="status" rules={[{ required: true }]}>
                        <Select>
                          <Select.Option value="approved">Approve</Select.Option>
                          <Select.Option value="closed">Close</Select.Option>
                        </Select>
                      </Form.Item>
                      <Form.Item wrapperCol={{ offset: 20, span: 4 }}>
                        <Button type="primary" htmlType="submit">
                          Submit
                        </Button>
                      </Form.Item>
                    </Form>
                  )}
                  {(request?.status == 'closed' || request?.status == 'approved') && (
                    <div>
                      <Paragraph type="secondary">
                        By {request?.reviewer_username}
                        {request && request?.closed_at_epoch && (
                          <span> on {new Date(request?.closed_at_epoch * 1000).toLocaleString('en-US')}</span>
                        )}
                        .
                      </Paragraph>
                      {request?.review_comment == undefined || request?.review_comment == '' ? (
                        <Paragraph disabled italic>
                          No comment provided.
                        </Paragraph>
                      ) : (
                        <Paragraph>{request?.review_comment}</Paragraph>
                      )}
                    </div>
                  )}
                </Card>
              </Col>
            </Row>
          </Col>
        </Row>
      </OuterLayout>
    </div>
  );
};

export default React.memo(ShowRequest);
