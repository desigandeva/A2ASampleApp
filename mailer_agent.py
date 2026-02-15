import uvicorn
import smtplib
from uuid import uuid4
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TextPart,
    Message
)
from dotenv import load_dotenv
import os
from email.message import EmailMessage

class MailExecutor:

    def __init__(self):
        self.sender_mail_id = ""
        self.sender_mail_password = ""
        self.receiver_mail_id = ""
        self.subject = ""
        self.message = ""
        load_dotenv()

    # @staticmethod
    def send_email(self, to_email: str, subject: str, body: str) -> str:
        try:
            sender_email = os.getenv("SENDERMAIL")
            app_password = os.getenv("SENDERPASSWORD")

            msg = EmailMessage()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)

            return "Mail sent successfully"
        except Exception as e:
            return f"Error: {e}"

    async def execute(self, request, queue):
        self.receiver_mail_id = os.getenv("RECEIVERMAIL")
        # print(request.message.parts)
        user_text = request.message.parts[0].root.text.lower()

        if "mail" in user_text:
            # Hardcoded example (later we can parse dynamically)
            result = MailExecutor.send_email(
                to_email=self.receiver_mail_id,
                subject="Test Mail from A2A",
                body="Hello, this is a test mail sent from my A2A agent."
            )
        else:
            result = "I can only send emails."

        response_message = Message(
            messageId=uuid4().hex,
            role="agent",
            parts=[TextPart(text=result)]
        )

        await queue.produce(response_message)

if __name__ == '__main__':
    skill = AgentSkill(
        id='mailer',
        name='Mail Agent',
        description='just mail agent',
        tags=['mail','email','gmail'],
        examples=['send me an email','mail me'],
    )

    extended_skill = AgentSkill(
        id='mailer-extended',
        name='Super Mail Agent',
        description='Just a super mail agent.',
        tags=['mail','email','gmail'],
        examples=['send me an email','mail me'],
    )

    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Mailer Agent',
        description='The basic mail agent for public users.',
        url='http://localhost:9001/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],  # Only the basic skill for the public card
        supports_authenticated_extended_card=True,
    )

    # # This will be the authenticated extended agent card
    # # It includes the additional 'extended_skill'
    # specific_extended_agent_card = public_agent_card.model_copy(
    #     update={
    #         'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
    #         'description': 'The full-featured hello world agent for authenticated users.',
    #         'version': '1.0.1',  # Could even be a different version
    #         # Capabilities and other fields like url, default_input_modes, default_output_modes,
    #         # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
    #         'skills': [
    #             skill,
    #             extended_skill,
    #         ],  # Both skills for the extended card
    #     }
    # )

    request_handler = DefaultRequestHandler(
        agent_executor=MailExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9001)