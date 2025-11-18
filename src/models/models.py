from pydantic import BaseModel

class AgentConfig(BaseModel):
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000

class TaskConfig(BaseModel):
    task_type: str
    parameters: dict

class AgentState(BaseModel):
    current_task: str | None = None
    task_history: list[str] = []
    model_config: AgentConfig
    task_config: TaskConfig

