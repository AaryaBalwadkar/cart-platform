# Cart Platform — complete DevOps exam guide

This is a manual, Windows-first runbook for the photographed case study. Prepare the tools and accounts before the timed exercise. During the exam, follow the task order and use the verification commands shown.

The sample asks for:

1. Git: initialize `cart-platform`, create `release-cart-v1`, commit `inventory.json`, merge into `main`, and create annotated tag `cart-v1.0.0`.
2. Jira: move `CART-10` and `CART-11` to Done, complete the active sprint, and review its progress report.
3. Jenkins: run a Declarative Pipeline with `Checkout Repo`, `Run Linter`, and `Docker Package`.
4. Docker: build `retail-cart:1.0` from Alpine so it serves `Shopping Cart Active`; run detached on `8083:80` and verify `docker ps`.
5. Kubernetes: run two `nginx:alpine` replicas labelled `tier=cart`, expose NodePort `30093`, and verify pods and service port.
6. IaC: Terraform creates `cart_endpoint.txt` with exactly `PORT=30093`; verify its contents with an Ansible ad-hoc command.

The app is deliberately tiny: a browser frontend plus a JSON backend that keeps cart items in memory. It is a lab demonstration, not a production shopping platform. Docker runs the custom Alpine frontend and Python backend. Kubernetes uses the required exact `nginx:alpine` image for its two frontend replicas, mounts the same frontend files from a ConfigMap, and sends API requests to a backend service.

## A. The flow and what connects

```text
Jira CART-10 / CART-11
        │ put issue key in a Git branch/commit when applicable
        ▼
Git local repo ── push ──► GitHub cart-platform
                              │ Jenkins reads the repository (manual Build Now)
                              ▼
                    One reusable Jenkins container
                    Checkout Repo → Run Linter → Docker Package
                              │ Docker socket
                              ▼
                     Docker Desktop engine
             retail-cart:1.0 :8083 → cart-backend:1.0 :5000

Docker Desktop Kubernetes: nginx:alpine × 2 → cart NodePort :30093
             Nginx /api proxy → backend ClusterIP :5000
                         ↑ kubectl port-forward
              Windows localhost:30093

Terraform container → cart_endpoint.txt → Ansible ad-hoc check
```

Jira/GitHub integration links issue keys to development activity, but it does not necessarily transition tickets automatically. Jenkins is one global local service reused for projects; configure this project's job in its UI. The pipeline is pasted into that UI; this project does not need a Jenkins server configuration or a Jenkinsfile.

## B. One-time preparation before exam day

### 1. Install/check Docker Desktop and Git

1. Install Git for Windows if needed. Verify in PowerShell:

   ```powershell
   git --version
   ```

2. Install Docker Desktop with the WSL 2 backend. Start it and wait until its engine reports running.
3. Verify:

   ```powershell
   docker version
   docker run --rm hello-world
   docker compose version
   ```

   `docker version` must show both Client and Server. If Server is missing, start Docker Desktop before continuing.
4. `kubectl` is included with Docker Desktop. Verify:

   ```powershell
   kubectl version --client
   ```

### 2. Prepare Docker Desktop Kubernetes

Use Docker Desktop's built-in Kubernetes cluster; no second cluster is needed.

1. In Docker Desktop, enable Kubernetes under **Settings → Kubernetes**, apply the change, and wait for the cluster to report ready.
2. In PowerShell, select and check the Docker Desktop context:

   ```powershell
   kubectl config use-context docker-desktop
   kubectl get nodes
   ```

3. Continue only after the node reports `Ready`.

For reliable access from Windows, the Kubernetes section below uses `kubectl port-forward`. This forwards local port `30093` to the Service's port `80`; the Service still has the exam-required NodePort `30093`. This is a temporary local tunnel, not a host port mapping created by Docker Desktop.

### 3. Create the GitHub repository and connect Jira (if permitted)

