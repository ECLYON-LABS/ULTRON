"""Ask an explicitly configured local checkpoint to draft website components."""

from eclipse.api.chat import ChatService
from eclipse.brain.model import LocalTransformersBackend


if __name__ == "__main__":
    service = ChatService(LocalTransformersBackend())
    result = service.chat([
        {"role": "user", "content": (
            "Draft a small accessible HTML/CSS landing page for ECLIPSE AI. "
            "Explain which parts would still need human review."
        )}
    ])
    print(result["answer"])