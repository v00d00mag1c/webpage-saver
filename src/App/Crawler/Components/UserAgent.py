from pydantic import Field, BaseModel
import ua_generator

class UserAgent(BaseModel):
    string: str = Field()

    @staticmethod
    def generate():
        return UserAgent(string = ua_generator.generate(device='desktop', browser=['chrome', 'edge']).text)
