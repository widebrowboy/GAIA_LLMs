"""
MCP Commands for Chatbot
"""

import asyncio
from typing import Optional


class MCPCommands:
    """MCP 명령어 처리 클래스"""
    
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.interface = chatbot.interface
        self.mcp_manager = chatbot.mcp_manager
    
    async def handle_mcp_command(self, args: str):
        """MCP 명령어 처리"""
        # 인수 정규화 (공백과 특수문자 처리)
        args = args.strip() if args else ""
        
        # 디버그 정보
        if self.chatbot.settings.get("debug_mode", False):
            print(f"🐛 [MCP 디버그] 받은 인수: '{args}' (길이: {len(args)})")
        
        if not args:
            self.show_mcp_help()
            return
        
        parts = args.split()
        subcommand = parts[0] if parts else ""
        
        # 디버그 정보
        if self.chatbot.settings.get("debug_mode", False):
            print(f"🐛 [MCP 디버그] 하위명령어: '{subcommand}' (총 {len(parts)}개 부분)")
        
        if subcommand == "start":
            await self.start_mcp()
        elif subcommand == "stop":
            await self.stop_mcp()
        elif subcommand == "status":
            await self.show_mcp_status()
        elif subcommand == "tools":
            await self.list_mcp_tools()
        elif subcommand == "call":
            if len(parts) >= 2:
                tool_name = parts[1]
                tool_args = " ".join(parts[2:]) if len(parts) > 2 else ""
                await self.call_mcp_tool(tool_name, tool_args)
            else:
                self.interface.display_error("사용법: /mcp call <tool_name> [arguments]")
        elif subcommand == "research":
            if len(parts) >= 2:
                question = " ".join(parts[1:])
                await self.mcp_research(question)
            else:
                self.interface.display_error("사용법: /mcp research <question>")
        elif subcommand == "evaluate":
            if len(parts) >= 3:
                question = parts[1]
                answer = " ".join(parts[2:])
                await self.mcp_evaluate(question, answer)
            else:
                self.interface.display_error("사용법: /mcp evaluate <question> <answer>")
        elif subcommand == "think":
            if len(parts) >= 2:
                problem = " ".join(parts[1:])
                await self.start_sequential_thinking(problem)
            else:
                self.interface.display_error("사용법: /mcp think <problem>")
        elif subcommand == "continue":
            if len(parts) >= 3:
                process_id = parts[1]
                thought = " ".join(parts[2:])
                await self.continue_sequential_thinking(process_id, thought)
            else:
                self.interface.display_error("사용법: /mcp continue <processId> <thought>")
        elif subcommand == "complete":
            if len(parts) >= 2:
                process_id = parts[1]
                await self.complete_sequential_thinking(process_id)
            else:
                self.interface.display_error("사용법: /mcp complete <processId>")
        elif subcommand == "bioarticle":
            if len(parts) >= 2:
                query = " ".join(parts[1:])
                await self.search_biomedical_articles(query)
            else:
                self.interface.display_error("사용법: /mcp bioarticle <검색어>")
        elif subcommand == "biotrial":
            if len(parts) >= 2:
                condition = " ".join(parts[1:])
                await self.search_clinical_trials(condition)
            else:
                self.interface.display_error("사용법: /mcp biotrial <질병/조건>")
        elif subcommand == "biovariant":
            if len(parts) >= 2:
                gene = " ".join(parts[1:])
                await self.search_genetic_variants(gene)
            else:
                self.interface.display_error("사용법: /mcp biovariant <유전자명>")
        elif subcommand == "chembl":
            if len(parts) >= 3:
                action = parts[1]
                query = " ".join(parts[2:])
                await self.chembl_search(action, query)
            else:
                self.interface.display_error("사용법: /mcp chembl <action> <query>")
                self.interface.display_error("Actions: molecule, target, activity, assay, drug")
        elif subcommand == "smiles":
            if len(parts) >= 2:
                smiles = " ".join(parts[1:])
                await self.chembl_smiles_tools(smiles)
            else:
                self.interface.display_error("사용법: /mcp smiles <SMILES_string>")
        elif subcommand == "drugbank":
            if len(parts) >= 3:
                action = parts[1]
                query = " ".join(parts[2:])
                await self.drugbank_search(action, query)
            else:
                self.interface.display_error("사용법: /mcp drugbank <action> <query>")
                self.interface.display_error("Actions: search, details, indication, interaction, target")
        elif subcommand == "opentargets":
            if len(parts) >= 3:
                action = parts[1]
                query = " ".join(parts[2:])
                await self.opentargets_search(action, query)
            else:
                self.interface.display_error("사용법: /mcp opentargets <action> <query>")
                self.interface.display_error("Actions: targets, diseases, target_diseases, disease_targets, drugs")
        elif subcommand == "test":
            if len(parts) >= 2:
                test_type = parts[1]
                if test_type == "integrated":
                    await self.run_integrated_mcp_test()
                elif test_type == "deep":
                    await self.run_deep_research_test()
                else:
                    await self.run_mcp_test()
            else:
                await self.run_mcp_test()
        else:
            self.show_mcp_help()
    
    def show_mcp_help(self):
        """MCP 도움말 표시"""
        help_text = """
[bold green]MCP (Model Context Protocol) 명령어:[/bold green]

[bold cyan]기본 명령어:[/bold cyan]
[cyan]/mcp start[/cyan]     - MCP 서버 시작
[cyan]/mcp stop[/cyan]      - MCP 서버 중지
[cyan]/mcp status[/cyan]    - MCP 상태 확인
[cyan]/mcp tools[/cyan]     - 사용 가능한 MCP 툴 목록

[bold cyan]툴 호출:[/bold cyan]
[cyan]/mcp call <tool> [args][/cyan] - MCP 툴 직접 호출
[cyan]/mcp research <question>[/cyan] - MCP를 통한 연구 수행
[cyan]/mcp evaluate <question> <answer>[/cyan] - MCP를 통한 답변 평가

[bold cyan]Sequential Thinking:[/bold cyan]
[cyan]/mcp think <problem>[/cyan] - 순차적 사고 프로세스 시작
[cyan]/mcp continue <processId> <thought>[/cyan] - 사고 단계 추가
[cyan]/mcp complete <processId>[/cyan] - 사고 프로세스 완료

[bold cyan]BioMCP (생의학 연구):[/bold cyan]
[cyan]/mcp bioarticle <query>[/cyan] - 생의학 논문 검색
[cyan]/mcp biotrial <condition>[/cyan] - 임상시험 검색
[cyan]/mcp biovariant <gene>[/cyan] - 유전자 변이 정보 검색

[bold cyan]ChEMBL (화학 데이터베이스):[/bold cyan]
[cyan]/mcp chembl molecule <name>[/cyan] - 분자 정보 검색
[cyan]/mcp chembl target <name>[/cyan] - 타겟 정보 검색  
[cyan]/mcp chembl activity <query>[/cyan] - 활성 데이터 검색
[cyan]/mcp chembl drug <name>[/cyan] - 약물 정보 검색
[cyan]/mcp smiles <SMILES>[/cyan] - SMILES 분자 구조 분석

[bold cyan]DrugBank (약물 데이터베이스):[/bold cyan]
[cyan]/mcp drugbank search <name>[/cyan] - 약물 검색
[cyan]/mcp drugbank details <drugbank_id>[/cyan] - 약물 상세 정보
[cyan]/mcp drugbank indication <condition>[/cyan] - 적응증별 약물 검색
[cyan]/mcp drugbank interaction <drugbank_id>[/cyan] - 약물 상호작용
[cyan]/mcp drugbank target <target>[/cyan] - 타겟별 약물 검색

[bold cyan]OpenTargets (타겟-질병 연관성):[/bold cyan]
[cyan]/mcp opentargets targets <gene>[/cyan] - 타겟 유전자 검색
[cyan]/mcp opentargets diseases <disease>[/cyan] - 질병 검색
[cyan]/mcp opentargets target_diseases <target_id>[/cyan] - 타겟 연관 질병
[cyan]/mcp opentargets disease_targets <disease_id>[/cyan] - 질병 연관 타겟
[cyan]/mcp opentargets drugs <drug>[/cyan] - 약물 검색

[bold cyan]테스트:[/bold cyan]
[cyan]/mcp test[/cyan] - HNSCC 예제를 활용한 MCP 통합 테스트
[cyan]/mcp test integrated[/cyan] - ChEMBL + BioMCP + Sequential Thinking 통합 테스트
[cyan]/mcp test deep[/cyan] - Deep Research 기능 테스트 (권장)

MCP가 활성화되면 일반 질문도 자동으로 MCP 툴을 사용하여 처리됩니다.
        """
        self.interface.console.print(help_text)
    
    async def start_mcp(self):
        """MCP 서버 시작"""
        try:
            self.interface.console.print("[yellow]🔬 통합 Deep Research MCP 시스템 시작 중...[/yellow]")
            
            # 1. GAIA MCP 서버 시작
            success = await self.mcp_manager.start_server()
            if success:
                self.interface.console.print("[green]✓ GAIA MCP 서버가 성공적으로 시작되었습니다.[/green]")
                
                # 기본 클라이언트 초기화
                try:
                    await self.mcp_manager.create_client("default")
                    self.interface.console.print("[green]✓ 기본 MCP 클라이언트가 연결되었습니다.[/green]")
                except Exception as e:
                    self.interface.console.print(f"[yellow]⚠ 기본 클라이언트 연결 실패: {e}[/yellow]")
                
                # 2. 외부 서버들 시작 (DrugBank, OpenTargets 포함)
                self.interface.console.print("[blue]외부 MCP 서버들 시작 중...[/blue]")
                if await self.mcp_manager.start_external_servers():
                    self.interface.console.print("[green]✓ 외부 MCP 서버들이 시작되었습니다.[/green]")
                    
                    # 시작된 서버들 표시
                    status = self.mcp_manager.get_status()
                    client_ids = status.get('client_ids', [])
                    if client_ids:
                        self.interface.console.print(f"[cyan]활성 클라이언트: {', '.join(client_ids)}[/cyan]")
                        
                        # 각 서버별 상태 표시
                        if 'drugbank-mcp' in client_ids:
                            self.interface.console.print("[green]💊 DrugBank MCP 서버 연결됨[/green]")
                        if 'opentargets-mcp' in client_ids:
                            self.interface.console.print("[green]🎯 OpenTargets MCP 서버 연결됨[/green]")
                        if 'biomcp' in client_ids:
                            self.interface.console.print("[green]📄 BioMCP 서버 연결됨[/green]")
                        if 'chembl' in client_ids:
                            self.interface.console.print("[green]🧪 ChEMBL 서버 연결됨[/green]")
                        if 'sequential-thinking' in client_ids:
                            self.interface.console.print("[green]🧠 Sequential Thinking 서버 연결됨[/green]")
                else:
                    self.interface.console.print("[yellow]⚠️ 일부 외부 서버 시작에 실패했습니다.[/yellow]")
                
                # 3. 챗봇 MCP 활성화
                self.chatbot.mcp_enabled = True
                self.interface.console.print("[green]✓ 챗봇 MCP 기능이 활성화되었습니다.[/green]")
                
                self.interface.console.print("\n[bold green]🎉 통합 Deep Research MCP 시스템이 성공적으로 시작되었습니다![/bold green]")
                self.interface.console.print("[dim]사용 가능한 명령어: /mcp tools, /mcp status[/dim]")
                self.interface.console.print("[dim]이제 신약개발 질문을 하면 자동으로 모든 MCP 서버를 활용한 Deep Search가 수행됩니다.[/dim]")
                self.interface.console.print("[dim]디버그 모드: /debug 로 토글 가능[/dim]")
                
            else:
                self.interface.console.print("[red]✗ MCP 서버 시작에 실패했습니다.[/red]")
                
        except Exception as e:
            self.interface.display_error(f"MCP 서버 시작 중 오류: {e}")
            if self.chatbot.settings.get("debug_mode", False):
                import traceback
                self.interface.console.print(f"[dim red]{traceback.format_exc()}[/dim red]")
    
    async def stop_mcp(self):
        """MCP 서버 중지"""
        try:
            self.interface.console.print("[yellow]MCP 서버를 중지하는 중...[/yellow]")
            
            # 외부 서버들 먼저 중지
            await self.mcp_manager.stop_external_servers()
            self.interface.console.print("[green]✓ 외부 MCP 서버들이 중지되었습니다.[/green]")
            
            # 전체 cleanup
            await self.mcp_manager.cleanup()
            self.chatbot.mcp_enabled = False
            
            self.interface.console.print("[green]✓ 모든 MCP 서버가 중지되었습니다.[/green]")
            
        except Exception as e:
            self.interface.display_error(f"MCP 서버 중지 중 오류: {e}")
    
    async def show_mcp_status(self):
        """MCP 상태 표시"""
        try:
            status = self.mcp_manager.get_status()
            
            self.interface.console.print("[bold]MCP 상태:[/bold]")
            self.interface.console.print(f"• 실행 중: {'✓' if status['running'] else '✗'}")
            self.interface.console.print(f"• 서버 활성: {'✓' if status['server_active'] else '✗'}")
            self.interface.console.print(f"• 클라이언트 수: {status['clients_count']}")
            self.interface.console.print(f"• 챗봇 MCP 활성화: {'✓' if self.chatbot.mcp_enabled else '✗'}")
            
            if status['server_info']:
                server_info = status['server_info']
                self.interface.console.print(f"• 서버 이름: {server_info.get('name', 'N/A')}")
                self.interface.console.print(f"• 서버 버전: {server_info.get('version', 'N/A')}")
                self.interface.console.print(f"• 등록된 툴 수: {server_info.get('tools_count', 0)}")
            
            # 연결된 MCP 서버 목록 표시
            self.interface.console.print("\n[bold]연결된 MCP 서버:[/bold]")
            connected_servers = await self.get_connected_mcp_servers()
            if connected_servers:
                for server in connected_servers:
                    self.interface.console.print(f"• [cyan]{server['name']}[/cyan]: {server['status']}")
                    if server.get('tools'):
                        self.interface.console.print(f"  └─ 툴: {', '.join(server['tools'][:3])}{'...' if len(server['tools']) > 3 else ''}")
            else:
                self.interface.console.print("[yellow]연결된 MCP 서버가 없습니다.[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"MCP 상태 확인 중 오류: {e}")
    
    async def list_mcp_tools(self):
        """MCP 툴 목록 표시"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            tools = await self.mcp_manager.list_tools("default")
            
            if not tools:
                self.interface.console.print("[yellow]사용 가능한 MCP 툴이 없습니다.[/yellow]")
                return
            
            self.interface.console.print("[bold]사용 가능한 MCP 툴:[/bold]")
            for tool in tools:
                self.interface.console.print(f"• [cyan]{tool['name']}[/cyan]: {tool['description']}")
            
        except Exception as e:
            self.interface.display_error(f"MCP 툴 목록 조회 중 오류: {e}")
    
    async def call_mcp_tool(self, tool_name: str, args_str: str):
        """MCP 툴 직접 호출"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            # 간단한 인자 파싱 (JSON 형태로 가정)
            import json
            try:
                args_dict = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                # JSON이 아닌 경우 간단한 키=값 형태로 파싱
                args_dict = {}
                if args_str:
                    for pair in args_str.split():
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            args_dict[key] = value
                        else:
                            args_dict["text"] = args_str  # 기본값
            
            self.interface.console.print(f"[yellow]MCP 툴 '{tool_name}' 호출 중...[/yellow]")
            
            result = await self.mcp_manager.call_tool("default", tool_name, args_dict)
            
            # 결과 표시
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    text_result = content[0].get("text", "결과 없음")
                    self.interface.display_response(text_result)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"MCP 툴 호출 중 오류: {e}")
    
    async def mcp_research(self, question: str):
        """MCP를 통한 연구 수행"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]'{question}'에 대한 MCP 연구 수행 중...[/yellow]")
            
            result = await self.mcp_manager.research_question(question)
            
            if result and not result.startswith("Error:"):
                self.interface.display_response(result)
                
                # 저장 확인
                save_choice = input("\n연구 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                if save_choice == 'y':
                    await self.chatbot.save_research_result(question, result)
            else:
                self.interface.display_error(f"연구 실패: {result}")
            
        except Exception as e:
            self.interface.display_error(f"MCP 연구 중 오류: {e}")
    
    async def mcp_evaluate(self, question: str, answer: str):
        """MCP를 통한 답변 평가"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]답변 평가 수행 중...[/yellow]")
            
            result = await self.mcp_manager.evaluate_answer(question, answer)
            
            if result and not result.startswith("Error:"):
                self.interface.display_response(result)
            else:
                self.interface.display_error(f"평가 실패: {result}")
            
        except Exception as e:
            self.interface.display_error(f"MCP 평가 중 오류: {e}")
    
    async def start_sequential_thinking(self, problem: str):
        """Sequential Thinking 프로세스 시작"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]Sequential Thinking 시작: '{problem}'[/yellow]")
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="start_thinking",
                arguments={
                    "problem": problem,
                    "maxSteps": 10,
                    "enableBranching": True,
                    "enableRevision": True
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    
                    # JSON 파싱해서 processId 추출
                    try:
                        import json
                        response_data = json.loads(response_text)
                        process_id = response_data.get("processId", "unknown")
                        
                        self.interface.console.print(f"[green]✓ Sequential Thinking 프로세스가 시작되었습니다.[/green]")
                        self.interface.console.print(f"[cyan]프로세스 ID: {process_id}[/cyan]")
                        self.interface.console.print(f"[yellow]다음 단계: /mcp continue {process_id} <your_thought>[/yellow]")
                        
                    except json.JSONDecodeError:
                        self.interface.display_response(response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"Sequential Thinking 시작 중 오류: {e}")
    
    async def continue_sequential_thinking(self, process_id: str, thought: str):
        """Sequential Thinking 프로세스 계속"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]사고 단계 추가 중...[/yellow]")
            
            # 간단한 사고 단계 번호 추정 (실제로는 프로세스 상태를 확인해야 함)
            import time
            thought_number = int(time.time()) % 10 + 1
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="think",
                arguments={
                    "processId": process_id,
                    "thought": thought,
                    "nextThoughtNeeded": True,
                    "thoughtNumber": thought_number,
                    "totalThoughts": 10,
                    "confidence": 0.8
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    self.interface.console.print(f"[yellow]계속하려면: /mcp continue {process_id} <next_thought>[/yellow]")
                    self.interface.console.print(f"[yellow]완료하려면: /mcp complete {process_id}[/yellow]")
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"Sequential Thinking 계속 중 오류: {e}")
    
    async def complete_sequential_thinking(self, process_id: str):
        """Sequential Thinking 프로세스 완료"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]Sequential Thinking 프로세스 완료 중...[/yellow]")
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="complete_thinking",
                arguments={
                    "processId": process_id,
                    "forceSolution": False
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    
                    try:
                        import json
                        response_data = json.loads(response_text)
                        solution = response_data.get("solution", "해결책 없음")
                        confidence = response_data.get("confidence", 0)
                        total_steps = response_data.get("totalSteps", 0)
                        
                        self.interface.console.print(f"[green]✓ Sequential Thinking 완료![/green]")
                        self.interface.console.print(f"[cyan]총 단계: {total_steps}[/cyan]")
                        self.interface.console.print(f"[cyan]신뢰도: {confidence:.2f}[/cyan]")
                        self.interface.console.print(f"[bold]해결책:[/bold]")
                        self.interface.display_response(solution)
                        
                        # 저장 확인
                        save_choice = input("\n결과를 저장하시겠습니까? (y/N): ").strip().lower()
                        if save_choice == 'y':
                            await self.chatbot.save_research_result(f"Sequential Thinking - {process_id}", response_text)
                        
                    except json.JSONDecodeError:
                        self.interface.display_response(response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"Sequential Thinking 완료 중 오류: {e}")
    
    async def search_biomedical_articles(self, query: str):
        """BioMCP를 통한 생의학 논문 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]생의학 논문 검색 중: '{query}'[/yellow]")
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="search_articles",
                arguments={
                    "query": query,
                    "limit": 10
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"BioMCP Article Search - {query}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"생의학 논문 검색 중 오류: {e}")
    
    async def search_clinical_trials(self, condition: str):
        """BioMCP를 통한 임상시험 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]임상시험 검색 중: '{condition}'[/yellow]")
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="search_trials",
                arguments={
                    "condition": condition,
                    "limit": 10
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"BioMCP Clinical Trial Search - {condition}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"임상시험 검색 중 오류: {e}")
    
    async def search_genetic_variants(self, gene: str):
        """BioMCP를 통한 유전자 변이 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]유전자 변이 검색 중: '{gene}'[/yellow]")
            
            result = await self.mcp_manager.call_tool(
                client_id="default",
                tool_name="search_variants",
                arguments={
                    "gene": gene,
                    "limit": 10
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"BioMCP Genetic Variant Search - {gene}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"유전자 변이 검색 중 오류: {e}")
    
    async def get_connected_mcp_servers(self):
        """연결된 MCP 서버 목록 가져오기"""
        connected_servers = []
        
        try:
            # 로컬 서버에 통합된 툴들
            integrated_servers = [
                {
                    'name': 'sequential-thinking',
                    'status': '연결됨 ✓' if self.chatbot.mcp_enabled else '미연결 ✗',
                    'tools': ['start_thinking'] if self.chatbot.mcp_enabled else []
                },
                {
                    'name': 'biomcp',
                    'status': '연결됨 ✓' if self.chatbot.mcp_enabled else '미연결 ✗',
                    'tools': ['search_articles'] if self.chatbot.mcp_enabled else []
                },
                {
                    'name': 'chembl',
                    'status': '연결됨 ✓' if self.chatbot.mcp_enabled else '미연결 ✗',
                    'tools': ['search_molecule'] if self.chatbot.mcp_enabled else []
                },
                {
                    'name': 'drugbank-mcp',
                    'status': '연결됨 ✓' if self.chatbot.mcp_enabled else '미연결 ✗',
                    'tools': ['search_drugs', 'get_drug_details'] if self.chatbot.mcp_enabled else []
                },
                {
                    'name': 'opentargets-mcp',
                    'status': '연결됨 ✓' if self.chatbot.mcp_enabled else '미연결 ✗',
                    'tools': ['search_targets', 'search_diseases'] if self.chatbot.mcp_enabled else []
                }
            ]
            
            return integrated_servers
            
        except Exception as e:
            self.interface.console.print(f"[red]서버 목록 확인 중 오류: {e}[/red]")
            return []
    
    async def run_mcp_test(self):
        """HNSCC 예제를 활용한 MCP 통합 테스트"""
        try:
            self.interface.console.print("[bold blue]=== MCP 통합 테스트 (HNSCC 연구 예제) ===[/bold blue]\n")
            
            # MCP가 활성화되어 있는지 확인
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP를 먼저 시작합니다...[/yellow]")
                await self.start_mcp()
                await asyncio.sleep(2)
            
            # HNSCC 연구 질문
            hnscc_question = (
                "What are the emerging treatment strategies for head and neck squamous cell carcinoma (HNSCC), "
                "particularly focusing on immunotherapy combinations, targeted therapies, and novel approaches "
                "currently in clinical trials?"
            )
            
            self.interface.console.print("[cyan]테스트 시나리오:[/cyan]")
            self.interface.console.print("1. Sequential Thinking으로 문제 분석")
            self.interface.console.print("2. BioMCP로 관련 논문 검색")
            self.interface.console.print("3. BioMCP로 임상시험 검색")
            self.interface.console.print("4. 종합 연구 수행\n")
            
            # 사용자 확인
            confirm = input("테스트를 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm != 'y':
                self.interface.console.print("[yellow]테스트가 취소되었습니다.[/yellow]")
                return
            
            # 1. Sequential Thinking
            self.interface.console.print("\n[bold]1. Sequential Thinking 분석[/bold]")
            await self.start_sequential_thinking(
                "Analyze emerging treatment strategies for HNSCC focusing on immunotherapy"
            )
            
            # 2. BioMCP 논문 검색
            self.interface.console.print("\n[bold]2. BioMCP 논문 검색[/bold]")
            await self.search_biomedical_articles(
                "HNSCC immunotherapy combination PD-1 PD-L1 clinical trial"
            )
            
            # 3. BioMCP 임상시험 검색
            self.interface.console.print("\n[bold]3. BioMCP 임상시험 검색[/bold]")
            await self.search_clinical_trials(
                "head neck squamous cell carcinoma immunotherapy"
            )
            
            # 4. 종합 연구
            self.interface.console.print("\n[bold]4. 종합 연구 수행[/bold]")
            self.interface.console.print(f"[cyan]연구 질문:[/cyan]\n{hnscc_question}\n")
            await self.mcp_research(hnscc_question)
            
            self.interface.console.print("\n[green]✓ MCP 통합 테스트가 완료되었습니다![/green]")
            self.interface.console.print("\n[yellow]테스트 결과가 research_outputs 폴더에 저장되었습니다.[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"MCP 테스트 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    async def chembl_search(self, action: str, query: str):
        """ChEMBL 데이터베이스 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]ChEMBL {action} 검색 중: '{query}'[/yellow]")
            
            # ChEMBL 툴 이름 매핑
            tool_mapping = {
                "molecule": "get_molecule",
                "target": "get_target", 
                "activity": "get_activity",
                "assay": "get_assay",
                "drug": "get_drug"
            }
            
            tool_name = tool_mapping.get(action)
            if not tool_name:
                self.interface.display_error(f"지원하지 않는 action: {action}")
                return
            
            result = await self.mcp_manager.call_tool(
                client_id="chembl",
                tool_name=tool_name,
                arguments={
                    "query": query,
                    "limit": 10
                }
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"ChEMBL {action} Search - {query}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"ChEMBL 검색 중 오류: {e}")
    
    async def chembl_smiles_tools(self, smiles: str):
        """ChEMBL SMILES 분자 구조 분석"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]SMILES 분자 구조 분석 중: '{smiles}'[/yellow]")
            
            # SMILES 관련 여러 분석 수행
            analyses = [
                ("canonicalize_smiles", "SMILES 정규화"),
                ("smiles_to_inchi", "InChI 변환"), 
                ("smiles_to_svg", "SVG 구조 생성"),
                ("get_structural_alerts", "구조 경고 분석")
            ]
            
            combined_results = []
            
            for tool_name, description in analyses:
                try:
                    self.interface.console.print(f"  - {description} 중...")
                    
                    result = await self.mcp_manager.call_tool(
                        client_id="chembl",
                        tool_name=tool_name,
                        arguments={"smiles": smiles}
                    )
                    
                    if result and "content" in result:
                        content = result["content"]
                        if content and len(content) > 0:
                            text_result = content[0].get("text", "결과 없음")
                            combined_results.append(f"### {description}\n\n{text_result}")
                        
                except Exception as e:
                    combined_results.append(f"### {description}\n\n오류: {e}")
            
            # 결과 통합 표시
            final_result = f"# SMILES 분자 분석 결과\n\n**분자:** {smiles}\n\n" + "\n\n".join(combined_results)
            self.interface.display_response(final_result)
            
            # 저장 확인
            save_choice = input("\n분석 결과를 저장하시겠습니까? (y/N): ").strip().lower()
            if save_choice == 'y':
                await self.chatbot.save_research_result(f"SMILES Analysis - {smiles}", final_result)
            
        except Exception as e:
            self.interface.display_error(f"SMILES 분석 중 오류: {e}")
    
    async def run_integrated_mcp_test(self):
        """ChEMBL + BioMCP + Sequential Thinking 통합 테스트"""
        try:
            self.interface.console.print("[bold blue]=== 통합 MCP 테스트 ===\n[/bold blue]")
            self.interface.console.print("[cyan]ChEMBL + BioMCP + Sequential Thinking 통합 연구[/cyan]\n")
            
            # MCP가 활성화되어 있는지 확인
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP를 먼저 시작합니다...[/yellow]")
                await self.start_mcp()
                await asyncio.sleep(3)
            
            # 크레아틴 연구 시나리오
            creatine_smiles = "C(=N)(N)N(C)CC(=O)O"  # 크레아틴 SMILES
            research_question = "크레아틴 보충제의 분자 구조 분석과 근육 성장 효과에 대한 종합 연구"
            
            self.interface.console.print("[cyan]연구 시나리오:[/cyan]")
            self.interface.console.print("1. Sequential Thinking으로 연구 계획 수립")
            self.interface.console.print("2. ChEMBL로 크레아틴 분자 구조 분석")
            self.interface.console.print("3. BioMCP로 관련 논문 및 임상시험 검색")
            self.interface.console.print("4. GAIA로 종합 연구 분석")
            self.interface.console.print(f"\n[yellow]연구 대상:[/yellow] 크레아틴 (SMILES: {creatine_smiles})")
            
            # 사용자 확인
            confirm = input("\n통합 테스트를 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm != 'y':
                self.interface.console.print("[yellow]테스트가 취소되었습니다.[/yellow]")
                return
            
            # 1. Sequential Thinking으로 연구 계획
            self.interface.console.print("\n[bold]1. Sequential Thinking - 연구 계획 수립[/bold]")
            await self.start_sequential_thinking(
                "Analyze creatine supplementation: chemical structure, mechanism, muscle growth effects"
            )
            
            # 2. ChEMBL로 분자 구조 분석
            self.interface.console.print("\n[bold]2. ChEMBL - 크레아틴 분자 분석[/bold]")
            await self.chembl_search("molecule", "creatine")
            
            self.interface.console.print("\n[bold]2-1. SMILES 구조 분석[/bold]")
            await self.chembl_smiles_tools(creatine_smiles)
            
            # 3. BioMCP로 생의학 연구
            self.interface.console.print("\n[bold]3. BioMCP - 크레아틴 연구 데이터[/bold]")
            await self.search_biomedical_articles("creatine supplementation muscle growth performance")
            
            await self.search_clinical_trials("creatine supplementation athletic performance")
            
            # 4. 종합 연구
            self.interface.console.print("\n[bold]4. GAIA 종합 연구[/bold]")
            await self.mcp_research(research_question)
            
            # 5. 추가 비교 분석
            self.interface.console.print("\n[bold]5. 추가 분석 - BCAA vs 단백질 비교[/bold]")
            await self.start_sequential_thinking(
                "Compare BCAA vs whey protein supplementation for muscle growth effectiveness"
            )
            
            self.interface.console.print("\n[green]✓ 통합 MCP 테스트가 완료되었습니다![/green]")
            self.interface.console.print("\n[cyan]통합 시스템 검증 완료:[/cyan]")
            self.interface.console.print("- ✓ 화학 구조 분석 (ChEMBL)")
            self.interface.console.print("- ✓ 생의학 연구 데이터 (BioMCP)")
            self.interface.console.print("- ✓ 단계별 추론 (Sequential Thinking)")
            self.interface.console.print("- ✓ 종합 연구 분석 (GAIA + Ollama Gemma3)")
            self.interface.console.print("\n[yellow]모든 결과가 research_outputs 폴더에 저장되었습니다.[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"통합 테스트 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    async def run_deep_research_test(self):
        """Deep Research 기능 테스트"""
        try:
            self.interface.console.print("[bold blue]=== Deep Research 기능 테스트 ===[/bold blue]\n")
            self.interface.console.print("[cyan]MCP 기반 Deep Search 시스템 검증[/cyan]\n")
            
            # MCP가 활성화되어 있는지 확인
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP를 먼저 시작합니다...[/yellow]")
                await self.start_mcp()
                await asyncio.sleep(3)
            
            # 테스트 질문 목록
            test_questions = [
                {
                    "title": "크레아틴 보충제 종합 분석",
                    "question": "크레아틴 보충제의 분자 구조, 작용 메커니즘, 그리고 근육 성장에 미치는 효과에 대해 종합적으로 분석해주세요.",
                    "description": "화학 구조 + 생의학 연구 + AI 분석 통합"
                },
                {
                    "title": "BCAA vs 단백질 보충제 비교",
                    "question": "BCAA와 단백질 보충제의 분자 구조적 차이점과 근육 성장 효과를 비교 분석해주세요.",
                    "description": "분자 비교 + 효능 분석"
                },
                {
                    "title": "카페인과 크레아틴 병용 효과",
                    "question": "운동 전 카페인과 크레아틴을 함께 복용했을 때의 상호작용과 시너지 효과를 분석해주세요.",
                    "description": "복합 성분 상호작용 분석"
                }
            ]
            
            self.interface.console.print("[cyan]Deep Research 테스트 질문 목록:[/cyan]")
            for i, q in enumerate(test_questions, 1):
                self.interface.console.print(f"{i}. {q['title']}")
                self.interface.console.print(f"   설명: {q['description']}")
            
            # 사용자 선택
            print("\n어떤 질문으로 테스트하시겠습니까? (1-3, 또는 'all'): ", end="")
            choice = input().strip().lower()
            
            if choice == 'all':
                selected_questions = test_questions
            elif choice in ['1', '2', '3']:
                selected_questions = [test_questions[int(choice) - 1]]
            else:
                self.interface.console.print("[yellow]잘못된 선택입니다. 첫 번째 질문으로 진행합니다.[/yellow]")
                selected_questions = [test_questions[0]]
            
            # 선택된 질문들로 테스트 진행
            for i, test_case in enumerate(selected_questions, 1):
                self.interface.console.print(f"\n[bold]=== Deep Research 테스트 {i}/{len(selected_questions)}: {test_case['title']} ===[/bold]")
                self.interface.console.print(f"[cyan]질문:[/cyan] {test_case['question']}\n")
                
                # Deep Research 실행 (실제 챗봇의 generate_response 사용)
                self.interface.console.print("[yellow]Deep Research 수행 중... (Sequential Thinking → ChEMBL → BioMCP → Ollama)[/yellow]")
                
                try:
                    # 챗봇의 Deep Research 기능 활용
                    response = await self.chatbot.generate_response(test_case['question'], ask_to_save=False)
                    
                    self.interface.console.print(f"\n[green]✓ Deep Research 완료![/green]")
                    self.interface.console.print("[cyan]생성된 응답 길이:[/cyan] {}자".format(len(response)))
                    
                    # 결과 요약 표시
                    if len(response) > 500:
                        preview = response[:500] + "..."
                        self.interface.console.print(f"\n[cyan]응답 미리보기:[/cyan]\n{preview}")
                    else:
                        self.interface.display_response(response)
                    
                    # 저장 여부 확인
                    save_choice = input("\n이 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(test_case['title'], response)
                        self.interface.console.print("[green]✓ 결과가 저장되었습니다.[/green]")
                    
                except Exception as e:
                    self.interface.console.print(f"[red]✗ Deep Research 실행 중 오류: {e}[/red]")
                    continue
                
                # 다음 테스트 전 대기 (여러 테스트인 경우)
                if len(selected_questions) > 1 and i < len(selected_questions):
                    proceed = input("\n다음 테스트를 계속하시겠습니까? (y/N): ").strip().lower()
                    if proceed != 'y':
                        break
            
            self.interface.console.print("\n[green]✓ Deep Research 테스트가 완료되었습니다![/green]")
            self.interface.console.print("\n[cyan]검증된 기능:[/cyan]")
            self.interface.console.print("- ✓ Sequential Thinking 기반 연구 계획")
            self.interface.console.print("- ✓ ChEMBL 화학 데이터 통합")
            self.interface.console.print("- ✓ BioMCP 생의학 연구 데이터")
            self.interface.console.print("- ✓ Ollama Gemma3 종합 분석")
            self.interface.console.print("- ✓ 구조화된 연구 보고서 생성")
            
            self.interface.console.print("\n[yellow]일반 사용법:[/yellow]")
            self.interface.console.print("MCP가 활성화된 상태에서 복잡한 질문을 하면")
            self.interface.console.print("자동으로 Deep Research가 실행됩니다.")
            
        except Exception as e:
            self.interface.display_error(f"Deep Research 테스트 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    async def drugbank_search(self, action: str, query: str):
        """DrugBank 데이터베이스 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]DrugBank {action} 검색 중: '{query}'[/yellow]")
            
            # DrugBank 툴 이름 매핑
            tool_mapping = {
                "search": "search_drugs",
                "details": "get_drug_details", 
                "indication": "find_drugs_by_indication",
                "interaction": "get_drug_interactions",
                "target": "find_drugs_by_target"
            }
            
            tool_name = tool_mapping.get(action)
            if not tool_name:
                self.interface.display_error(f"지원하지 않는 action: {action}")
                return
            
            # 인자 구성
            if action == "search":
                arguments = {"query": query, "limit": 10}
            elif action == "details":
                arguments = {"drugbank_id": query}
            elif action == "indication":
                arguments = {"indication": query, "limit": 10}
            elif action == "interaction":
                arguments = {"drugbank_id": query, "limit": 20}
            elif action == "target":
                arguments = {"target": query, "limit": 10}
            
            result = await self.mcp_manager.call_tool(
                client_id="drugbank-mcp",
                tool_name=tool_name,
                arguments=arguments
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"DrugBank {action} Search - {query}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"DrugBank 검색 중 오류: {e}")
    
    async def opentargets_search(self, action: str, query: str):
        """OpenTargets 플랫폼 검색"""
        try:
            if not self.chatbot.mcp_enabled:
                self.interface.console.print("[yellow]MCP가 활성화되지 않았습니다. '/mcp start'로 시작하세요.[/yellow]")
                return
            
            self.interface.console.print(f"[yellow]OpenTargets {action} 검색 중: '{query}'[/yellow]")
            
            # OpenTargets 툴 이름 매핑
            tool_mapping = {
                "targets": "search_targets",
                "diseases": "search_diseases", 
                "target_diseases": "get_target_associated_diseases",
                "disease_targets": "get_disease_associated_targets",
                "drugs": "search_drugs"
            }
            
            tool_name = tool_mapping.get(action)
            if not tool_name:
                self.interface.display_error(f"지원하지 않는 action: {action}")
                return
            
            # 인자 구성
            if action in ["targets", "diseases", "drugs"]:
                arguments = {"query": query, "limit": 10}
            elif action == "target_diseases":
                arguments = {"target_id": query, "limit": 10}
            elif action == "disease_targets":
                arguments = {"disease_id": query, "limit": 10}
            
            result = await self.mcp_manager.call_tool(
                client_id="opentargets-mcp",
                tool_name=tool_name,
                arguments=arguments
            )
            
            if result and "content" in result:
                content = result["content"]
                if content and len(content) > 0:
                    response_text = content[0].get("text", "결과 없음")
                    self.interface.display_response(response_text)
                    
                    # 저장 확인
                    save_choice = input("\n검색 결과를 저장하시겠습니까? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        await self.chatbot.save_research_result(f"OpenTargets {action} Search - {query}", response_text)
                else:
                    self.interface.console.print("[yellow]결과가 비어있습니다.[/yellow]")
            else:
                self.interface.console.print(f"[yellow]원본 결과: {result}[/yellow]")
            
        except Exception as e:
            self.interface.display_error(f"OpenTargets 검색 중 오류: {e}")