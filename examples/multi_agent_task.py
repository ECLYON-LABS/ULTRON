"""Plan and execute a bounded task with registered Pluto agents."""

from eclipse.api.chat import ChatService
from eclipse.brain.model import LocalTransformersBackend


if __name__ == "__main__":
    request = input("Task: ").strip()
    result = ChatService(LocalTransformersBackend()).task({"prompt": request})
    print(result["answer"])
    print("Plan:", result["tasks"])