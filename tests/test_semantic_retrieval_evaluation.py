from codemind.embeddings.service import EmbeddingService
from codemind.vectorstore.service import VectorStoreService
from codemind.search.evaluation import (
    precision_at_k,
    recall_at_k,
)


def test_evaluate_real_semantic_retrieval(tmp_path):
    embedding_service = EmbeddingService()

    vector_store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="retrieval_benchmark",
    )

    documents = [
        {
            "id": "payment_001",
            "text": "Validate payment details and charge a customer's credit card.",
            "symbol": "process_payment",
        },
        {
            "id": "payment_002",
            "text": "Refund a completed customer transaction and reverse the payment.",
            "symbol": "refund_payment",
        },
        {
            "id": "hr_001",
            "text": "Generate employee attendance reports and calculate working hours.",
            "symbol": "generate_employee_report",
        },
        {
            "id": "hr_002",
            "text": "Calculate employee salaries and monthly payroll.",
            "symbol": "calculate_payroll",
        },
        {
            "id": "image_001",
            "text": "Resize uploaded images and generate thumbnail previews.",
            "symbol": "resize_image",
        },
        {
            "id": "image_002",
            "text": "Compress image files and optimize image quality.",
            "symbol": "compress_image",
        },
    ]

    # Generate all document embeddings in one batch.
    texts = [document["text"] for document in documents]
    embeddings = embedding_service.generate_embeddings(texts)

    for document, embedding in zip(documents, embeddings):
        vector_store.add_code(
            document_id=document["id"],
            text=document["text"],
            embedding=embedding,
            metadata={"symbol": document["symbol"]},
        )

    assert vector_store.count() == 6

    benchmark_queries = [
        {
            "query": "Find code that handles customer payments and refunds.",
            "relevant_ids": {"payment_001", "payment_002"},
        },
        {
            "query": "Find code that manages employee salaries and attendance.",
            "relevant_ids": {"hr_001", "hr_002"},
        },
        {
            "query": "Find code that resizes and optimizes uploaded images.",
            "relevant_ids": {"image_001", "image_002"},
        },
    ]

    k = 3

    for benchmark in benchmark_queries:
        query_embedding = embedding_service.generate_query_embedding(benchmark["query"])

        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
        )

        retrieved_ids = [result["id"] for result in results]

        precision = precision_at_k(
            retrieved_ids,
            benchmark["relevant_ids"],
            k,
        )

        recall = recall_at_k(
            retrieved_ids,
            benchmark["relevant_ids"],
            k,
        )

        print(f"\nQuery: {benchmark['query']}")
        print(f"Retrieved: {retrieved_ids}")
        print(f"Precision@{k}: {precision:.2f}")
        print(f"Recall@{k}: {recall:.2f}")

        # At least one relevant document should appear in the top 3.
        assert set(retrieved_ids) & benchmark["relevant_ids"]
