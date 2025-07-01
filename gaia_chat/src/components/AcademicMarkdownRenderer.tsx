'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';

interface AcademicMarkdownRendererProps {
  content: string;
  className?: string;
}

export const AcademicMarkdownRenderer: React.FC<AcademicMarkdownRendererProps> = ({ 
  content, 
  className = '' 
}) => {
  return (
    <div className={`prose prose-lg max-w-none academic-markdown ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkBreaks, remarkGfm]}
        components={{
          // 제목 스타일링 - 학술적 디자인
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-emerald-500">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8 pb-2 border-b border-emerald-300">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold text-gray-700 mb-3 mt-6">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-medium text-gray-700 mb-2 mt-4">
              {children}
            </h4>
          ),
          
          // 단락 스타일링
          p: ({ children }) => (
            <p className="mb-4 leading-relaxed text-gray-700 text-justify">
              {children}
            </p>
          ),
          
          // 리스트 스타일링
          ul: ({ children }) => (
            <ul className="mb-4 ml-6 space-y-2 list-disc marker:text-emerald-600">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-4 ml-6 space-y-2 list-decimal marker:text-emerald-600">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700 leading-relaxed">
              {children}
            </li>
          ),
          
          // 인용구 스타일링 - 학술 논문 스타일
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic my-6 bg-blue-50 py-3 px-4 rounded-r-lg">
              <div className="text-blue-900">
                {children}
              </div>
            </blockquote>
          ),
          
          // 코드 스타일링
          code: ({ inline, children, ...props }) => {
            if (inline) {
              return (
                <code className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded font-mono text-sm">
                  {children}
                </code>
              );
            }
            return (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4">
                <code className="font-mono text-sm" {...props}>
                  {children}
                </code>
              </pre>
            );
          },
          
          // 테이블 스타일링 - 학술 논문 테이블
          table: ({ children }) => (
            <div className="overflow-x-auto my-6">
              <table className="min-w-full border-collapse border border-gray-300">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-emerald-50 border-b-2 border-emerald-500">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-200">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-gray-50 transition-colors">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left font-semibold text-gray-800 border border-gray-300">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-gray-700 border border-gray-300">
              {children}
            </td>
          ),
          
          // 링크 스타일링 - 참고문헌 스타일
          a: ({ href, children }) => (
            <a 
              href={href} 
              className="text-blue-600 hover:text-blue-800 underline decoration-1 hover:decoration-2 transition-all"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          
          // 강조 스타일링
          strong: ({ children }) => (
            <strong className="font-bold text-gray-900">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700">
              {children}
            </em>
          ),
          
          // 수평선 스타일링
          hr: () => (
            <hr className="my-8 border-t-2 border-gray-300" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
      
      <style jsx global>{`
        .academic-markdown {
          font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* 학술 논문 스타일 추가 */
        .academic-markdown h1::before {
          content: '';
          display: inline-block;
          width: 5px;
          height: 100%;
          background: linear-gradient(to bottom, #10b981, #3b82f6);
          margin-right: 12px;
          vertical-align: middle;
        }
        
        .academic-markdown h2 {
          counter-increment: section;
        }
        
        .academic-markdown h2::before {
          content: counter(section) '. ';
          color: #10b981;
          font-weight: bold;
        }
        
        /* 표 캡션 스타일 */
        .academic-markdown table + p {
          text-align: center;
          font-style: italic;
          color: #6b7280;
          font-size: 0.875rem;
          margin-top: -1rem;
          margin-bottom: 2rem;
        }
        
        /* 그림 캡션 스타일 */
        .academic-markdown img + p {
          text-align: center;
          font-style: italic;
          color: #6b7280;
          font-size: 0.875rem;
          margin-top: 0.5rem;
          margin-bottom: 2rem;
        }
      `}</style>
    </div>
  );
};

export default AcademicMarkdownRenderer;