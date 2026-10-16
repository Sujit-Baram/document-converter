# Document Converter Starter

A small FastAPI service that converts UTF-8 `.txt` uploads into PDF files. Includes a Dockerfile, tests, and a Jenkins pipeline that builds, tests, and pushes the image to Amazon ECR.

## Scope

This starter supports **TXT to PDF only**. It is not a full Office/PDF conversion suite.

AWS values are prefilled from your project context:
- Region: `us-east-2`
- AWS account: `533267015112`
- ECR repository: `document-converter/dev`

Confirm these match your environment before running Jenkins.

## Endpoints

- `GET /` — service information
- `GET /health` — ALB health check, returns HTTP 200
- `GET /docs` — interactive API documentation
- `POST /convert/txt-to-pdf` — multipart upload field `file`, `.txt` only, up to 5 MB

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Test health:

```bash
curl -i http://localhost:8080/health
```

Convert a file:

```bash
curl -X POST http://localhost:8080/convert/txt-to-pdf -F "file=@sample.txt" -o sample.pdf
```

## Docker

```bash
docker build -t document-converter:local .
docker run --rm -p 8080:8080 document-converter:local
```

## Jenkins prerequisites

The Jenkins agent needs Git, Python 3, Docker Engine, AWS CLI, network access to ECR, and an IAM role or securely configured AWS credentials. The IAM identity needs ECR push permissions for `document-converter/dev`.

Create a Jenkins Pipeline job pointing to this Git repository and set script path to `Jenkinsfile`.

The Jenkinsfile runs tests, builds the image, and pushes the build-number tag plus `latest`. Do not store AWS access keys in the Jenkinsfile.

## Deploy to the existing EC2 Auto Scaling Group

The pipeline does **not** automatically run Terraform. Your launch template's User Data embeds the image URI, so changing the image requires a Terraform launch-template update and an Auto Scaling instance refresh.

After a successful build, copy the exact image URI printed in `Deployment Handoff`, such as:

`533267015112.dkr.ecr.us-east-2.amazonaws.com/document-converter/dev:42`

Update `app_image` in `environments/dev/terraform.tfvars` to that URI, then run from the dev environment:

```bash
terraform plan -out=tfplan
```

Review the plan and confirm the image exists and only intended changes are included. Then:

```bash
terraform apply tfplan
```

Verify the new instances start the container and the ALB target group reports `healthy`. Do not apply until the Ubuntu User Data template is correct, the EC2 role can pull from ECR, and `/health` returns HTTP 200.

## Production hardening

- Configure HTTPS on the ALB.
- Use immutable version tags for releases.
- Add dependency/container vulnerability scanning.
- Add application authentication, authorization, request limits, and robust upload validation.
- Store credentials in Secrets Manager; never commit secrets.
- Implement and test additional conversion formats explicitly if required.
