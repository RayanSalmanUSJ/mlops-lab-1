Rayan Salman 231200

# LAB 1:

### Question 1: 
uv init creates pyproject.toml (tracks project metadata and dependencies), .python-version (pins the Python version), hello.py (template entrypoint), and .gitignore (excludes temporary environments).

### Question 2: 
dvc init creates the .dvc/ directory (stores DVC internal configurations, remote links, and cache settings) and .dvcignore. .dvcignore and .dvc/config should be pushed to Git so teammates share the same setup, but local cache files inside .dvc/cache must never be pushed to Git.

### Question 3: 
Credentials added with --global are stored in your machine's global user config file (%LOCALAPPDATA%\dvc\config on Windows). Alternatives are --local (stores in .dvc/config.local inside the repo) and --system (system-wide). Credentials must never be pushed to GitHub.

### Question 4: 
DVC automatically appended /data to your .gitignore file. This prevents Git from tracking large raw binary images, delegating data management entirely to DVC.

### Question 5: 
Yes, data.dvc is created in the root directory. It is a small text pointer file containing the MD5 hash of the data directory, total byte size, file count, and relative path (data).

### Question 6: 
On GitHub, only the code, .gitignore, configuration, and the lightweight data.dvc pointer file exist (the raw images are not on GitHub). On DagsHub, you can see both code and the actual image dataset because DagsHub integrates directly with DVC storage.

### Question 7: 
No, cloning the repository in a new folder will only bring down data.dvc, not the images. To restore the data/ folder, run dvc pull.

### Question 8: 
No, food11_processed and food11_processed_mini are no longer in your local folder. git checkout reverted data.dvc back to pointing only to food11_raw, and dvc checkout synced your filesystem to match that exact point in time.

# LAB 2:

### Question 1: 
Setting the PyTorch index to CPU-only in pyproject.toml forces uv.lock to resolve and pin the lightweight CPU versions of torch and torchvision. This prevents uv from downloading the massive default CUDA binaries, saving several gigabytes of space since you are using CPU processing.

### Question 2: 
The --backend-store-uri specifies where MLflow saves structured metadata, such as run IDs, parameter names, and metric values. The --default-artifact-root specifies the storage directory for heavy artifact files, such as trained model weights and charts. Metadata is lightweight and stored in a database (like SQLite), whereas artifacts are heavy binary outputs stored on a filesystem.

### Question 3: 
Git should not track these files because mlruns/ contains heavy binary artifacts that bloat Git repositories, and mlflow.db is a frequently updating local database that causes Git merge conflicts. DVC shouldn't track them because they are temporary, locally generated run outputs, not the canonical underlying dataset.

### Question 4: 
The first time you call mlflow.set_experiment("food11") with a non-existent name, MLflow automatically creates the experiment and assigns it a unique ID, which immediately appears in the left sidebar of the MLflow UI.

### Question 5: 
mlflow.log_param logs a fixed configuration value that does not change (like batch size or learning rate), while mlflow.log_metric logs a dynamic value that evolves during training (like loss). log_metric requires a step argument to map the metric's changes over time to create a time-series chart, whereas a parameter only needs to be recorded once.

### Question 6: 
Because you launched the server with --default-artifact-root ./mlruns, the actual model artifact lives on your local hard drive inside the ./mlruns/<experiment_id>/<run_id>/artifacts/model/ directory.

### Question 7: 
You will observe the results in your UI, but typically a learning rate of 0.001 achieves the best validation accuracy for a fine-tuned ResNet. Higher is not always better; an excessively high learning rate (like 0.01) often causes the model weights to overshoot optimal values, severely hurting accuracy.

### Question 8: 
In the parallel coordinates plot, you will likely see lines clustering toward high accuracy when lr is moderate (0.001 or 0.0001), whereas lines connected to a high lr (0.01) drop steeply to poor accuracy levels regardless of the batch size.

### Question 9: 
Sort the val_accuracy column descending in the MLflow UI to locate your best model. Make sure to copy that specific Run ID (a 32-character string), as it will be required for your next lab.

### Best Model Results
After running multiple experiments with varying learning rates and batch sizes on the `mini` dataset, the best-performing model achieved the following results:

* **Run ID:** `26fb07a20a6e4a94942f3ea119b53baf`
* **Run Name:** treasured-sloth-562

**Best Hyperparameters:**
* Dataset: mini
* Epochs: 5
* Learning Rate (lr): 0.01
* Batch Size: 32

**Final Metrics:**
* Validation Accuracy: ~17.34% (0.1733)
* Validation Loss: 2.4244
* Training Loss: 2.3759

# LAB 3
### Question 1
The model was given version 1. A logged model artifact is just a raw file saved to disk tied to a specific historical training run. A registered model acts as a centralized catalog that gives that model a persistent name (e.g., `food11`), tracks its lineage, and manages its deployment lifecycle across different versions independently of the raw experiment runs.

### Question 2:
Custom aliases (like `champion` or `challenger`) replaced the old fixed stages (`Staging`/`Production`). Versioning models separately allows you to manage the deployment lifecycle of the best models without sorting through hundreds of failed or experimental runs. Aliases are more flexible because they are mutable pointers; you can instantly reassign the `champion` tag to a newer version without touching your application code, whereas hardcoded stages were rigid.

