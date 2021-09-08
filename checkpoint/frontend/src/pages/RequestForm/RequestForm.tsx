import * as React from 'react';
import OuterLayout from '../../components/OuterLayout';
import { Row, Col, Button, Alert } from 'antd';
import { PageHeader } from 'antd';
import { useHistory } from 'react-router-dom';
import { History } from 'history';
import { Divider, Form, Input, Select } from 'antd';
import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { CreatePromoteRequest, Model, ModelVersion } from '../../../packages/ui/dist/utils/types';

export interface Props {
  models?: Model[];
  versions?: ModelVersion[];
  stages?: string[];
  fetchVersions: (model: string) => void;
  onSubmit: (history: History, request: CreatePromoteRequest) => void;
  error?: string;
}

const RequestForm: React.FC<Props> = ({ error, models, versions, stages, fetchVersions, onSubmit }) => {
  const history = useHistory();
  const search = useLocation().search;
  const params = new URLSearchParams(search);
  const defaultModel = params.get('model') || undefined;
  const defaultVersion = params.get('version') || undefined;
  const defaultTarget = params.get('target') || undefined;

  useEffect(() => {
    if (defaultModel) {
      fetchVersions(defaultModel);
    }
  }, [defaultModel]);

  const onModelChange = (model: string) => {
    fetchVersions(model);
  };

  const handleSubmit = (values: CreatePromoteRequest) => {
    console.log(values);
    onSubmit(history, values);
  };

  return (
    <div>
      <OuterLayout>
        <Row gutter={[16, 24]} justify="space-between" align="middle" style={{ padding: '30px' }}>
          <Col span={12} offset={6}>
            <PageHeader className="site-page-header" title="New Promote Request" />
            <Divider />
            <Form name="promote_request" labelCol={{ span: 6 }} wrapperCol={{ span: 14 }} onFinish={handleSubmit}>
              <Form.Item label="Title" name="title" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea autoSize={{ minRows: 10 }} />
              </Form.Item>
              <Form.Item label="Model" name="model_name" rules={[{ required: true }]} initialValue={defaultModel}>
                <Select disabled={models === undefined} onChange={onModelChange}>
                  {models?.map((model, i) => (
                    <Select.Option value={model.name} key={i}>
                      {model.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item label="Version" name="version_id" initialValue={defaultVersion} rules={[{ required: true }]}>
                <Select disabled={versions === undefined}>
                  {versions?.map((version, i) => (
                    <Select.Option value={version.id} key={i}>
                      {version.id}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                label="Target Stage"
                name="target_stage"
                rules={[{ required: true }]}
                initialValue={defaultTarget}
              >
                <Select disabled={stages === undefined}>
                  {stages?.map((stage, i) => (
                    <Select.Option key={i} value={stage}>
                      {stage}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item wrapperCol={{ offset: 6, span: 14 }}>
                <Button type="primary" htmlType="submit">
                  Create
                </Button>
              </Form.Item>
            </Form>
            {error && <Alert message={error} type="error" />}
          </Col>
        </Row>
      </OuterLayout>
    </div>
  );
};

export default React.memo(RequestForm);
