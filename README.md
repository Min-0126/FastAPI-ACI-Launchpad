# Fast API -> Docker -> Azure (ACR + ACI)

>Use Docker and Azure to deploy a FastAPI app.
>Build a container image using Docker and copy to Azure Container Registry (ACR), run on Azure Container Instances (ACI), reachable at http://<FQDN>:8000

## Features

+ **Containerized App**: Reproducible FastAPI image with uvicorn
+ **Private Registry**: Store images in ACR (azplacr.azurecr.io)
+ **Serverless Container**: Run on ACI with a public DNS label
+ **CMD work**: All commands tested from cmd.exe
+ **Straightforward troubleshooting**: Logs provider registration, auth checks

## Workflow
1. Develop FastAPI
2. Build Docker image locally
3. Push Docker image to ACR
4. Run the image on ACI (port 8000)
5. Access via http://<FQDN>:8000

>Fast API is a modern, high-performance Python web framework designed for building APIs

## Requirements
+ Windows with **Docker Desktop** and **Git**
+ **Azure subscription** & **Azure CLI**
+ **ACR**
+ Outbound Internet access

## Code and Project Structure

```
.
├─ app.py

├─ requirements.txt

└─ Dockerfile
```

### app.py
```python
# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hello from Dockerized Python!")

if __name__ == "__main__":
    server = HTTPServer(("", 8000), Handler)
    print("Serving on port 8000")
    server.serve_forever()
```

### Dockerfile
```dockerfile
# Dockerfile, Python 3.12 slim image
FROM python:3.12-slim

#Working Directory
WORKDIR /app

#File copy
COPY app.py .

#Port exposure
EXPOSE 8000

#App excution
CMD ["python", "app.py"]
```

## ACR Setup & Push

**Create ACR (Portal)**: New **Container Registry**, name *azplacr*, **Basic**, region **Korea Central

**Enable Admin user**: ACR -> **Access keys** -> **Admin user** = **Enable**

**Login, tag, push**:
```cmd
docker login azplacr.azurecr.io -u <ACR Username> -p "<ACR Password>"
docker tag jongm/azp1:1 azplacr.azurecr.io/azp1:1
docker push azplacr.azurecr.io/azp1:1
```
> ACR Username and ACR Password should be kept secret

**Verify tag exists**
```cmd
az acr repository show-tags -n azplacr --repository azp1 -o table
```
> Expected result is 1 and 
> Tag is used for tracking

## ACI Deployment

**Provider Registration** :
```cmd
az provider register --namespace Microsoft.ContainerInstance
```

**Variables**:
```cmd
set RG=azp1
set LOC=koreacentral
set ACI=azp1-aci
set DNS=azp1demo12345 
set ACR_SERVER=azplacr.azurecr.io
set REPO=azp1
set TAG=1
```

+ RG is the Azure Resource Group name. All related resources are in there
+ LOC is the Azure region where you create a resource
+ ACI is the Azure Container Instance container group name
+ DNS is a public DNS label for ACL. Must be globally unique.
+ ACR_SERVER is the ACR login server, which is the registry endpoint
+ REPO is the repository name in ACR (folder for image tags)
+ TAG is an image tag (1 in this example)

**Resource group**:
```cmd
az group create -n %RG% -l %LOC%
```
> A resource group is a group of resources

**Create ACI**:
```cmd
az container create -g %RG% -n %ACI% --location %LOC% ^
  --image %ACR_SERVER%/%REPO%:%TAG% ^
  --os-type Linux --cpu 1 --memory 1 ^
  --ports 8000 ^
  --dns-name-label %DNS% ^
  --registry-login-server %ACR_SERVER% ^
  --registry-username <ACR Username> ^
  --registry-password "<ACR Password>"
```

> ACI is Azure Container Instance, which is a PaaS service that runs individual containers
> in Azure without managing infrastructure (no need OS)

**Get FQDN & Test**:
```cmd
for /f "delims=" %F in ('az container show -g %RG% -n %ACI% --query "ipAddress.fqdn" -o tsv') do set FQDN=%F
echo %FQDN%
curl http://%FQDN%:8000
```

>FQDN is a Fully Qualified Domain Name is the complete and unambiguous address for a specific resource, 
>like a website or server, on the internet

## Common Troubleshooting

1. **Inaccesible Image** (ACI can't pull from ACR)
  + Confirm tag exists
  + Allow public access
  + Pass credentials correctly
  + Sanity check locally

2. *az* is not recongnized
  + Use full path or add to PATH

Call *az* by full path and set handy variables
```cmd
"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" --version
set "AZ=C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
"%AZ%" login
```

Use the *%AZ%* variables for all Azure commands
```cmd
"%AZ%" acr update -n azplacr --admin-enabled true
"%AZ%" acr credential show -n azplacr ...
"%AZ%" container create -g azp1 -n azp1-aci ...
```

3. MissingSubscriptionRegistration
  + Register provider: *az provider register --namespace Microsoft.ContainerInstance*
  + Retry *az container* create after it's **Registered**

4. Smoke Test
    + Local smoke
```cmd
GET http://localhost:8000/healthz
```
If answer is 200 -> Success

## Security
+ Keep secrets (ACR password and API keys) out of source control
+ Consider **private networking** and **HTTPS** termination

## Author
**Jongmin Kim (Min)**

email: minha0126@proton.me

## Resources
+ [Fundamentals and Deployment Docker](https://www.44bits.io/ko/post/easy-deploy-with-docker)
+ [az is not recognized](https://learn.microsoft.com/en-us/answers/questions/1305373/how-to-fix-the-term-az-is-not-recognized-as-the-na)