### Question 3:
Using the MLflow model URI decouples the API code from hardcoded file paths and specific model versions. The application dynamically fetches whichever model currently holds the `champion` tag. To serve a newer model, you wouldn't need to change or redeploy the application code at all; you would simply update the `champion` alias in the MLflow Model Registry to point to the new version.

### Question 4:
Docker caches each layer sequentially. Because dependencies change much less frequently than application code, copying the lockfile and syncing first caches the heavy installation step. If you only change a line in `serve.py`, Docker skips the dependency installation and only rebuilds the final `COPY src/ ./src/` layer, making rebuilds nearly instant.

### Question 5:
A multi-stage image is significantly smaller. The final runtime stage discards all the heavy build tools, package managers (`uv`), and source caches from the builder stage, retaining only the minimal Python runtime and the compiled dependencies required to execute the API.

### Question 6:
Without `.dockerignore`, the Docker daemon copies your entire project directory (including gigabytes of image data and models) into the build context, destroying build speed and ballooning image size. Crucially, copying the local `.venv/` folder would break the build: it contains a Windows-compiled virtual environment, which is completely incompatible with the Linux base image inside the container.

### Question 7:
Because a Docker container runs in its own isolated network namespace, `127.0.0.1` (localhost) inside the container points to the container itself, not the host machine. `host.docker.internal` is a special DNS name provided by Docker Desktop that resolves to the host machine's internal IP address, allowing the container to bridge the gap and communicate with the local MLflow server.

### Question 8:
Yes, the model still loads correctly. This tells us that the model files are *not* baked into the Docker image itself. Instead, the image only contains the API code and the Python environment (the dependencies). The actual ML model is fetched dynamically at runtime from the MLflow tracking server via the `MLFLOW_TRACKING_URI`.

### Question 9:
The built Docker image currently only exists locally on this specific machine. To allow other machines or CI pipelines to pull and run the exact same container, the image needs to be pushed to a remote container registry (such as Docker Hub, GitHub Container Registry, or AWS ECR) using `docker push`.

# LAB 4

### Question 1:
If a volume is not mounted, everything written to `/mlflow-data` is saved to the container's ephemeral, writable layer. When the container is stopped and removed, all that data (the database and artifacts) is permanently deleted. Starting a new container from the same image will result in a completely empty MLflow UI with no history.

### Question 2:
A named volume is managed entirely by Docker, making it highly portable and immune to file permission conflicts across different operating systems. A bind mount maps directly to a specific folder path on the host machine, which works for local development but can cause permission errors (like the SQLite lock issues encountered earlier) or break if the path changes on a different host.

### Question 3:
The hostname resolves because Docker Compose automatically creates an isolated, custom network for all the services defined in the `docker-compose.yml` file. Within this custom network, Docker provides embedded DNS resolution, allowing containers to discover and communicate with each other simply by using their assigned service names (like `mlflow`) as hostnames.

### Question 4:
Reading the URL from an environment variable decouples the frontend code from a specific deployment environment. If the URL were hardcoded, the image could only ever work inside the specific Compose network where the backend is named `inference`. By using an environment variable, the image becomes flexible and can be run standalone or pointed at a remote production API without modifying the application code.

### Question 5:
The `inference` service does not need a published port because it is only meant to be accessed internally by the frontend service, not directly by a user from the host machine. The frontend container can still reach the inference container over port 8000 because all ports are inherently open and accessible *within* the private Docker Compose network; publishing a port only controls external access from the host.

### Question 6:
If the inference container attempts to fetch the model before the MLflow server is fully initialized and accepting connections, the API call will fail with a connection error. Because `serve.py` loads the model synchronously at startup, the failure will cause the Uvicorn application to crash, and the `inference` container will exit entirely.

### Question 7:
The `mlflow` and `frontend` services have published ports (5000 and 8501, respectively). The `inference` service does not have a published port listed. This perfectly matches the `docker-compose.yml` file, where only `mlflow` and `frontend` were given `ports:` blocks, leaving `inference` strictly on the internal Docker network.

### Question 8:
The prediction still comes from the old model version because `serve.py` caches the model in memory at startup and does not actively poll MLflow for updates. To fetch the new version without rebuilding anything, you just restart the container: `docker compose restart inference`.

### Question 9:
A restart works without a rebuild because the ML model is not baked into the Docker image itself. The image only contains the static Python code and dependencies. The model artifacts are dynamic data fetched over the network from the MLflow tracking server every time the container executes its startup routine.

### Question 10:
Yes, after a standard `down` and `up`, the model is still there because the `mlflow-data` volume persists. However, running `docker compose down -v` destroys all named volumes. When bringing it back `up` afterwards, the MLflow UI is completely empty because the persistent database and artifacts were explicitly deleted.

### Question 11:
Docker Compose is inherently limited to single-node orchestration. To distribute replicas across multiple machines, automatically load balance incoming traffic, and provide self-healing failover if a machine dies, we would need a distributed container orchestration system like Kubernetes or Docker Swarm.
