import * as React from 'react';
import { Row, Col, Space } from 'antd';
import s from './CodeViewer.module.scss';

interface TagProps {
  key: string;
  value: string;
}

interface LogLineDto {
  line: string;
  timestamp: string;
  tags: TagProps[];
}

export interface CodeViewerProps {
  title?: string;
  logLines?: LogLineDto[];
}

const CodeViewer: React.FC<CodeViewerProps> = ({ title, logLines }) => {
  return (
    <div className={s.codeViewerContainer}>
      <div className="ant-descriptions-header">
        <div className="ant-descriptions-title">{title}</div>
      </div>
      <Row gutter={[16, 16]} className={s.codeViewerRow}>
        {logLines?.map(({ line, timestamp }, index) => (
          <Col key={index}>
            <Space align="start" size="middle">
              <div className={s.line}>{index < 9 ? `0${index + 1}` : index + 1}</div>
              {timestamp && <div className={s.date}>{timestamp}</div>}
              <div className={s.line}>{line}</div>
            </Space>
          </Col>
        ))}
      </Row>
    </div>
  );
};
export default React.memo(CodeViewer);
