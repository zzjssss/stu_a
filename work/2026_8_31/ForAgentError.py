class AgentError(Exception):
    def __init__(self,a):
        self.a = a
    def __str__(self):
        return "this is the error of AgentError"



class TokenAgentError(AgentError):
    pass



class ModelAgentError(AgentError):
    pass # 避免空体错误
