<!-- omit in toc -->
# Project: Hive Box

Almost everyone loves honey, and appreciate the role that bees play for the planet! Because [bees are essential to people and planet](https://www.unep.org/news-and-stories/story/why-bees-are-essential-people-and-planet).

For that reason, this project will be for the bees! I will utilize the technology and open source software to build an API to track the environmental sensor data from [openSenseMap](https://opensensemap.org/), a platform for open sensor data in which everyone can participate.

<!-- omit in toc -->
## ToC

- [Goal](#goal)
- [Phase 1](#phase-1)
  - [1.1 Tools](#11-tools)
  - [1.2 Code](#12-code)
  - [1.3 Containers](#13-containers)
  - [1.4 Testing](#14-testing)
- [Phase 2](#phase-2)
  - [2.1 Tools](#21-tools)
  - [2.2 Code](#22-code)
  - [2.3 Containers](#23-containers)
  - [2.4 Continuous Integration](#24-continuous-integration)
  - [2.5 Testing](#25-testing)
- [Phase 3](#phase-3)
  - [3.1 Tools](#31-tools)
  - [3.2 Code](#32-code)
  - [3.3 Containers](#33-containers)
  - [3.4 Continuous Integration](#34-continuous-integration)
  - [3.5 Continuous Delivery](#35-continuous-delivery)
- [Phase 4](#phase-4)
  - [4.1 Tools](#41-tools)
  - [4.2 Code](#42-code)
  - [4.3 Containers](#43-containers)
  - [4.4 Infrastructure as Code](#44-infrastructure-as-code)
  - [4.5 Continuous Integration](#45-continuous-integration)
  - [4.6 Continuous Delivery](#46-continuous-delivery)
- [Phase 5](#phase-5)

## Goal

The goal of this project is to build a scalable RESTful API around [openSenseMap](https://opensensemap.org/) but customized to help beekeeper with their chores. The API output should be in JSON. You will start with a basic implementation, then extend the whole system to handles thousands of requests per second. But always remember, every decision has a cost.

You can get senseBox IDs by checking the [openSenseMap](https://opensensemap.org/) website. Use 3 senseBox IDs close to each other (I used this one [5eba5fbad46fb8001b799786](https://opensensemap.org/explore/5eba5fbad46fb8001b799786) as starting point). 

---


## Phase 1

### 1.1 Tools

- Git
- VS Code
- Docker

### 1.2 Code

- Create GitHub repository for the project.
- Implement the code requirements.

**Requirements:**

- Create a function that print current app version. It should print the version then exit the application.
- Use [Semantic Versioning](https://semver.org/) for the app version starting with `v0.0.1`.

### 1.3 Containers

- Create Dockerfile for the project.
- Build the Docker image and run it locally.

### 1.4 Testing

- Locally, run the app container and ensure that it returns the correct value.

---

## Phase 2

### 2.1 Tools

- [Hadolint](https://github.com/hadolint/hadolint) **and** [VS Code hadolint extension](https://marketplace.visualstudio.com/items?itemName=exiasr.hadolint)
- [Pylint](https://pypi.org/project/pylint/) **and** [VS Code Pylint extension](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint)

### 2.2 Code

- Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for Git commits.
- Familiarize yourself with [openSenseMap API](https://docs.opensensemap.org/).
- Implement the code requirements (Hint: [Flask Quickstart](https://flask.palletsprojects.com/en/2.3.x/quickstart/) or [FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/)) .
- Write unit tests for all endpoints.

**Requirements:**

**Version:**
- Endpoint: `/version`
- Parameters: No parameters.
- Requirements:
  - Returns the version of the deployed app.

**Temperature:**
- Endpoint: `/temperature`
- Parameters: No parameters.
- Requirements:
  - Return current average temperature based on all senseBox data.
  - Ensure that the data is no older 1 hour.

### 2.3 Containers

- Apply Best Practices for containers.

### 2.4 Continuous Integration

- Create a GitHub Actions workflow for CI.
- Add step to lint code and Dockerfile.
- Add step to build the Docker image.
- Add step to unit tests.
- Setup [OpenSSF Scorecard GitHub Action](https://securityscorecards.dev/#using-the-github-action) and fix any issues reported by it.

### 2.5 Testing

- In the CI pipeline, call the `/version` endpoint and ensure that it returns the correct value.

---

## Phase 3

### 3.1 Tools

- Kind
- Kubectl

### 3.2 Code

- Implement the code requirements.
- Write integration test (Hint: [3 ways to test your API with Python](https://opensource.com/article/21/9/unit-test-python)).

**Requirements:**

**General:**
- The senseBox should be configurable via env vars.

**Metrics:**
- Endpoint: `/metrics`
- Parameters: No parameters.
- Requirements:
  - Returns default Prometheus metrics about the app.

**Temperature:**
- Endpoint: `/temperature`
- Parameters: No parameters.
- Requirements:
  - Add "status" field based on the temperature average value.
    - Less than 10: Too Cold
    - Between 11-36: Good
    - More than 37: Too Hot

### 3.3 Containers

- Create KIND config to run with Ingress-Nginx.
- Create Kubernetes core manifests to deploy the application.

### 3.4 Continuous Integration

- Run code integration tests.
- Run SonarQube for code quality, security and static analysis (Hint: [Use SonarQube Quality Gate check](https://github.com/marketplace/actions/sonarqube-quality-gate-check) action, also consider [Semgrep](https://github.com/semgrep/semgrep)).
- Run Terrascan for Kubernetes manifest misconfigurations and vulnerabilities (Hint: [Terrascan GitHub Action](https://github.com/marketplace/actions/terrascan-iac-scanner)).
- Apply Best Practices for CI (Hint: [10 CI/CD Best Practices for DevOps Success](https://codefresh.io/learn/ci-cd/10-ci-cd-best-practices-for-devops-success/)).

### 3.5 Continuous Delivery

- Create a GitHub Actions workflow for CD.
- Add step to release by pushing a versioned Docker image to a container registry (Hint: [Use GitHub Container registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)).

---

## Phase 4

### 4.1 Tools

- Kind
- Kubectl

### 4.2 Code

- Implement the code requirements.

**Requirements:**

**General:**
- Add a caching layer using Memcached or etcd.

**Metrics:**
- Endpoint: `/metrics`
- Parameters: No parameters.
- Requirements:
  - Extend the Prometheus metrics by adding custom metrics based on the code logic.

**Readyz:**
- Endpoint: `/readyz`
- Parameters: No parameters.
- Requirements:
  - Returns HTTP 200 unless:
    - 50% + 1 of the configured senseBoxes are not accessible.
    - AND caching content is older than 5 min.

### 4.3 Containers

- Create a Helm chart for the application (Hint: [Awesome Helm List](https://github.com/cdwv/awesome-helm)).
- Create Kustomize manifests for the infrastructure resources like Memcached or etcd (Hint: [Awesome Kustomize List](https://github.com/DevOpsHiveHQ/awesome-kustomize)).
- Review Kubernetes Security Best Practices (Hint: [Kubernetes Security Best Practices with tips for the CKS exam](https://tech.aabouzaid.com/2022/07/kubernetes-security-best-practices-with-tips-for-the-cks-exam.html)).
- Configure the Kubernetes app manifest to use `/readyz` as a readiness probe.

### 4.4 Infrastructure as Code

- Deploy Grafana agent to collect logs and metrics (Hint: Create [Grafana Cloud](https://grafana.com/products/cloud/) free account to Use Loki and Grafana).
<!-- - Create a Kubernetes cluster using Terraform IaC (Hint: Use free tier from any Cloud provider). -->

### 4.5 Continuous Integration

- Run KIND cluster, deploy the app and infrastructure, then run the End-to-End test.

### 4.6 Continuous Delivery

- Apply Best Practices for CD.

---

<!-- ## Phase 5

This phase a free-style user-defined enhancements which means the enhancements could be related to any part of the project.

Here are some suggestions:

- Build Multi-environment Kubernetes clusters (Dev, Stage, and Prod) with Terraform and Kustomize.
- Use [TestKube](https://testkube.io/) for better testing execution.
- Automate dependency updates with [Dependabot](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide).
- Deploy the application in Declarative GitOps style using [Argo CD](https://argo-cd.readthedocs.io/en/stable/getting_started/).
- Develop a Kubernetes Operator to handle the app operations (Hint: [Introduction to Kubernetes Operators](https://tech.aabouzaid.com/2020/03/introduction-to-kubernetes-operators-presentation.html)). -->