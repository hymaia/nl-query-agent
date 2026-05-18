# NL Query Agent

Agent de requêtage en langage naturel sur AWS Glue Data Catalog, propulsé par FastAPI, LangGraph et Bedrock Claude Sonnet.

## Prérequis

Outils à installer :
- uv version >= 0.5.7
- Python version 3.13
- Terraform version >= 1.15.1
- Docker
- kubectl
- helm version >= 3.x
- ArgoCD CLI (optionnel)

## Installer les dépendances

```bash
uv venv
uv sync
```

## Lancer l'application en local

Créez un fichier `.env` à la racine du projet :

```bash
AWS_REGION=eu-west-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5
BEDROCK_MAX_TOKENS=4096
GLUE_DATABASE=my_glue_database
ATHENA_OUTPUT_BUCKET=s3://my-athena-results-bucket/prefix/
ATHENA_WORKGROUP=primary
APP_ENV=development
LOG_LEVEL=DEBUG
APP_PORT=8000
```

Buildez et lancez le conteneur :

```bash
docker build -t nl-sql-agent .
docker run --env-file .env -p 8000:8000 nl-sql-agent
```

L'API est accessible sur `http://localhost:8000`. La documentation Swagger est disponible sur `http://localhost:8000/docs`.

## Tester

```bash
uv run pytest
```

## Déployer

### Prérequis AWS

Avant le premier déploiement, activez le modèle Anthropic Claude Sonnet dans la console AWS Bedrock → Model access, ou via AWS CLI :

```bash
aws bedrock put-foundation-model-entitlement \
  --model-id anthropic.claude-sonnet-4-5 \
  --region eu-west-1
```

### Déployer l'infra manuellement

Authentifiez-vous à votre compte AWS et lancez ces commandes :

```bash
cd infra
terraform init
terraform plan
terraform apply
```

Le `terraform apply` génère automatiquement le fichier `helm/values.yaml` avec les valeurs de l'infrastructure (URL ECR, ARN du role IAM, etc.).

Si besoin vous pouvez renseigner les variables terraform dans un fichier `infra/terraform.tfvars` :

```hcl
data_platform_role_name = "<DATA_PLATFORM_ROLE_NAME>"
glue_database           = "<GLUE_DATABASE>"
athena_output_bucket    = "<ATHENA_OUTPUT_BUCKET>"
athena_workgroup        = "<ATHENA_WORKGROUP>"
ingress_host            = "<INGRESS_HOST>"
certificate_arn         = "<CERTIFICATE_ARN>"
github_org              = "<GITHUB_ORG>"
```

**> ⚠️ Ne commitez pas `infra/terraform.tfvars`, il n'est que pour vous !!**

### CI/CD

À chaque commit sur `main`, GitHub Actions :

1. Build et pousse l'image Docker sur ECR avec le SHA du commit comme tag :
   <ECR_REGISTRY>/nl-sql-agent:a1b2c3d4e5f6...
2. Met à jour le tag dans `dev-argo-app.yaml` sur la branche orpheline `env/dev`
3. ArgoCD détecte le changement et synchronise automatiquement le cluster

Le SHA du commit comme tag garantit une traçabilité totale — depuis un pod Kubernetes vous pouvez remonter au commit exact qui a produit l'image :

```bash
# retrouver le tag de l'image qui tourne
kubectl get pod <pod-name> -n nl-sql-agent-dev -o jsonpath='{.spec.containers[0].image}'
```

### Construire et pousser l'image

L'image est buildée et poussée automatiquement sur ECR à chaque push sur `main` via GitHub Actions.

### Déployer sur Kubernetes via ArgoCD

La branche orpheline `env/dev` contient la ressource ArgoCD `dev-argo-app.yaml` qui pointe sur le chart Helm de `main`. ArgoCD se synchronise automatiquement à chaque mise à jour de cette branche.

### Vérifier le déploiement

```bash
kubectl get pods -n nl-sql-agent-dev
kubectl logs -f deployment/nl-sql-agent -n nl-sql-agent-dev
```

## Tester l'API déployée

```bash
curl -X POST https://nlq-agent.example.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Combien de lignes dans la table clients ?"}'
```

## Architecture

L'agent reçoit une question en langage naturel, interroge le Glue Data Catalog pour découvrir le schéma, génère une requête SQL via Bedrock Claude Sonnet, l'exécute sur Athena et retourne le résultat accompagné d'une explication.

```
User (NL query)
      ↓
FastAPI
      ↓
LangGraph (orchestration)
      ↓
Bedrock Claude Sonnet (NL → SQL)
      ↓
Amazon Athena → AWS Glue Data Catalog
      ↓
Résultat + explication
```
