from pydantic import BaseModel


class ValueExpression(BaseModel):
    content: str
