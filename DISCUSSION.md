# Discussion Questions

Answer the **Shared Questions** section plus the **one track section** specified in your email (Solutions Architect OR Data Engineer). 

Aim for 2-4 sentences per answer unless otherwise noted. We value clarity and depth over length.

---

## Shared Questions (everyone answers)
### 1. Troubleshooting

If you could not complete the assessment or got stuck at any point, what went wrong and what did you try to troubleshoot?

I ran into several setup and deployment issues during the assessment. Docker repeatedly hung during `make deploy` without producing an error message, which took approximately 20 minutes to troubleshoot and was resolved by restarting Docker Desktop. I also could not run `make docker-push` without the required credentials, so I had to create them before proceeding. While troubleshooting these issues, I used ChatGPT to help diagnose the errors and continued implementing and pushing the three functions. I then encountered a Lambda deployment error, `":latest does not exist. Provide a valid source image."`, because the order of operations in the README was incorrect. Changing the deployment order resolved that issue. Finally, I could not retrieve the state machine’s output through the CLI or access the AWS console using the provided credentials. I therefore focused on completing the functions as thoroughly as possible, but was unable to verify their final outputs or the end-to-end results.

### 2. Proof of Completion

Paste the S3 URI to one of your result files (e.g., `s3://nmd-genai-<your-name>-documents/results/<document-id>.json`).

