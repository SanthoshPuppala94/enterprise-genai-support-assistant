from app.config import get_settings


class LLMClient:
    """OpenAI-compatible chat interface with an offline PoC fallback."""

    def __init__(self):
        self.settings = get_settings()
        self._client = None
        if self.settings.openai_api_key:
            from langchain_openai import ChatOpenAI

            self._client = ChatOpenAI(
                model=self.settings.openai_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0,
            )

    def invoke(self, prompt: str) -> str:
        if self._client is None:
            return f"Offline PoC response based on prompt: {prompt[:500]}"
        return self._client.invoke(prompt).content

