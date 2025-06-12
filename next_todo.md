@https://github.com/gosset-ai/mcps 에서 pubmed-mcp와 clinicaltrials-mcp를 챗봇 mcp에 추가 하고 다른 mcp와 연동하고 deep research에 통합해줘 "Method not implemented: tools/call" 오류가 발생하지 않게 수정해줘 관련된 모든 문서들도 해당 기능을 추가해줘. mcp 서버들을 통해 얻은 결과들의 중복이 정도들을 제외하여 중복된 것 중에 가장 높은 정도의 결과만 반환하도록 수정해줘 







@https://github.com/genomoncology/biomcp 의 github에서 biomcp의 variant_searcher와 variant_details를 챗봇 mcp에 추가 하고 다른 mcp와 연동하고 deep research에 통합해줘. variant-mcp 이름으로 mcp 서버를 추가하고 variant_searcher와 variant_details를 검색이 가능하도록 해줘. "Method not implemented: tools/call" 오류가 발생하지 않게 수정해줘 관련된 모든 문서들도 해당 기능을 추가해줘. variant_searcher와 variant_details은 다음과 같음. variant_searcher: Search for genetic variants with sophisticated filtering,variant_details: Comprehensive annotations from multiple sources (CIViC, ClinVar, COSMIC, dbSNP, etc.). 커맨드 라인 인터페이스는 다음과 같이 작동하도록 수정해줘 variant-mcp search --gene TP53 --significance pathogenic, variant-mcp get rs113488022 








MyVariant.info 
variant_searcher: Search for genetic variants with sophisticated filtering
variant_details: Comprehensive annotations from multiple sources (CIViC, ClinVar, COSMIC, dbSNP, etc.)