**Your answer:**
N/A could not get it to work =[

### 3. Prompt Engineering

How would you improve the classification prompt to handle ambiguous documents that could match multiple types? What techniques would you use to ensure consistent JSON output from the LLM?

**Your answer:**
I would improve the classification prompt by clearly defining each document type, including its distinguishing features and examples of documents that could fit multiple categories. I would add explicit tie-breaking rules, such as prioritizing the document’s primary purpose over incidental content, and specify whether a single best match or multiple labels are allowed. If there is insufficient evidence for a reliable decision, I would allow an “unknown” or “needs review” classification rather than forcing a guess. Alternatively, I would consider allowing multiple classifications when each meets a defined confidence threshold. For example, a document could be classified as both security and financial if there is sufficient evidence for both.

I would not assume that the LLM will consistently return valid JSON. In my implementation, I tried to handle this by removing any preamble from the response. To improve reliability, I would explicitly define the expected JSON structure in the prompt and validate the output before processing it. Additional pattern matching could help extract specific fields from malformed responses, but I would prefer schema validation and controlled retries over relying on regex alone.

### 4. Error Handling

How would you handle Bedrock throttling (429 errors) in a production pipeline? What retry strategy would you implement, and how would it interact with Step Functions' built-in error handling?

**Your answer:**
 I would use Step Functions as the primary retry layer, configuring its retry policy with a starting interval, that increases its wight timew with increasing try number, a maximum delay, and a limited number of attempts.


### 5. Enterprise Readiness

Assume a CTO prototyped this pipeline over a weekend using AI code assistants. It works for demos but needs to go to production for a Fortune 500 client.

Write a prioritized list of changes organized by:
1. **Must-fix before production** — what would block a launch?
2. **Should-fix in the first sprint** — what's important but not blocking?
3. **Nice-to-have for long-term maintainability** — what would you plan for later?

Consider security, error handling, observability, testing, CI/CD, and infrastructure hardening.

**Your answer:**
Must fix:
-verify the complete workflow since I could not
-handle failures reliably (fail loud and fast)
-validate classification output for distinct categories
-prevent duplicate processing
-add retries

should fix:
-more testing for borderline documents
-add logs for documents/ runtimes ect (possible dashboard)


nice to have:
-optimize cost/performance
-have a way to reprocess failed documents
-document operations with architecture diagrams, troubleshooting runbooks, and recovery procedures

### 4. Terraform — Adding a Pipeline Step

A new "validate" Lambda needs to be added to the pipeline between Extract and Aggregate. It will validate the extracted fields against a schema before writing results. List every file you'd need to change and what you'd add to each.

**Your answer:**
I would update the Python code, Terraform configuration, deployment workflow, and tests. In Python, I would add src/tasks/validate.py for schema validation and src/lambdas/validate/handler.py for the Lambda entry point

In Terraform, I would define the new Lambda resource and its CloudWatch log group in terraform/modules/lambda/main.tf, add any necessary variables in terraform/modules/lambda/variables.tf, and expose the Lambda ARN in terraform/modules/lambda/outputs.tf. I would then update terraform/modules/step-functions/state_machine.asl.json to insert the Validate state between Extract and Aggregate. I would also update the Step Functions module’s main.tf and variables.tf to accept the new Lambda ARN and grant the state machine permission to invoke it.

Finally, I would update terraform/live/candidate/main.tf to connect the new Lambda to the Step Functions module and update the Makefile to include it in the deployment and image-update workflow, if those updates are managed there. 

---

## Solutions Architect Track

*Answer this section only if your email specified Solutions Architect.*

### SA-1. Model Selection & Cost Architecture

This assessment restricts you to Claude Haiku. In a production system processing thousands of documents daily, how would you decide which model to use for classification vs. extraction? What factors (cost, latency, accuracy, token limits) would drive that decision? How would you implement cost attribution per client?

**Your answer:**

### SA-2. Security Review

A client wants to process PHI (protected health information) through this pipeline. What changes are needed to meet HIPAA requirements? Think about data at rest, data in transit, Bedrock's data handling policies, IAM scoping, and logging.

**Your answer:**

### SA-3. Multi-Tenancy

A client wants to offer this pipeline as a SaaS feature where each of their customers uploads documents. How would you isolate tenants? Consider S3 partitioning, IAM scoping, cost attribution, and noisy-neighbor protection.

**Your answer:**

### SA-4. Production Readiness Briefing

List the key points you'd convey to a client's VP of Engineering who approved this project but hasn't seen the implementation. What changes are needed before going to production, and how would you prioritize them?

**Your answer:**

---

## Data Engineer Track

*Answer this section only if your email specified Data Engineer.*

### DE-1. Data Quality & Validation

The pipeline trusts the LLM's JSON output without validation. How would you validate extracted fields against a schema? How would you handle extraction failures — retry, dead-letter queue, or flag for human review? What's your strategy?

**Your answer:**
I would validate every extraction against a strict schema before writing the final record trying to catch missing keys, incorrect types, invalid date formats, etc. I would reject or quarantine anything that fails validation instead of trusting the raw LLM output. For transient model or Bedrock failures, I would do a limited amount fo reties. For repeated failures or low-confidence outputs, I would route a human-review queue with metadata like document ID so that record can be investigated without blocking the whole pipeline.

### DE-2. Pipeline at Scale

This processes one document per Step Functions execution. Design a batch pipeline that handles 100,000 documents per day. What changes to the Step Functions architecture? Where would you parallelize, and where are the bottlenecks?

**Your answer:**
I would replace the one-document-per-execution model with a batch-oriented design using Step Functions Distributed Map or a queue-driven fan-out pattern, where each batch holds multiple documents and the Lambda workers process them in parallel while respecting Bedrock and Lambda concurrency limits. The main bottlenecks would be Bedrock rate limiting, network I/O to S3, and Lambda concurrency/timeout.

### DE-3. Observability & Data Lineage

How would you monitor this pipeline in production? What metrics, alerts, and dashboards would you build? A downstream team also needs to know which model version and prompt version produced each extraction. How would you track that lineage?

**Your answer:**
I would have the pipeline record metrics on documents processed, latency per stage, retries, failure rate, model cost, and output-validation failures, and I would alert on sustained queue growth, step failures, and unusually high latency or error rate. For lineage, every output record should include document ID, source bucket/key, model ID, model version, prompt version, schema version, timestamp, and Step Functions execution ID, and I would store that metadata alongside the extracted JSON in S3 or a metadata store so downstream teams can trace exactly what produced each result for ease of use or in a data warehouse if it were to be used for monitoring dashboards.

### DE-4. Caching & Deduplication

If the same document is uploaded twice, the pipeline currently processes it again at full cost. How would you implement caching or deduplication? Consider where in the pipeline to check, what to use as a cache key, and the tradeoffs of different storage options (DynamoDB, S3 metadata, Elasticache).

**Your answer:**
I would compute a content hash or canonical document hash at upload time and check it before invoking expensive model calls, which is the cheapest place to deduplicate because it avoids re-running the full pipeline. As for starage, A DynamoDB table with a conditional write is a good fit for a dedupe ledger because it gives atomicity and metadata like document ID, hash, status, and last-updated timestamp. S3 would be a simple and chaep options for small amounts of records but would be limited if large amounts of documents were used or if we wanted analysis built off of it. I would use Elasticache only when I need ultra-fast repeated lookups for very hot keys, but I’d avoid relying on it as the system of record because it is eventually consistent.