#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh  –  Build, push to ECR, and force-redeploy ECS for
#               C22-Mastery-Quiz-Tool
#
# Usage:
#   ./deploy.sh                  # build + push + redeploy
#   ./deploy.sh --build-only     # build & push, skip ECS redeploy
#   ./deploy.sh --redeploy-only  # skip build, just force new ECS deployment
#
# Prerequisites:
#   - AWS CLI configured (aws configure or environment variables)
#   - Docker running
#   - Terraform already applied (ECR repo and ECS service must exist)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
AWS_REGION="${AWS_REGION:-eu-west-2}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"

APP_NAME="c22-mastery-quiz-tool"
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"
ECS_CLUSTER="c22-mastery-quiz-cluster"
ECS_SERVICE="c22-mastery-quiz-service"

IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"

BUILD=true
REDEPLOY=true

# ── Argument parsing ───────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --build-only)    REDEPLOY=false ;;
    --redeploy-only) BUILD=false ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║        C22 Mastery Quiz Tool  –  Deploy              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo "  Region:    ${AWS_REGION}"
echo "  Account:   ${AWS_ACCOUNT_ID}"
echo "  ECR repo:  ${ECR_REPO}"
echo "  Tag:       ${IMAGE_TAG}"
echo "  Cluster:   ${ECS_CLUSTER}"
echo "  Service:   ${ECS_SERVICE}"
echo ""

# ── Build & Push ───────────────────────────────────────────────────────────────
if [ "$BUILD" = true ]; then
  echo "▶ Logging in to ECR..."
  aws ecr get-login-password --region "${AWS_REGION}" \
    | docker login --username AWS --password-stdin \
        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

  echo ""
  echo "▶ Building Docker image..."
  docker build \
    --platform linux/amd64 \
    -t "${APP_NAME}:${IMAGE_TAG}" \
    -t "${APP_NAME}:latest" \
    .

  echo ""
  echo "▶ Tagging and pushing to ECR..."
  docker tag "${APP_NAME}:${IMAGE_TAG}" "${ECR_REPO}:${IMAGE_TAG}"
  docker tag "${APP_NAME}:latest"       "${ECR_REPO}:latest"

  docker push "${ECR_REPO}:${IMAGE_TAG}"
  docker push "${ECR_REPO}:latest"

  echo ""
  echo "✅ Image pushed → ${ECR_REPO}:${IMAGE_TAG}"
fi

# ── Force ECS redeployment ─────────────────────────────────────────────────────
if [ "$REDEPLOY" = true ]; then
  echo ""
  echo "▶ Forcing new ECS deployment..."
  aws ecs update-service \
    --region "${AWS_REGION}" \
    --cluster "${ECS_CLUSTER}" \
    --service "${ECS_SERVICE}" \
    --force-new-deployment \
    --output text \
    --query "service.serviceName" > /dev/null

  echo ""
  echo "⏳ Waiting for ECS service to stabilise (this may take ~2 min)..."
  aws ecs wait services-stable \
    --region "${AWS_REGION}" \
    --cluster "${ECS_CLUSTER}" \
    --services "${ECS_SERVICE}"

  echo ""
  echo "✅ ECS service is stable."

  # Print the ALB URL from Terraform output
  if command -v terraform &>/dev/null && [ -d terraform ]; then
    ALB_DNS=$(terraform -chdir=terraform output -raw alb_dns_name 2>/dev/null || true)
    if [ -n "${ALB_DNS}" ]; then
      echo ""
      echo "🌐 App URL: http://${ALB_DNS}"
    fi
  fi
fi

echo ""
echo "🎉 Deploy complete!"
