from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, TextPart, Message
from a2a.server.agent_execution.context import RequestContext
from dotenv import load_dotenv
from ddgs import DDGS
from uuid import uuid4
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

    async def execute(self, request, queue):
        try:
            user_query = ""
            message = request.message

            for part in message.parts:
                if hasattr(part, "root") and isinstance(part.root, TextPart):
                    user_query += part.root.text

            result = self.agent.web_search(user_query)

            response_message = Message(
                messageId=uuid4().hex,
                role="agent",
                parts=[TextPart(text=result)]
            )

            await queue.enqueue_event(response_message)

        except Exception as e:
            error_message = Message(
                messageId=uuid4().hex,
                role="agent",
                parts=[TextPart(text=f"Error: {str(e)}")]
            )

            await queue.enqueue_event(error_message)


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
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supports_authenticated_extended_card=True
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