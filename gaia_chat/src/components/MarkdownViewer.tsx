import React from 'react';
import matter from 'gray-matter';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownViewerProps {
  markdown: string;
}

const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ markdown }) => {
  const { content, data } = matter(markdown);
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
