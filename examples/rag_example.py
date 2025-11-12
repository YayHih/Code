#!/usr/bin/env python3
"""
Example: Using RAG with Local LLM for Codebase-Aware Development

This demonstrates how to:
1. Load a RAG index created by setup_rag.py
2. Query for relevant code context
3. Use that context with your local LLM
4. Get better, more consistent code generation
"""

import sys
import subprocess
from pathlib import Path

try:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    print("Please install required packages:")
    print("  pip install langchain langchain-community sentence-transformers faiss-cpu")
    sys.exit(1)


class RAGCodeAssistant:
    """Code assistant with RAG-enhanced context"""

    def __init__(self, index_path: str = "./rag_system/codebase_index"):
        """Initialize with path to FAISS index"""
        self.index_path = Path(index_path)

        if not self.index_path.exists():
            print(f"Error: RAG index not found at {index_path}")
            print("Please run: python scripts/setup_rag.py /path/to/your/codebase")
            sys.exit(1)

        print("Loading RAG system...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = FAISS.load_local(
            str(self.index_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        print("✓ RAG system loaded")

    def get_relevant_context(self, query: str) -> str:
        """Get relevant code context for a query"""
        print(f"\nSearching codebase for: '{query}'")

        docs = self.retriever.get_relevant_documents(query)

        context_parts = []
        print(f"Found {len(docs)} relevant code snippets:\n")

        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'unknown')
            print(f"{i}. {source}")

            context_parts.append(f"# From {source}\n{doc.page_content}\n")

        return "\n".join(context_parts)

    def generate_with_context(
        self,
        task: str,
        model: str = "qwen2.5-coder:7b-instruct-q8_0"
    ):
        """Generate code using RAG context"""

        # Get relevant context
        context = self.get_relevant_context(task)

        # Build prompt with context
        prompt = f"""Using the following code examples from the codebase as reference:

{context}

Task: {task}

Please generate code that is consistent with the existing codebase style and patterns.
"""

        print("\n" + "=" * 60)
        print("Generating code with RAG context...")
        print("=" * 60)

        # Call Ollama
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=120
            )

            print("\nGenerated code:")
            print("-" * 60)
            print(result.stdout)
            print("-" * 60)

            return result.stdout

        except Exception as e:
            print(f"Error generating code: {e}")
            return None

    def interactive_mode(self):
        """Interactive RAG-enhanced coding mode"""
        print("\n" + "=" * 60)
        print("RAG-Enhanced Code Assistant")
        print("=" * 60)
        print("Enter your coding task, and I'll search the codebase")
        print("for relevant examples before generating code.")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                task = input("Task: ").strip()

                if task.lower() in ['quit', 'exit', 'q']:
                    break

                if not task:
                    continue

                self.generate_with_context(task)
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break


def example_usage():
    """Example of using RAG with local LLM"""

    # Initialize RAG assistant
    assistant = RAGCodeAssistant()

    # Example task
    task = "Create a function to parse configuration files"

    print("\n" + "=" * 60)
    print("Example: RAG-Enhanced Code Generation")
    print("=" * 60)

    # This will:
    # 1. Search the codebase for similar patterns
    # 2. Provide those as context to the LLM
    # 3. Generate code consistent with existing style
    assistant.generate_with_context(task)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            assistant = RAGCodeAssistant()
            assistant.interactive_mode()
        else:
            print("Usage:")
            print("  python rag_example.py              # Run example")
            print("  python rag_example.py interactive  # Interactive mode")
    else:
        example_usage()


if __name__ == "__main__":
    main()