1. On GitHub, create an empty repository named `cart-platform`. Do not initialize it with a README or `.gitignore`.
2. In Jira Cloud, use **Apps → Explore more apps** and install the official **GitHub for Jira** app if it is not already installed.
3. Connect the GitHub organization/repository from the app setup. This may require Jira site-admin and GitHub organization permissions; ask the instructor/admin if you lack them.
4. Include issue keys such as `CART-10` in commit messages, for example `CART-10 add cart inventory`. If connected, confirm the Jira issue's development panel shows the commit.
5. The integration links development activity; move issues to Done in Jira separately as required.

If app installation is not allowed, do GitHub and Jira as separate demonstrations. Do not spend the exam trying to obtain admin permissions.

### 4. Start one reusable Jenkins server and prepare it

This is one shared Jenkins container for your laptop, not one server per project. Do the setup once before the exam and keep its named data volume.

> **Local practice only:** mounting the Docker socket gives Jenkins broad control of Docker Desktop and can effectively provide host-level control. The following lab-only command runs Jenkins as root to avoid socket permission problems. Do not use this setup for a shared/production Jenkins server, and never expose Docker's unauthenticated TCP daemon.

Start Docker Desktop, then run once from PowerShell:

```powershell
docker volume create jenkins_home
docker run -d --name jenkins --restart unless-stopped --user 0:0 -p 8081:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts-jdk21
docker ps
```

Open **http://localhost:8081**. Get the one-time unlock password:

```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

In the Jenkins UI:

1. Unlock Jenkins with that password.
2. Choose **Install suggested plugins**; confirm the **Pipeline** and **Git** plugins are available under **Manage Jenkins → Plugins**.
3. Create the administrator user and save the login securely.
4. Complete setup and confirm the dashboard opens at `http://localhost:8081`.

Install the commands needed by the global Jenkins agent once from PowerShell:

```powershell
docker exec -u 0 jenkins bash -lc "apt-get update && apt-get install -y git python3 python3-venv python3-pip docker.io"
docker exec jenkins git --version
docker exec jenkins python3 --version
docker exec jenkins docker version
```

Docker version should show Client and Server. Docker CLI inside Jenkins uses the mounted Docker Desktop socket. Keep this same container; stopping/starting it preserves these packages, and the `jenkins_home` volume preserves jobs/plugins/account. Do not remove the container or volume.

### 5. Prepare Terraform and Ansible in a tools container

No Terraform or Ansible Windows install is needed. Build the tools image once during preparation:

```powershell
cd "F:\SEM_7\Devops_Lab\ESE Practice\cart-platform"
docker compose -f .\tools\compose.yaml build
```

The image contains pinned Terraform and Ansible CLI versions. Terraform provider downloads and state live in this project folder; `.gitignore` excludes the state.

## C. Exam execution guide

Use PowerShell in this project folder unless a step says to use a browser:

```powershell
cd "F:\SEM_7\Devops_Lab\ESE Practice\cart-platform"
```

### 1. Git and GitHub: release branch, merge, annotated tag

Create the repository in GitHub first as described above. Replace `YOUR-NAME` with your GitHub username or organization:

```powershell
git init -b main
git add README.md .gitignore
git commit -m "chore: initialize cart platform"
git remote add origin https://github.com/YOUR-NAME/cart-platform.git
git push -u origin main

git switch -c release-cart-v1
git add .
git commit -m "CART-10 add cart inventory and deployment assets"
git push -u origin release-cart-v1

git switch main
git merge --no-ff release-cart-v1 -m "merge release-cart-v1"
git tag -a cart-v1.0.0 -m "Release cart-v1.0.0"
git push origin main
git push origin cart-v1.0.0
```

Confirm `main`, `release-cart-v1`, and tag `cart-v1.0.0` appear on GitHub. An annotated Git tag is different from a branch: the branch moves as new commits are added; the tag marks the release commit.

If Git asks for identity before committing, configure it once:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

### 2. Jira: close the specified sprint work

1. Open the Jira project/board and active sprint.
2. Transition **CART-10** and **CART-11** to **Done** using the workflow's status action (or drag each card to Done).
3. Open the sprint **Reports → Sprint progress/Burndown** report and review it.
4. Complete the active sprint as the question requests. If completing hides the report, review it first.
5. If the GitHub app is connected, open an issue and show the linked commit/development panel. Jira still needs the manual status transitions above.

