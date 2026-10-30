from pydantic import BaseModel, Field


class CodeSymbol(BaseModel):
    name: str
    kind: str
    start_line: int
    end_line: int
    parameters: str | None = None


class CodeImport(BaseModel):
    statement: str
    line: int


class CodeCall(BaseModel):
    name: str
    line: int


class ParsedFile(BaseModel):
    file_path: str
    language: str
    symbols: list[CodeSymbol] = Field(default_factory=list)
    imports: list[CodeImport] = Field(default_factory=list)
    calls: list[CodeCall] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
