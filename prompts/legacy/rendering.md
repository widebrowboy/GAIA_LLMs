# Next.js에서 신장암 임상시험 의료 문서를 자연스럽게 렌더링하는 완전한 가이드

## 핵심 접근법: 데이터 구조화와 자연스러운 문장 처리

이전 대화에서 제공받은 신장암 임상시험 데이터를 Next.js에서 **의료 문서답게 전문적이면서도 읽기 쉽게 렌더링**하는 방법을 제안합니다[1][2][3].

## 1. 의료 데이터 구조화 전략

### 임상시험 데이터 모델링

```javascript
// lib/clinicalTrialsData.js
export const clinicalTrialsData = {
  lastUpdated: "2024년 5월 15일",
  disclaimer: {
    warning: "임상 정보는 빠르게 변화하므로, 아래 정보는 참고용이며 최신 정보는 ClinicalTrials.gov 또는 관련 기관 웹사이트에서 확인하시기 바랍니다.",
    caution: "복합 처방은 여러 약물의 조합이므로, 각 약물에 대한 부작용 및 주의사항을 반드시 확인해야 합니다."
  },
  trials: [
    {
      id: "pembrolizumab-axitinib-2023",
      title: "Pembrolizumab과 Axitinib 복합 요법 임상시험",
      subtitle: "A Study of Pembrolizumab in Combination With Axitinib in Patients With Advanced Renal Cell Carcinoma (Zoster)",
      status: "모집 중",
      startDate: "2023년 2월 16일",
      country: "미국",
      phase: "Phase 2",
      compounds: [
        {
          name: "Pembrolizumab",
          koreanName: "키트루다",
          category: "면역관문억제제"
        },
        {
          name: "Axitinib", 
          koreanName: "아프리바",
          category: "혈관신생억제제"
        }
      ],
      description: "진행성 신세포암종 환자를 대상으로 Pembrolizumab과 Axitinib 병용 요법의 안전성과 효과를 평가하는 임상연구입니다.",
      year: 2023
    },
    {
      id: "cabozantinib-nivolumab-2020",
      title: "Cabozantinib과 Nivolumab 복합 요법 임상시험",
      subtitle: "Phase 2 Study of Cabozantinib in Combination With Nivolumab in Patients With Advanced Renal Cell Carcinoma (COSMIC-003)",
      status: "진행 중, 모집 완료",
      startDate: "2020년 3월 23일",
      country: "다국가",
      phase: "Phase 2",
      compounds: [
        {
          name: "Cabozantinib",
          koreanName: "카보메틱",
          category: "혈관신생억제제 및 티로신 키나아제억제제"
        },
        {
          name: "Nivolumab",
          koreanName: "옵디비오", 
          category: "면역관문억제제"
        }
      ],
      description: "진행성 신세포암종 환자를 대상으로 Cabozantinib과 Nivolumab 병용 요법의 효과를 평가하는 2상 임상연구입니다.",
      year: 2020
    }
  ],
  drugInformation: {
    "Pembrolizumab": {
      koreanName: "키트루다",
      category: "면역관문억제제",
      mechanism: "PD-1 단백질을 억제하여 면역 세포의 활성을 증가시킵니다",
      indications: ["진행성 신세포암종", "흑색종", "폐암"],
      commonSideEffects: ["피로", "설사", "발진", "자가면역 반응"]
    },
    "Axitinib": {
      koreanName: "아프리바", 
      category: "혈관신생억제제",
      mechanism: "VEGF 수용체를 억제하여 암 혈관 형성을 억제합니다",
      indications: ["진행성 신세포암종"],
      commonSideEffects: ["고혈압", "설사", "피로", "체중 감소"]
    },
    // ... 다른 약물들
  }
};
```

## 2. 자연스러운 문장 렌더링 컴포넌트

### 메인 의료 문서 컴포넌트

