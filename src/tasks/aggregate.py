"""Results aggregation task logic."""

import json
import logging

from common.aws import get_s3_client

logger = logging.getLogger(__name__)


def aggregate_results(event: dict) -> dict:
    """Aggregate extraction results and write summary to S3.

    Args:
        event: Full pipeline state with preprocess, classify, and extract results.

    Returns:
        Summary of the pipeline execution.
    """
    preprocess = event.get("preprocess_result", {})
    classify = event.get("classify_result", {})
    extract = event.get("extract_result", {})

    document_id = preprocess.get("document_id")
    s3_bucket = preprocess.get("s3_bucket")

    if not isinstance(document_id, str) or not document_id:
        raise ValueError("Pipeline event must include a document_id.")
    if not isinstance(s3_bucket, str) or not s3_bucket:
        raise ValueError("Pipeline event must include an s3_bucket.")

    logger.info("Aggregating results for document: %s", document_id)

    summary = {
        "document_id": document_id,
        "document_type": classify.get("document_type", "unknown"),
        "classification_confidence": classify["classification_confidence"],
        "extracted_fields": extract.get("extracted_fields", {}),
        "extraction_confidence": extract["extraction_confidence"],
        "status": "completed",
    }

    result_key = f"results/{document_id}.json"
    get_s3_client().put_object(
        Bucket=s3_bucket,
        Key=result_key,
        Body=json.dumps(summary),
        ContentType="application/json",
    )
    logger.info("Wrote pipeline results to s3://%s/%s", s3_bucket, result_key)
    return summary
