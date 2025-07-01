'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';
import matter from 'gray-matter';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ 
  content, 
  className = '' 
}) => {
  // 줄바꿈 전처리 함수
  const preprocessContent = (text: string): string => {
    // 1. 연속된 공백을 하나로 정리 (단, 코드 블록 제외)
    let processed = text.replace(/(?<!`.*) {2,}(?!.*`)/g, ' ');
    
    // 2. 제목 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2');
    processed = processed.replace(/(#{1,6}[^\n]+)\n([^\n#])/g, '$1\n\n$2');
    
    // 3. 리스트 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n([*+-]\s|[0-9]+\.\s)/g, '$1\n\n$2');
    processed = processed.replace(/([*+-][^\n]+|[0-9]+\.[^\n]+)\n([^\n*+-])/g, '$1\n\n$2');
    
    // 4. 코드 블록 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n(```)/g, '$1\n\n$2');
    processed = processed.replace(/(```[^\n]*)\n([^\n`])/g, '$1\n\n$2');
    
    // 5. 인용구 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n(>)/g, '$1\n\n$2');
    processed = processed.replace(/(>[^\n]+)\n([^>\n])/g, '$1\n\n$2');
    
    // 6. 표 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n(\|[^|\n]*\|)/g, '$1\n\n$2');
    processed = processed.replace(/(\|[^|\n]*\|)\n([^|\n])/g, '$1\n\n$2');
    
    // 7. 수평선 앞뒤에 빈 줄 확보
    processed = processed.replace(/([^\n])\n(---+|===+|\*\*\*+)/g, '$1\n\n$2');
    processed = processed.replace(/(---+|===+|\*\*\*+)\n([^\n])/g, '$1\n\n$2');
    
    // 8. 중요한 단락 구분을 위한 추가 처리
    processed = processed.replace(/([.!?:])\s*\n([A-Z가-힣])/g, '$1\n\n$2');
    
    return processed;
  };

  // gray-matter로 front matter와 content 분리
  const { data: frontMatter, content: rawContent } = matter(content);
  
  // 줄바꿈 전처리 적용
  const markdownContent = preprocessContent(rawContent);

  return (
    <div className={`prose prose-slate max-w-none prose-emerald korean-text ${className}`}
         style={{
           fontFamily: '"Pretendard", "Noto Sans KR", "Malgun Gothic", "맑은 고딕", system-ui, sans-serif',
           lineHeight: '1.7',
           wordBreak: 'break-word',
           overflowWrap: 'break-word',
           wordSpacing: '0.1em',
           letterSpacing: '0.02em'
         }}>
      {/* Front matter가 있는 경우 메타데이터 표시 */}
      {Object.keys(frontMatter).length > 0 && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">
            {Object.entries(frontMatter).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <span className="font-semibold capitalize">{key}:</span>
                <span>{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* 마크다운 콘텐츠 렌더링 */}
      <ReactMarkdown
        remarkPlugins={[remarkBreaks, remarkGfm]}
        components={{
          // 제목 스타일링
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-emerald-800 mb-4 pb-2 border-b border-emerald-200">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-emerald-700 mb-3 mt-6">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-emerald-600 mb-2 mt-4">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-base font-semibold text-emerald-600 mb-2 mt-3">
              {children}
            </h4>
          ),
          h5: ({ children }) => (
            <h5 className="text-sm font-semibold text-emerald-600 mb-1 mt-2">
              {children}
            </h5>
          ),
          h6: ({ children }) => (
            <h6 className="text-sm font-medium text-emerald-600 mb-1 mt-2">
              {children}
            </h6>
          ),
          
          // 단락 스타일링 - 줄바꿈 지원 강화
          p: ({ children }) => (
            <p className="mb-4 leading-relaxed text-gray-700 whitespace-pre-wrap break-words">
              {children}
            </p>
          ),
          
          // br 태그 지원 (remark-breaks로 생성된 줄바꿈)
          br: () => (
            <br className="leading-relaxed" />
          ),
          
          // 리스트 스타일링
          ul: ({ children }) => (
            <ul className="mb-4 ml-6 space-y-1 list-disc marker:text-emerald-500">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-4 ml-6 space-y-1 list-decimal marker:text-emerald-500">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700 leading-relaxed mb-1 break-words" 
                style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}>
              {children}
            </li>
          ),
          
          // 인용구 스타일링
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic my-4 bg-blue-50 py-2 rounded-r-lg">
              <div className="text-blue-800">
                {children}
              </div>
            </blockquote>
          ),
          
          // 코드 스타일링
          code: ({ inline, children, ...props }) => {
            if (inline) {
              return (
                <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono">
                  {children}
                </code>
              );
            }
            return (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
                <code {...props}>
                  {children}
                </code>
              </pre>
            );
          },
          
          // 테이블 스타일링
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-gray-300 rounded-lg">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-emerald-50">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-200">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-gray-50">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2 text-left font-semibold text-emerald-800 border-b border-emerald-200">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 text-gray-700 border-b border-gray-200">
              {children}
            </td>
          ),
          
          // 링크 스타일링
          a: ({ href, children }) => (
            <a 
              href={href} 
              className="text-blue-600 hover:text-blue-800 underline hover:no-underline transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          
          // 강조 스타일링 - 한국어 텍스트 최적화
          strong: ({ children }) => (
            <strong className="font-bold text-gray-900 break-words" 
                    style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700 break-words" 
                style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}>
              {children}
            </em>
          ),
          
          // 수평선 스타일링
          hr: () => (
            <hr className="my-6 border-t-2 border-gray-200" />
          ),
        }}
      >
        {markdownContent}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;