```javascript
// components/MedicalDocumentRenderer.js
import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { convertToNaturalMarkdown } from '../lib/markdownConverter';

export default function MedicalDocumentRenderer({ data, className }) {
  const naturalMarkdown = useMemo(() => {
    return convertToNaturalMarkdown(data);
  }, [data]);

  return (
    <article className={`medical-document ${className || ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          h1: ({ children }) => (
            <h1 className="document-main-title">
              <span className="title-icon">🏥</span>
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="section-title">
              <span className="section-number">
                {getSectionNumber(children)}
              </span>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="subsection-title">
              <span className="subsection-icon">📋</span>
              {children}
            </h3>
          ),
          blockquote: ({ children }) => (
            <div className="medical-alert">
              <div className="alert-icon">⚠️</div>
              <div className="alert-content">{children}</div>
            </div>
          ),
          ul: ({ children }) => (
            <ul className="medical-list">{children}</ul>
          ),
          li: ({ children }) => (
            <li className="medical-list-item">
              <span className="list-marker">💊</span>
              <span className="list-content">{children}</span>
            </li>
          ),
          p: ({ children }) => (
            <p className="medical-paragraph">{children}</p>
          ),
          strong: ({ children }) => (
            <strong className="medical-emphasis">{children}</strong>
          ),
          a: ({ href, children }) => (
            <a 
              href={href} 
              className="medical-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children} 
              <span className="external-link-icon">🔗</span>
            </a>
          )
        }}
      >
        {naturalMarkdown}
      </ReactMarkdown>
    </article>
  );
}
```

### 자연스러운 마크다운 변환 함수

```javascript
// lib/markdownConverter.js
export function convertToNaturalMarkdown(data) {
  const { trials, drugInformation, disclaimer, lastUpdated } = data;
  
  let markdown = `# 신세포암종(RCC) 복합 처방 임상연구 현황

> **📅 정보 기준일:** ${lastUpdated}

> **⚠️ 중요한 안내사항**  
> ${disclaimer.warning}  
> 
> ${disclaimer.caution}

---

## 📊 최신 임상연구 동향

현재 신세포암종 치료 분야에서는 **면역관문억제제와 표적치료제의 복합 요법**이 주목받고 있습니다. 최근 등록된 주요 임상시험들을 시기순으로 정리하면 다음과 같습니다.

`;

  // 시험들을 연도 역순으로 정렬
  const sortedTrials = trials.sort((a, b) => b.year - a.year);

  sortedTrials.forEach((trial, index) => {
    const statusEmoji = getStatusEmoji(trial.status);
    const phaseColor = getPhaseColor(trial.phase);
    
    markdown += `
## ${index + 1}. ${trial.title}

### 🔬 임상시험 개요

**공식 명칭:** ${trial.subtitle}

**현재 상태:** ${statusEmoji} ${trial.status}  
**시작일:** ${trial.startDate}  
**진행 국가:** ${trial.country}  
**임상 단계:** <span class="phase-badge ${phaseColor}">${trial.phase}</span>

### 💊 복합 처방 구성

이번 임상시험에서는 다음과 같은 약물들의 복합 요법을 평가합니다:

${trial.compounds.map(compound => `
**${compound.name} (${compound.koreanName})**
- 분류: ${compound.category}
- 작용기전: ${drugInformation[compound.name]?.mechanism || '정보 준비 중'}
- 적응증: ${drugInformation[compound.name]?.indications?.join(', ') || '정보 준비 중'}
`).join('\n')}

### 📈 연구 목적 및 의미

${trial.description}

이 연구는 ${trial.compounds.length}가지 약물의 시너지 효과를 통해 기존 단일 요법의 한계를 극복하고자 하는 중요한 시도입니다.

---
`;
  });

  markdown += `
## 💊 주요 치료제 상세 정보

신세포암종 복합 처방에 사용되는 주요 약물들의 특성을 살펴보겠습니다.

`;

  Object.entries(drugInformation).forEach(([drugName, info]) => {
    markdown += `
### ${drugName} (${info.koreanName})

**분류:** ${info.category}  
**작용기전:** ${info.mechanism}

**적응증**
${info.indications.map(indication => `- ${indication}`).join('\n')}

**주요 부작용**
${info.commonSideEffects.map(effect => `- ${effect}`).join('\n')}

`;
  });

  markdown += `
## 📚 추가 정보 및 참고 자료

### 🔍 최신 정보 확인처

더 자세하고 최신의 임상시험 정보는 다음 공식 사이트에서 확인하실 수 있습니다:

- **ClinicalTrials.gov** - 전 세계 임상시험 정보 데이터베이스
- **FDA (미국 식품의약국)** - 신장암 치료제 승인 정보
- **EMA (유럽 의약품청)** - 유럽 지역 치료제 정보

### ⚖️ 면책 조항

본 정보는 일반적인 정보 제공 목적으로만 제공되며 **의학적 조언으로 간주되어서는 안 됩니다**. 신장암 치료와 관련된 모든 결정은 **자격을 갖춘 의료 전문가와 상담하여** 내려야 합니다.

환자 개개인의 상태, 병력, 현재 복용 중인 약물 등을 종합적으로 고려한 맞춤형 치료 계획이 필요하며, 이는 반드시 전문의의 진료를 통해 결정되어야 합니다.
`;

  return markdown;
}

