from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, TextPart, Message
from agent_executor import ReimbursementAgentExecutor
from agent import ReimbursementAgent
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import uuid
load_dotenv()


class WebAgent:
    def web_search(self, user_query: str) -> str:
        results_text = ""

        with DDGS() as ddgs:
            results = list(ddgs.text(user_query, max_results=5))

        if not results:
            return "No results found."

        for i, r in enumerate(results, 1):
            results_text += (
                f"{i}. {r.get('title')}\n"
                f"   {r.get('href')}\n"
                f"   {r.get('body')}\n\n"
            )

        return results_text

class WebSearchAgentExecutor:
    SUPPORTED_CONTENT_TYPES = ["text"]

    def __init__(self):
        self.agent = WebAgent()

    async def execute(self, message: Message, **kwargs) -> Message:
        user_query = ""

        for part in message.parts:
            if isinstance(part, TextPart):
                user_query += part.text

        result = self.agent.web_search(user_query)

        return Message(
            id=str(uuid.uuid4()),
            role="assistant",
            parts=[TextPart(text=result)]
        )



if __name__ == '__main__':
    skill = AgentSkill(
        id='web-search',
        name='Web Search',
        description='Search the web for information about a topic',
        tags=['search', 'web', 'google'],
        examples=['what is the current treanding news?']
    )

    card = AgentCard(
        id='web-search-agent',
        name='Web Search Agent',
        description='Search the web for information about a topic',
        url='http://localhost:9002/',
        version='1.0.0',
        default_input_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supports_authenticated_extended_card=False
    )

    agent_executor = WebSearchAgentExecutor()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler
    )

    import uvicorn
    uvicorn.run(server.build(), host='0.0.0.0', port=9002)