### 3. Jenkins: run the three-stage Declarative Pipeline

The Jenkins server is already set up; do not create another one. Ensure Docker Desktop and the existing Jenkins container are running:

```powershell
docker start jenkins
```

Open **http://localhost:8081** and sign in. Create a job through the UI:

1. Select **New Item**, enter `cart-platform-pipeline`, choose **Pipeline**, then **OK**.
2. In the **Pipeline** section, select **Pipeline script** for **Definition**.
3. Paste the Declarative Pipeline below. Replace `YOUR-NAME`. For a public GitHub repository, no credentials are needed. For a private repo, add a read-only GitHub credential in Jenkins and add `credentialsId: 'YOUR-CREDENTIAL-ID'` to the `git` step.
4. Save and select **Build Now** after `main` has the release merge.
5. Open **Console Output** and verify each named stage is successful.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YOUR-NAME/cart-platform.git'
            }
        }

        stage('Run Linter') {
            steps {
                sh 'python3 -m json.tool inventory.json > /dev/null'
                sh 'python3 -m unittest discover -s backend/tests -p "test_*.py"'
            }
        }

        stage('Docker Package') {
            steps {
                sh 'docker build -t retail-cart:1.0 ./frontend'
                sh 'docker build -t cart-backend:1.0 ./backend'
            }
        }
    }
}
```

The linter stage parses the inventory JSON and runs the backend unit tests. The package stage builds both the Alpine frontend and Python backend images. If checkout fails, check the public URL/credential. If Docker reports it cannot connect to the daemon, verify `docker exec jenkins docker version`; do not expose a TCP daemon.

### 4. Docker: build and launch the frontend and backend

From the project root, build both images and start the microservice detached:

```powershell
docker compose up --build -d
docker ps
```

Compose creates image `retail-cart:1.0` from `frontend\Dockerfile` (based on Alpine) and `cart-backend:1.0` from `backend\Dockerfile`. It publishes the frontend on `8083:80`; the frontend reaches the backend over the Compose network on port 5000. `docker ps` should show both containers running and the frontend port mapping.

Open **http://localhost:8083**. The page should show **Shopping Cart Active** and a cart form. Add an item to verify the UI calls the backend API through Nginx. You can inspect the API response via the frontend proxy:

```powershell
Invoke-RestMethod http://localhost:8083/api/cart
```

The frontend container logs the required message when it starts:

```powershell
docker logs retail-cart
```

`docker ps` should show `0.0.0.0:8083->80/tcp` (or equivalent). To stop both app containers:

```powershell
docker compose down
```

### 5. Kubernetes: frontend and backend, two frontend replicas, localhost port-forward

The Kubernetes configuration provides a backend API with an internal `ClusterIP` service and exactly two frontend replicas using the required `nginx:alpine` image, label `tier=cart`, and NodePort `30093`. The frontend uses the same HTML and Nginx proxy configuration as the Docker deployment.

Select Docker Desktop Kubernetes and create/update a ConfigMap from the frontend source files:

```powershell
kubectl config use-context docker-desktop
kubectl get nodes
kubectl create configmap cart-frontend-files --from-file=default.conf=.\frontend\nginx.conf --from-file=index.html=.\frontend\index.html --dry-run=client -o yaml | kubectl apply -f -
```

The backend image should already exist from the Docker task. Apply the manifests and check both tiers:

```powershell
kubectl apply -f .\kubernetes\cart.yaml
kubectl rollout status deployment/backend
kubectl rollout status deployment/cart
kubectl get pods -l tier=cart -o wide
kubectl get pods -l app=cart-backend -o wide
kubectl get service cart
kubectl get service backend
```

Expected: two Ready frontend pods labelled `tier=cart`, a Ready backend pod, frontend service `cart` reporting `80:30093/TCP`, and backend service `backend` reporting `5000/TCP`.

In a dedicated PowerShell window, port-forward the frontend service and leave the command running:

```powershell
kubectl port-forward service/cart 30093:80
```

In a second PowerShell window, verify access:

```powershell
(Invoke-WebRequest -Uri http://localhost:30093 -TimeoutSec 10).StatusCode
```

Expected HTTP status is `200`. Open **http://localhost:30093** and add an item: the page should load and show the updated cart. Nginx in a frontend pod proxies `/api/` requests to the backend service at `backend:5000`. The Service remains a NodePort on `30093`; `kubectl port-forward` provides reliable localhost access without changing the cluster. Keep the first PowerShell window open while testing; press **Ctrl+C** there to stop the forward.

This deploys both sides of the microservice while preserving the exam's exact frontend image, replica count, label, NodePort, and pod/service verification.

If the pods are not Ready, inspect only the relevant resources:

```powershell
kubectl describe pods -l tier=cart
kubectl logs deployment/cart
kubectl logs deployment/backend
kubectl get endpoints cart
kubectl get endpoints backend
```

If `localhost:30093` does not respond, confirm the port-forward command is still running and the Service has a ready endpoint:

```powershell
kubectl get endpoints cart
kubectl get service cart
```

Port-forwarding temporarily occupies local port `30093`. If Windows reports that it is already in use, stop the process using that port before starting the forward; keep the exam-required NodePort value unchanged.

### 6. Terraform and Ansible ad-hoc verification

Apply Terraform using the prepared tools container:

```powershell
docker compose -f .\tools\compose.yaml run --rm tools terraform -chdir=terraform init
docker compose -f .\tools\compose.yaml run --rm tools terraform -chdir=terraform validate
docker compose -f .\tools\compose.yaml run --rm tools terraform -chdir=terraform apply
```

Inspect the plan and type `yes` when asked. Terraform creates `cart_endpoint.txt` at the project root. Confirm the exact content:

```powershell
Get-Content .\cart_endpoint.txt
```

Expected:

```text
PORT=30093
```

Run an Ansible **ad-hoc** `command` module to assert that exact line exists:

```powershell
docker compose -f .\tools\compose.yaml run --rm tools ansible localhost -i "localhost," -c local -m command -a "grep -Fx PORT=30093 /workspace/cart_endpoint.txt"
```

Expected output contains `PORT=30093` and `SUCCESS`. The ad-hoc command checks file contents; it does not run a playbook, as the question specifically requests an ad-hoc module.

## D. Final 60–75 minute checklist

The photographed paper allows **1 hour 15 minutes**. Complete tool installation, container image builds, account setup, and the Jira/GitHub connection before the exam.

| Suggested time | Task | Demonstration evidence |
|---|---|---|
| 0–10 min | Git branch, commit, merge, annotated tag, push | GitHub branches, main history, tag |
| 10–17 min | Jira tickets and sprint report | CART-10/CART-11 Done; sprint completed/report shown |
| 17–30 min | Jenkins | Three pipeline stages green; console output |
| 30–38 min | Docker | `docker ps`; browser on `localhost:8083` |
| 38–53 min | Kubernetes | Two frontend replicas, backend pod, `80:30093/TCP`, cart UI on `localhost:30093` |
| 53–68 min | Terraform and Ansible | `cart_endpoint.txt` exact value and ad-hoc `SUCCESS` |
| 68–75 min | Final review | Re-show requested outputs |

## E. Cleanup after practice (optional)

Stop the Docker Compose app and remove only the lab Kubernetes resources:

```powershell
docker compose down
kubectl delete -f .\kubernetes\cart.yaml
kubectl delete configmap cart-frontend-files
```

Stop Jenkins while preserving its saved configuration:

```powershell
docker stop jenkins
```

Destroy the local Terraform-managed file/state only if you want to reset that task:

```powershell
docker compose -f .\tools\compose.yaml run --rm tools terraform -chdir=terraform destroy
```

Do not remove the `jenkins_home` Docker volume; it contains your reusable Jenkins account, plugins, and job.

## Official references

- [Docker Desktop Kubernetes](https://docs.docker.com/desktop/use-desktop/kubernetes/)
- [Kubernetes Services and NodePort](https://kubernetes.io/docs/concepts/services-networking/service/)
- [kubectl port-forward](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)
- [Jenkins in Docker](https://www.jenkins.io/doc/book/installing/docker/)