// 유틸리티 함수들
function getStatusEmoji(status) {
  const statusMap = {
    '모집 중': '🟢',
    '진행 중, 모집 완료': '🟡',
    '완료': '✅',
    '중단': '🔴'
  };
  return statusMap[status] || '📋';
}

function getPhaseColor(phase) {
  const phaseColorMap = {
    'Phase 1': 'phase-1',
    'Phase 2': 'phase-2', 
    'Phase 3': 'phase-3',
    'Phase 4': 'phase-4'
  };
  return phaseColorMap[phase] || 'phase-default';
}

function getSectionNumber(children) {
  // children에서 숫자 추출
  const text = children.toString();
  const match = text.match(/^(\d+)\./);
  return match ? match[1] : '';
}
```

## 3. 의료 문서 전용 스타일링[4][5]

```css
/* styles/medical-document.css */
.medical-document {
  max-width: 1000px;
  margin: 0 auto;
  padding: 3rem 2rem;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.7;
  color: #2c3e50;
  background: linear-gradient(135deg, #f8fffe 0%, #f1f8ff 100%);
}

/* 메인 타이틀 */
.document-main-title {
  color: #1a365d;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-align: center;
  border-bottom: 3px solid #3182ce;
  padding-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title-icon {
  font-size: 3rem;
  color: #e53e3e;
}

/* 섹션 타이틀 */
.section-title {
  color: #2d3748;
  font-size: 1.8rem;
  font-weight: 600;
  margin: 3rem 0 1.5rem 0;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
  border-radius: 12px;
  border-left: 6px solid #4299e1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.section-number {
  background: #4299e1;
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
}

/* 서브섹션 타이틀 */
.subsection-title {
  color: #4a5568;
  font-size: 1.4rem;
  font-weight: 600;
  margin: 2rem 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subsection-icon {
  font-size: 1.2rem;
}

/* 의료 경고 박스 */
.medical-alert {
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  border: 2px solid #fc8181;
  border-radius: 16px;
  padding: 2rem;
  margin: 2rem 0;
  display: flex;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(252, 129, 129, 0.15);
}

.alert-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-content p {
  margin: 0.5rem 0;
  font-weight: 500;
  line-height: 1.6;
}

/* 의료 리스트 */
.medical-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
}

.medical-list-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  margin: 0.5rem 0;
  background: #ffffff;
  border-radius: 8px;
  border-left: 4px solid #48bb78;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.medical-list-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.list-marker {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.list-content {
  flex: 1;
}

/* 문단 스타일 */
.medical-paragraph {
  margin: 1.5rem 0;
  line-height: 1.8;
  text-align: justify;
  color: #2d3748;
}

/* 강조 텍스트 */
.medical-emphasis {
  color: #2b6cb0;
  font-weight: 600;
  background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

/* 링크 스타일 */
.medical-link {
  color: #3182ce;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.2s ease;
}

.medical-link:hover {
  color: #2c5282;
  text-decoration: underline;
}

.external-link-icon {
  font-size: 0.9rem;
}

/* 임상 단계 배지 */
.phase-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.phase-1 { background: #fed7d7; color: #c53030; }
.phase-2 { background: #feebc8; color: #dd6b20; }
.phase-3 { background: #d4edda; color: #38a169; }
.phase-4 { background: #bee3f8; color: #3182ce; }

/* 반응형 디자인 */
@media (max-width: 768px) {
  .medical-document {
    padding: 2rem 1rem;
  }
  
  .document-main-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .section-title {
    font-size: 1.5rem;
    padding: 1rem;
  }
  
  .medical-alert {
    flex-direction: column;
    padding: 1.5rem;
  }
}

/* 인쇄 최적화 */
@media print {
  .medical-document {
    background: white;
    padding: 1rem;
  }
  
  .medical-alert {
    border: 2px solid #666;
    background: white;
  }
  
  .medical-link {
    color: #000;
    text-decoration: underline;
  }
  
  .external-link-icon {
    display: none;
  }
}
```

## 4. Next.js 페이지 구현[6][7]

```javascript
// pages/clinical-trials.js 또는 app/clinical-trials/page.js
import Head from 'next/head';
import { useState, useMemo } from 'react';
import MedicalDocumentRenderer from '../components/MedicalDocumentRenderer';
import { clinicalTrialsData } from '../lib/clinicalTrialsData';

export default function ClinicalTrialsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const filteredData = useMemo(() => {
    let filteredTrials = clinicalTrialsData.trials;

    if (searchTerm) {
      filteredTrials = filteredTrials.filter(trial =>
        trial.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        trial.compounds.some(compound => 
          compound.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          compound.koreanName.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    if (selectedStatus !== 'all') {
      filteredTrials = filteredTrials.filter(trial => 
        trial.status === selectedStatus
      );
    }

    return {
      ...clinicalTrialsData,
      trials: filteredTrials
    };
  }, [searchTerm, selectedStatus]);

  return (
    <>
      <Head>
        <title>신세포암종 복합 처방 임상연구 현황 | 의료 정보 포털</title>
        <meta name="description" content="최신 신세포암종 복합 처방 임상시험 정보와 치료제 데이터를 제공합니다." />
        <meta name="keywords" content="신세포암종, RCC, 임상시험, 복합 처방, 면역관문억제제" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        {/* 검색 및 필터 컨트롤 */}
        <div className="container mx-auto p-4">
          <div className="flex flex-col md:flex-row gap-4 mb-6 p-4 bg-white rounded-lg shadow-md">
            <div className="flex-1">
              <input
                type="text"
                placeholder="임상시험명 또는 약물명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="md:w-48">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">모든 상태</option>
                <option value="모집 중">모집 중</option>
                <option value="진행 중, 모집 완료">진행 중</option>
                <option value="완료">완료</option>
              </select>
            </div>
          </div>
        </div>

        {/* 메인 문서 렌더링 */}
        <MedicalDocumentRenderer 
          data={filteredData} 
          className="clinical-trials-document"
        />
      </main>
    </>
  );
}
```

## 5. 추가 기능: 실시간 업데이트와 접근성

### 자동 업데이트 기능

```javascript
// hooks/useClinicalTrialsData.js
import { useState, useEffect } from 'react';

export function useClinicalTrialsData() {
  const [data, setData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 실제 환경에서는 API 호출
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // const response = await fetch('/api/clinical-trials');
        // const freshData = await response.json();
        
        // 현재는 정적 데이터 사용
        const { clinicalTrialsData } = await import('../lib/clinicalTrialsData');
        setData(clinicalTrialsData);
        setLastUpdate(new Date().toLocaleString('ko-KR'));
      } catch (error) {
        console.error('데이터 로딩 실패:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, lastUpdate, isLoading };
}
```

이 방법론을 통해 **의료 전문성을 유지하면서도 일반인이 이해하기 쉬운 자연스러운 문서**로 렌더링할 수 있습니다[8][9]. 특히 **아이콘과 색상 코딩을 통한 시각적 구분**[10][11], **단계적 정보 제공**[4], 그리고 **반응형 디자인**[12][13]으로 다양한 환경에서 최적의 읽기 경험을 제공합니다.

출처
[1] Markdown and MDX - Next.js 한글 문서 번역 (커뮤니티) https://nextjs-ko.org/docs/pages/building-your-application/configuring/mdx
[2] [NextJS] 마크다운으로 글 작성하는 방법 - growd - 티스토리 https://growd.tistory.com/78
[3] Next.js에서 MDX를 활용한 고급 마크다운 및 JSX 통합 https://reactnext-central.xyz/blog/nextjs/mdx
[4] 타이포그래피(Typography) | 스타일 가이드 - KRDS https://www.krds.go.kr/html/site/style/style_03.html
[5] 세종병원 전용서체 - 인천세종병원 https://incheon.sejongh.co.kr/my_information/user_content?cate1=178&cate2=299&cate3_idx=304&html_mode=html&Depth=3
[6] [NextJs] Markdown 포스팅을 정적 페이지(SSG)로 배포하기 https://stirringdev.tistory.com/98
[7] [Next.js] 마크다운 종합편 - DogKaeBi 독깨비 https://www.dogkaebi.com/blog/blog-development-post-use-markdown
[8] React 컴포넌트 상태 관리와 데이터 동기화 문제 해결하기 - F-Lab https://f-lab.kr/insight/react-state-management-20250128
[9] 미래 임상연구는 환자 전 생애 데이터 수집‧관리 - 청년의사 http://www.docdocdoc.co.kr/news/articleView.html?idxno=3017896
[10] Next.js를 배워보자 2_(next.js에서 icon 사용법) - young01 - 티스토리 https://s-young01.tistory.com/71
[11] [Next.js] Next.js/React 에 Font Awesome Icon 적용하기/ 아이콘 추가 ... https://31daylee.tistory.com/entry/nextjs-NextjsReact-%EC%97%90-Font-Awesome-Icon-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0-%EC%95%84%EC%9D%B4%EC%BD%98-%EC%B6%94%EA%B0%80%ED%95%98%EB%8A%94-%EB%B2%95
[12] React 환경에서 Markdown 출력하기 (react-markdown) https://jayprogram.tistory.com/99
[13] React - Markdown & Code Block & Block Quote 적용 - 우주먼지 https://iizz.tistory.com/438
[14] React.js의 렌더링 방식 살펴보기 - 이정환 | 2023 NE(O ... - YouTube https://www.youtube.com/watch?v=N7qlk_GQRJU
[15] [React Document] 조건부 렌더링 - YundleYundle - 티스토리 https://zzdd1558.tistory.com/284
[16] Next.js 블로그 만들기 - (1) React-Markdown - velog https://velog.io/@again7536/Next.js-%EB%B8%94%EB%A1%9C%EA%B7%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0-1
[17] [리액트] 마크다운 문서에서 HTML 랜더링하기(rehype-raw, next-intl) https://all-dev-kang.tistory.com/entry/%EB%A6%AC%EC%95%A1%ED%8A%B8-%EB%A7%88%ED%81%AC%EB%8B%A4%EC%9A%B4-%EB%AC%B8%EC%84%9C%EC%97%90%EC%84%9C-HTML-%EB%9E%9C%EB%8D%94%EB%A7%81%ED%95%98%EA%B8%B0rehype-raw-next-intl
[18] [논문 리뷰] AUTOCT: Automating Interpretable Clinical Trial ... https://www.themoonlight.io/ko/review/autoct-automating-interpretable-clinical-trial-prediction-with-llm-agents
[19] Next.js markdown 적용하기 https://sonblog.vercel.app/projects/nextjs-blog/nextjs-markdown
[20] nextjs emoji 사용법 - 코딩애플 온라인 강좌 https://codingapple.com/forums/topic/nextjs-emoji-%EC%82%AC%EC%9A%A9%EB%B2%95/
[21] Contentlayer란? next.js 13에서 활용하기 - velog https://velog.io/@boyeon_jeong/Nest.js-getStaticPaths
[22] React 렌더링 2번씩 발생하는 이유 - velog https://velog.io/@gusrud13579/React-%EB%A0%8C%EB%8D%94%EB%A7%81-2%EB%B2%88%EC%94%A9-%EB%B0%9C%EC%83%9D%ED%95%98%EB%8A%94-%EC%9D%B4%EC%9C%A0
[23] Next.js로 마크다운 블로그를 만들어보자 - Cloud-Vanila-Blog https://www.cloud-sanghun.com/content?id=2022-10-23-make-md-blog-withnext&type=post-dev
[24] Next.js로 마크다운 블로그 만들기 - velog https://velog.io/@s2s2hyun/Next.js%EB%A1%9C-%EB%A7%88%ED%81%AC%EB%8B%A4%EC%9A%B4-%EB%B8%94%EB%A1%9C%EA%B7%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0
[25] Next.js 완벽 마스터 (v15): Notion 기반 개발자 블로그 만들기 ... - 인프런 https://www.inflearn.com/course/next-%EC%99%84%EB%B2%BD%EB%A7%88%EC%8A%A4%ED%84%B0-notion-%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%B8%94%EB%A1%9C%EA%B7%B8-cursorai
[26] Next.js로 마크다운 블로그 만들기 - velog https://velog.io/@ctdlog/Next.js%EB%A1%9C-%EB%A7%88%ED%81%AC%EB%8B%A4%EC%9A%B4-%EB%B8%94%EB%A1%9C%EA%B7%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0
[27] 실무에서 쓰는 진짜 타이포그래피! (편집디자인) - YouTube https://www.youtube.com/watch?v=dTgkRCbXH_s
[28] React-markdown 적용시켜보기 - velog https://velog.io/@jswing5267/Velog-%ED%81%B4%EB%A1%A0%EC%BD%94%EB%94%A9%ED%95%98%EA%B8%B0-1-React-markdown-%EC%A0%81%EC%9A%A9%EC%8B%9C%EC%BC%9C%EB%B3%B4%EA%B8%B0
