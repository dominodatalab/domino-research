import * as React from 'react';
import OuterLayout from '../../components/OuterLayout';
import { Row, Col, Button } from 'antd';
import { PageHeader } from 'antd';
import { useHistory } from 'react-router-dom';
import { Divider, Form, Input, Select } from 'antd';
import { useLocation } from 'react-router-dom';
import { useState } from 'react';
import { CreatePromoteRequest } from '../../../packages/ui/dist/utils/types';
import { submitRequest } from 'redux/actions/appActions';

export interface Props {
  models?: string[];
  versions?: string[];
  fetchVersions: (model: string) => void;
}

const RequestForm: React.FC<Props> = ({ models, versions, fetchVersions }) => {
  const history = useHistory();
  const search = useLocation().search;
  const params = new URLSearchParams(search);
  const defaultModel = params.get('model') || undefined;
  const defaultVersion = params.get('version') || undefined;
  const defaultTarget = params.get('target') || undefined;

  const [name, setName] = useState<string | undefined>(undefined);
  const [description, setDescription] = useState<string | undefined>(undefined);
  const [model, setModel] = useState<string | undefined>(undefined);
  const [version, setVersion] = useState<string | undefined>(undefined);
  const [target, setTarget] = useState<string | undefined>(undefined);

  if (defaultModel) {
    fetchVersions(defaultModel);
  }

  const onModelChange = (model: string) => {
    fetchVersions(model);
    setModel(model);
  };

  const handleSubmit = (values: CreatePromoteRequest) => {
    submitRequest(values);
  };

  return (
    <div>
      <OuterLayout>
        <Row gutter={[16, 24]} justify="space-between" align="middle" style={{ padding: '30px' }}>
          <Col span={12} offset={6}>
            <PageHeader className="site-page-header" onBack={() => history.goBack()} title="New Promote Request" />
            <Divider />
            <Form name="promote_request" labelCol={{ span: 6 }} wrapperCol={{ span: 14 }} onFinish={handleSubmit}>
              <Form.Item label="Title" name="title" rules={[{ required: true }]}>
                <Input value={name} onChange={(e) => setName(e.target.value)} />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea
                  autoSize={{ minRows: 10 }}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </Form.Item>
              <Form.Item label="Model" name="model_name" rules={[{ required: true }]}>
                <Select
                  disabled={models === undefined}
                  value={model}
                  defaultValue={defaultModel}
                  onChange={onModelChange}
                >
                  {models?.map((model, i) => (
                    <Select.Option value={model} key={i}>
                      {model}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item label="Version" name="model_version" rules={[{ required: true }]}>
                <Select disabled={versions === undefined} value={version} onChange={setVersion}>
                  {versions?.map((version, i) => (
                    <Select.Option value={version} key={i}>
                      {version}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item label="Target Stage" name="target_stage" rules={[{ required: true }]}>
                <Select value={target} onChange={setTarget}>
                  <Select.Option value="production">Production</Select.Option>
                  <Select.Option value="staging">Staging</Select.Option>
                  <Select.Option value="archived">Archived</Select.Option>
                  <Select.Option value="none">None</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item wrapperCol={{ offset: 6, span: 14 }}>
                <Button type="primary" htmlType="submit">
                  Create
                </Button>
              </Form.Item>
            </Form>
          </Col>
        </Row>
      </OuterLayout>
    </div>
  );
};

export default React.memo(RequestForm);
