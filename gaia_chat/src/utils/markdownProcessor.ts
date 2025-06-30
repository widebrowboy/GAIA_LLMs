// 고급 마크다운 전처리 유틸리티 함수들

// 고급 마크다운 전처리 함수 - 컨텍스트 인식 처리
export const advancedMarkdownProcessor = (text: string): string => {
  const lines = text.split('\n');
  let inCodeBlock = false;
  let inListContext = false;
  
  return lines.map((line, index) => {
    // 코드 블록 감지
    if (line.startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      return line;
    }
    
    if (inCodeBlock) return line; // 코드 블록 내부는 건드리지 않음
    
    const trimmedLine = line.trim();
    const isListItem = /^\s*[*\-+]\s+/.test(line);
    const prevLine = index > 0 ? lines[index - 1].trim() : '';
    const nextLine = index < lines.length - 1 ? lines[index + 1].trim() : '';
    
    // 리스트 컨텍스트 추적
    if (isListItem) {
      inListContext = true;
    } else if (trimmedLine === '' && !nextLine.match(/^\s*[*\-+]\s+/)) {
      inListContext = false;
    }
    
    // * 기호 분석 및 처리
    if (trimmedLine.includes('*')) {
      // 리스트 아이템인 경우
      if (isListItem) {
        return handleListItem(line, nextLine);
      }
      
      // 강조 텍스트인 경우
      if (trimmedLine.match(/\*[^*]+\*/)) {
        return line + (nextLine ? '  ' : '');
      }
      
      // 볼드 텍스트인 경우  
      if (trimmedLine.match(/\*\*[^*]+\*\*/)) {
        return line + (nextLine ? '  ' : '');
      }
    }
    
    return handleRegularText(line, nextLine, inListContext);
  }).join('\n');
};

export const handleListItem = (line: string, nextLine: string): string => {
  const isNextListItem = /^\s*[*\-+]\s+/.test(nextLine);
  
  // 다음 줄도 리스트면 자연스러운 연결
  if (isNextListItem) return line;
  
  // 리스트 항목이 길면 줄바꿈 추가
  if (line.length > 80) return line + '  ';
  
  return line;
};

export const handleRegularText = (line: string, nextLine: string, inListContext: boolean): string => {
  if (!line.trim()) return line; // 빈 줄 유지
  
  // 리스트 컨텍스트에서는 자연스러운 흐름 유지
  if (inListContext && nextLine && !nextLine.match(/^\s*[*\-+]\s+/)) {
    return line + '  ';
  }
  
  // 일반 텍스트 처리
  if (nextLine && nextLine.trim()) {
    return line + '  ';
  }
  
  return line;
};

// 다중 줄바꿈 지원
export const handleMultipleLineBreaks = (content: string): string => {
  // \n\n을 강제 줄바꿈으로 변환
  return content.replace(/\n\n/g, '\n &nbsp;\n &nbsp;\n');
};

// 통합 전처리 함수
export const processMarkdownText = (text: string): string => {
  let processed = advancedMarkdownProcessor(text);
  processed = handleMultipleLineBreaks(processed);
  return processed;
};