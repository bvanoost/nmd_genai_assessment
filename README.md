# GenAI Document Processing Pipeline — Technical Assessment

**Time:** 90 minutes (setup not counted — clock starts at `terraform init`)

## What You're Building

A serverless document processing pipeline: S3 → EventBridge → Step Functions → Lambda + Bedrock → S3.

The infrastructure and pipeline skeleton are working. Your job is to **implement the three Bedrock functions**, deploy, test end-to-end, and answer discussion questions.

```
S3 (/uploads/)  →  EventBridge  →  Step Functions
                                      ├── Preprocess  (Lambda — reads S3)        ✅ working
                                      ├── Classify    (Lambda + Bedrock Haiku)   ← implement
                                      ├── Extract     (Lambda + Bedrock Haiku)   ← implement
                                      └── Aggregate   (Lambda → S3 /results/)   ← implement
```

All four Lambda functions share one Docker image pushed to ECR, with different handler entry points.

## Prerequisites

- Python 3.13+ with [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.13
- AWS CLI v2
- Docker
- Your AWS credentials (from the pwpush link in your email)

## Setup

**1. Fork and clone**

1. Go to [github.com/New-Math-Data/nmd_genai_assessment](https://github.com/New-Math-Data/nmd_genai_assessment)
2. Click **Fork** (top right) to create a copy under your GitHub account
3. Clone your fork:

```bash
git clone https://github.com/<your-username>/nmd_genai_assessment.git
cd nmd_genai_assessment
```

**2. Configure AWS**

```bash
aws configure --profile nmd-codescreen
# Enter: access key, secret key, region = us-west-2
AWS_PROFILE=nmd-codescreen aws sts get-caller-identity   # verify
```

**3. Fill in config files**

```bash
cp env.example .env
cp terraform/live/candidate/terraform.tfvars.example terraform/live/candidate/terraform.tfvars
```

Edit both files with your candidate name and application prefix (`nmd-genai-<your-name>`).

**4. Deploy infrastructure**

```bash
cd terraform/live/candidate
terraform init -backend-config="key=genai-assessment/brad-van-oosten"/terraform.tfstate"
AWS_PROFILE=nmd-codescreen terraform apply -var-file=terraform.tfvars
```

> The first `terraform apply` creates the ECR repo, S3 bucket, and Lambda functions. The Lambdas won't work until you build and push the Docker image.

**5. Build and push Docker image**

```bash
cd ../../..   # back to repo root
make docker-build
AWS_PROFILE=nmd-codescreen make docker-push
```

## Deliverables

### Bedrock Implementation

1. Implement `classify_document()` in `src/tasks/classify.py` — call Bedrock to classify the document type
2. Implement `extract_fields()` in `src/tasks/extract.py` — call Bedrock to extract structured fields
3. Implement `aggregate_results()` in `src/tasks/aggregate.py` — write results JSON to S3

### Deploy and Test

4. Rebuild and push: `make deploy` then `AWS_PROFILE=nmd-codescreen make update-lambdas`
5. Upload sample docs and verify the pipeline runs end-to-end
6. Answer discussion questions in `DISCUSSION.md` (shared section + your assigned track)

## After Making Code Changes

Rebuild and deploy the updated image:

```bash
make deploy                                     # builds + pushes Docker image
AWS_PROFILE=nmd-codescreen make update-lambdas  # tells Lambda to pull the new image
```

Upload a sample document to trigger the pipeline:

```bash
AWS_PROFILE=nmd-codescreen aws s3 cp \
  data/cybersecurity-advisory.json \
  s3://nmd-genai-<your-name>-documents/uploads/cybersecurity-advisory.json
```

## Verification

Check Step Functions in the AWS console, or:

```bash
# List executions
AWS_PROFILE=nmd-codescreen aws stepfunctions list-executions \
  --state-machine-arn $(cd terraform/live/candidate && terraform output -raw state_machine_arn) \
  --query 'executions[0].{status:status,start:startDate}'

# Check results in S3
AWS_PROFILE=nmd-codescreen aws s3 ls s3://nmd-genai-<your-name>-documents/results/
```

## Allowed Bedrock Model

Your credentials are scoped to **Claude Haiku** models only (e.g., `us.anthropic.claude-haiku-5-5`). The model ID is set via the `BEDROCK_MODEL_ID` environment variable in your Lambda functions.

Sonnet, Opus, and other model families are not available. Design your prompts for Haiku.

## What We're Evaluating

| Area | What we look for |
|---|---|
| **Bedrock implementation** | Prompt quality, API usage, JSON parsing, error handling |
| **Deployment** | Working end-to-end pipeline (Terraform → Docker → Lambda → S3 results) |
| **Discussion answers** | Depth of reasoning, real-world awareness, clear communication |
| **Git usage** | Atomic commits with descriptive messages, logical progression of work |

## Tips

- **Commit early and often.** We review your process, not just the end state.
- **Partial completion is fine.** Depth over breadth — a polished classify function beats three rushed ones.
- **Read the existing code.** `src/tasks/preprocess.py` and `src/common/aws.py` show the patterns to follow.
- **If you get stuck**, document what you tried and move on.

## Suggested Time

| Phase | Time |
|---|---|
| Implement Bedrock functions | 30 min |
| Deploy, test, iterate | 20 min |
| Discussion questions | 40 min |
| **Total** | **90 minutes** |
