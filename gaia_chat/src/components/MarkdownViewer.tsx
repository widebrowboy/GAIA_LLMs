import React from 'react';
import matter from 'gray-matter';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownViewerProps {
  markdown: string;
}

const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ markdown }) => {
  let content = '';
  let data: any = {};
  let parseError = false;

  try {
    const parsed = matter(markdown);
    content = parsed.content;
    data = parsed.data;
  } catch (e) {
    parseError = true;
  }

  if (parseError || !markdown) {
    return (
      <div className="prose prose-red">
        <p>⚠️ 문서 파싱 오류 또는 빈 응답입니다.</p>
      </div>
    );
  }

  return (
    <div className="mb-4">
      {data.title && (
        <h1 className="text-xl font-bold mb-1">{data.title}</h1>
      )}
      {(data.created || data.model) && (
        <div className="text-xs text-gray-500 mb-2">
          {data.created ? <span>{data.created}</span> : null}
          {data.created && data.model ? ' | ' : null}
          {data.model ? <span>{data.model}</span> : null}
        </div>
      )}
      <article className="prose prose-lg max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </article>
    </div>
  );
};

export default MarkdownViewer;
