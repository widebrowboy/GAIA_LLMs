// 고급 마크다운 전처리 유틸리티 함수들

// 고급 마크다운 전처리 함수 - * 패턴 기반 줄바꿈 처리 강화
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
    
    // * 패턴 기반 강화된 줄바꿈 처리
    if (trimmedLine.includes('*')) {
      // 리스트 아이템인 경우 - 항상 앞뒤 줄바꿈 보장
      if (isListItem) {
        return handleListItemWithLineBreaks(line, prevLine, nextLine);
      }
      
      // 강조 텍스트인 경우 - 독립적인 줄로 처리
      if (trimmedLine.match(/\*[^*]+\*/)) {
        return ensureLineBreaksAround(line, prevLine, nextLine);
      }
      
      // 볼드 텍스트인 경우 - 독립적인 줄로 처리
      if (trimmedLine.match(/\*\*[^*]+\*\*/)) {
        return ensureLineBreaksAround(line, prevLine, nextLine);
      }
      
      // 단순 * 기호 구분자인 경우
      if (trimmedLine.match(/^\s*\*+\s*$/)) {
        return '\n' + line + '\n';
      }
    }
    
    return handleRegularText(line, nextLine, inListContext);
  }).join('\n');
};

// * 패턴 기반 리스트 아이템 줄바꿈 처리 (강화)
export const handleListItemWithLineBreaks = (line: string, prevLine: string, nextLine: string): string => {
  const isNextListItem = /^\s*[*\-+]\s+/.test(nextLine);
  const isPrevListItem = /^\s*[*\-+]\s+/.test(prevLine);
  
  // 리스트 시작 부분 - 앞에 빈 줄 추가
  if (!isPrevListItem && prevLine !== '') {
    line = '\n' + line;
  }
  
  // 리스트 끝 부분 - 뒤에 빈 줄 추가  
  if (!isNextListItem && nextLine !== '') {
    line = line + '\n';
  }
  
  return line;
};

// 기존 handleListItem 함수 (호환성 유지)
export const handleListItem = (line: string, nextLine: string): string => {
  const isNextListItem = /^\s*[*\-+]\s+/.test(nextLine);
  
  // 다음 줄도 리스트면 자연스러운 연결
  if (isNextListItem) return line;
  
  // 리스트 항목이 길면 줄바꿈 추가
  if (line.length > 80) return line + '  ';
  
  return line;
};

// 텍스트 앞뒤 줄바꿈 보장 함수
export const ensureLineBreaksAround = (line: string, prevLine: string, nextLine: string): string => {
  let result = line;
  
  // 앞줄이 비어있지 않고 현재 줄과 다른 내용이면 앞에 줄바꿈 추가
  if (prevLine && prevLine !== line.trim()) {
    result = '\n' + result;
  }
  
  // 뒷줄이 비어있지 않고 현재 줄과 다른 내용이면 뒤에 줄바꿈 추가
  if (nextLine && nextLine !== line.trim()) {
    result = result + '\n';
  }
  
  return result;
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