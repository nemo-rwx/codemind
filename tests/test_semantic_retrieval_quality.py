from codemind.embeddings.service import EmbeddingService
from codemind.vectorstore.service import VectorStoreService


def test_semantic_search_retrieves_relevant_code(tmp_path):
    embedding_service = EmbeddingService()

    vector_store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="retrieval_quality_test",
    )

    documents = [
        {
            "id": "payment_001",
            "text": """
            def process_payment(amount, card):
                Validate payment details and transaction amount.
                Charge the customer's credit card.
                Return the payment confirmation.
            """,
            "metadata": {
                "symbol": "process_payment",
                "kind": "function",
            },
        },
        {
            "id": "report_001",
            "text": """
            def generate_employee_report(employees):
                Summarize employee attendance.
                Calculate working hours and generate an HR report.
            """,
            "metadata": {
                "symbol": "generate_employee_report",
                "kind": "function",
            },
        },
        {
            "id": "image_001",
            "text": """
            def resize_image(image_path):
                Resize an uploaded image.
                Create a thumbnail and save the processed image.
            """,
            "metadata": {
                "symbol": "resize_image",
                "kind": "function",
            },
        },
    ]

    # Generate embeddings for all documents.
    texts = [document["text"] for document in documents]

    embeddings = embedding_service.generate_embeddings(texts)

    # Store documents and their embeddings.
    for document, embedding in zip(documents, embeddings):
        vector_store.add_code(
            document_id=document["id"],
            text=document["text"],
            embedding=embedding,
            metadata=document["metadata"],
        )

    assert vector_store.count() == 3

    # Search using natural language rather than a function name.
    query = (
        "Where does the application validate a transaction "
        "and charge a customer's credit card?"
    )

    query_embedding = embedding_service.generate_query_embedding(query)

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    # The payment function should be the most relevant result.
    assert len(results) == 3
    assert results[0]["id"] == "payment_001"
    assert results[0]["metadata"]["symbol"] == "process_payment"
