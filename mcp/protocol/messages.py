"""
MCP Protocol Messages and Types
"""

from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
import json


class MCPMessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    INITIALIZE = "initialize"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    PING = "ping"


class MCPMessage:
    def __init__(self, jsonrpc: str = "2.0"):
        self.jsonrpc = jsonrpc
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass  
class MCPRequest(MCPMessage):
    method: str
    id: Union[str, int]
    params: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"
    
    def __post_init__(self):
        super().__init__(self.jsonrpc)


@dataclass
class MCPResponse(MCPMessage):
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"
    
    def __post_init__(self):
        super().__init__(self.jsonrpc)


@dataclass
class MCPNotification(MCPMessage):
    method: str
    params: Optional[Dict[str, Any]] = None
    jsonrpc: str = "2.0"
    
    def __post_init__(self):
        super().__init__(self.jsonrpc)


@dataclass
class MCPError:
    code: int
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


class MCPErrorCode(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000


@dataclass
class MCPTool:
    name: str
    description: str
    inputSchema: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }