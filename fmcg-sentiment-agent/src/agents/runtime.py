"""
runtime.py
"""

import asyncio
import concurrent.futures
import threading

from src.agents.agent_core import run_turn

STARTUP_TIMEOUT = 400
REQUEST_TIMEOUT = 480


def create_backend(framework, model_spec):
    if framework == "langgraph":
        from src.agents.backend_langgraph import LangGraphBackend


        return LangGraphBackend(model_spec)
    raise ValueError("framework must be 'langgraph'")




class AgentRuntime:
    def __init__(self, framework, model_spec, audit_path=None):
        self.framework = framework
        self.model_spec = model_spec
        self.audit_path = audit_path
        self.backend = create_backend(framework, model_spec)
        self.turn_counts = {}
        self.session_reviews = {}
        self.ready = threading.Event()
        self.startup_error = None
        self.queue = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()


    @staticmethod
    def _quiet_handler(loop, context):
        if "overlapped future" in str(context.get("message", "")):
            return
        loop.default_exception_handler(context)


    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.set_exception_handler(self._quiet_handler)
        task = self.loop.create_task(self._serve())
        task.add_done_callback(lambda _: self.loop.stop())
        self.loop.run_forever()


    async def _serve(self):
        self.queue = asyncio.Queue()
        try:
            await self.backend.open()
        except Exception as exc:
            self.startup_error = exc
            self.ready.set()
            return
        self.ready.set()


        try:
            while True:
                item = await self.queue.get()
                if item is None:
                    break
                kwargs, future = item
                try:
                    result = await run_turn(
                        self.backend, kwargs["question"], kwargs["role"], kwargs["session_id"],
                        self.turn_counts, self.model_spec, self.audit_path, self.session_reviews,
                    )
                    future.set_result(result)
                except Exception as exc:
                    future.set_exception(exc)
        finally:
            await self.backend.close()


    def wait_until_ready(self):
        if not self.ready.wait(STARTUP_TIMEOUT):
            raise RuntimeError("The agent did not start in time.")
        if self.startup_error:
            raise RuntimeError(f"The agent failed to start: {self.startup_error}")


    def ask(self, question, role, session_id):
        self.wait_until_ready()
        future = concurrent.futures.Future()
        payload = ({"question": question, "role": role, "session_id": session_id}, future)
        self.loop.call_soon_threadsafe(self.queue.put_nowait, payload)
        return future.result(timeout=REQUEST_TIMEOUT)


    def close(self):
        if self.queue is not None and self.ready.is_set() and not self.startup_error:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, None)
        self.thread.join(timeout=30)



