import ollama

class LLMService:
    def __init__(self , model: str = "qwen2.5:7b"):
        self.model = model

    def generate_answer(
            self ,
            question : str,
            context : str
    ) -> str:

        response = ollama.chat(
            model = self.model,
            messages = [
                {
                    "role" : "system",
                    "content" : (
                        "You are DocuMind, an AI assistant that answers "
                        "questions using the provided document context. "
                        "Use the context as your primary source of information. "
                        "If the answer is not present in the context, say so "
                        "clearly instead of inventing information. "
                        "Explain technical concepts clearly and accurately."
                    )
                },
                {
                    "role" : "user",
                    "content" :(
                        f"Document context : \n{context}\n\n"
                        f"Question:\n{question}"
                    )
                }
            ],
            options = {
                "tempreature" : 0.2
            }
        )

        answer = response["message"]["content"]

        return answer.strip()