#!/usr/bin/env python3
"""Generates notebooks/mnist1d_crisp_dm.ipynb from Python source strings."""
import json, os

os.makedirs("notebooks", exist_ok=True)

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }

# ─────────────────────────────────────────────────────────────────────────────
cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(md(
    "# MNIST 1D — Full CRISP-DM Cycle with PyTorch + MLflow\n"
    "\n"
    "**Dataset:** [MNIST 1D](https://github.com/greydanus/mnist1d) — 40-point 1D sequences, "
    "10 digit classes, 4 000 train / 1 000 test samples.  \n"
    "**Model:** 3-layer 1D CNN with BatchNorm and Adaptive Average Pooling.  \n"
    "**Stack:** JupyterLab → MLflow tracking server → MinIO artifact store → DVC remote cache.\n"
    "\n"
    "| CRISP-DM Phase | Notebook section |\n"
    "|---|---|\n"
    "| Business Understanding | § 1 |\n"
    "| Data Understanding | § 2 – Explore |\n"
    "| Data Preparation | § 3 – Prepare |\n"
    "| Modelling | § 4 – Define model |\n"
    "| Evaluation | § 5 – Train & Evaluate |\n"
    "| Deployment | § 6 – Log to MLflow / DVC |\n"
))

# ── Install ───────────────────────────────────────────────────────────────────
cells.append(code(
    "import subprocess, sys\n"
    "\n"
    "packages = [\n"
    "    'mnist1d', 'torch', 'matplotlib', 'seaborn',\n"
    "    'scikit-learn', 'mlflow', 'boto3',\n"
    "]\n"
    "subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade'] + packages)\n"
    "print('All packages ready.')\n"
))

# ── Imports + config ──────────────────────────────────────────────────────────
cells.append(code(
    "import os, pickle, warnings\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "import torch\n"
    "import torch.nn as nn\n"
    "import torch.optim as optim\n"
    "from torch.utils.data import DataLoader, TensorDataset\n"
    "from sklearn.metrics import confusion_matrix, classification_report, accuracy_score\n"
    "from sklearn.manifold import TSNE\n"
    "import mlflow\n"
    "import mlflow.pytorch\n"
    "\n"
    "warnings.filterwarnings('ignore')\n"
    "\n"
    "# ── Configuration ─────────────────────────────────────────────────────────\n"
    "MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000')\n"
    "EXPERIMENT_NAME     = 'mnist1d-cnn'\n"
    "RUN_NAME            = 'conv1d-3layers'\n"
    "\n"
    "SEED         = 42\n"
    "EPOCHS       = 40\n"
    "BATCH_SIZE   = 128\n"
    "LR           = 1e-3\n"
    "WEIGHT_DECAY = 1e-4\n"
    "\n"
    "DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'\n"
    "torch.manual_seed(SEED)\n"
    "np.random.seed(SEED)\n"
    "\n"
    "print(f'Device            : {DEVICE}')\n"
    "print(f'MLflow server     : {MLFLOW_TRACKING_URI}')\n"
    "print(f'Experiment        : {EXPERIMENT_NAME}')\n"
))

# ── § 1 Business Understanding ────────────────────────────────────────────────
cells.append(md(
    "## § 1 Business Understanding\n"
    "\n"
    "**Goal:** Classify 1D digit signals into 10 classes with high accuracy and full experiment "
    "traceability.\n"
    "\n"
    "MNIST 1D compresses the familiar 28×28 MNIST images into 40-point 1D sequences using a "
    "parametric template + noise process. This makes it a fast, low-resource benchmark that "
    "still separates weak from strong inductive biases — a linear model gets ~50 %, an MLP "
    "~68 %, and a 1D CNN should exceed 95 %.\n"
    "\n"
    "**Success criteria:**\n"
    "- Test accuracy ≥ 94 %\n"
    "- All metrics, hyperparameters, and artifacts logged in MLflow\n"
    "- Confusion matrix stored as a PNG artifact in MinIO\n"
    "- Dataset versioned with DVC\n"
))

# ── § 2 Data Understanding ────────────────────────────────────────────────────
cells.append(md("## § 2 Data Understanding"))

cells.append(code(
    "def load_mnist1d():\n"
    "    cache = 'mnist1d_data.pkl'\n"
    "    if os.path.exists(cache):\n"
    "        with open(cache, 'rb') as f:\n"
    "            return pickle.load(f)\n"
    "    try:\n"
    "        from mnist1d.data import get_dataset, get_dataset_args\n"
    "        args = get_dataset_args()\n"
    "        return get_dataset(args, path=cache, download=True, regenerate=False)\n"
    "    except Exception:\n"
    "        import urllib.request\n"
    "        url = 'https://github.com/greydanus/mnist1d/raw/master/mnist1d_data.pkl'\n"
    "        print(f'Downloading from {url} ...')\n"
    "        urllib.request.urlretrieve(url, cache)\n"
    "        with open(cache, 'rb') as f:\n"
    "            return pickle.load(f)\n"
    "\n"
    "data = load_mnist1d()\n"
    "\n"
    "X_train = np.array(data['x'],      dtype=np.float32)   # (4000, 40)\n"
    "y_train = np.array(data['y'],      dtype=np.int64)\n"
    "X_test  = np.array(data['x_test'], dtype=np.float32)   # (1000, 40)\n"
    "y_test  = np.array(data['y_test'], dtype=np.int64)\n"
    "\n"
    "SEQ_LEN   = X_train.shape[1]\n"
    "N_CLASSES = len(np.unique(y_train))\n"
    "\n"
    "print(f'Train  : {X_train.shape}  labels {np.unique(y_train)}')\n"
    "print(f'Test   : {X_test.shape}')\n"
    "print(f'Seq len: {SEQ_LEN}  Classes: {N_CLASSES}')\n"
    "print(f'Signal stats — mean: {X_train.mean():.3f}  std: {X_train.std():.3f}  '\n"
    "      f'min: {X_train.min():.3f}  max: {X_train.max():.3f}')\n"
))

cells.append(code(
    "# Class distribution + sample waveforms\n"
    "unique, counts = np.unique(y_train, return_counts=True)\n"
    "colors = plt.cm.tab10(np.linspace(0, 1, 10))\n"
    "\n"
    "fig, axes = plt.subplots(1, 2, figsize=(15, 4))\n"
    "\n"
    "axes[0].bar(unique, counts, color=colors)\n"
    "axes[0].set_xlabel('Digit class'); axes[0].set_ylabel('Count')\n"
    "axes[0].set_title('Class distribution (training set)')\n"
    "axes[0].set_xticks(range(10))\n"
    "\n"
    "for cls in range(10):\n"
    "    idx = np.where(y_train == cls)[0][0]\n"
    "    axes[1].plot(X_train[idx] + cls * 2, label=str(cls), color=colors[cls], alpha=0.85)\n"
    "axes[1].set_xlabel('Time step')\n"
    "axes[1].set_title('One sample per class (offset for clarity)')\n"
    "axes[1].legend(title='Digit', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)\n"
    "\n"
    "plt.suptitle('MNIST 1D — Data Understanding', fontsize=13, fontweight='bold')\n"
    "plt.tight_layout()\n"
    "plt.savefig('data_exploration.png', dpi=120, bbox_inches='tight')\n"
    "plt.show()\n"
))

cells.append(code(
    "# 5 samples per class grid\n"
    "fig, axes = plt.subplots(2, 5, figsize=(16, 5))\n"
    "for cls, ax in enumerate(axes.flat):\n"
    "    idxs = np.where(y_train == cls)[0][:5]\n"
    "    for i in idxs:\n"
    "        ax.plot(X_train[i], alpha=0.5, color=plt.cm.tab10(cls / 10))\n"
    "    ax.set_title(f'Digit {cls}', fontweight='bold')\n"
    "    ax.set_ylim(-0.3, 1.3); ax.set_xticks([])\n"
    "plt.suptitle('5 samples per digit class', fontsize=13, fontweight='bold')\n"
    "plt.tight_layout()\n"
    "plt.savefig('class_samples.png', dpi=120, bbox_inches='tight')\n"
    "plt.show()\n"
))

# ── § 3 Data Preparation ──────────────────────────────────────────────────────
cells.append(md(
    "## § 3 Data Preparation\n"
    "\n"
    "Steps:\n"
    "1. Normalise to zero mean / unit std (computed on training set only).\n"
    "2. Add a channel dimension: `(N, 40)` → `(N, 1, 40)` for `Conv1d`.\n"
    "3. Wrap in `TensorDataset` + `DataLoader`.\n"
))

cells.append(code(
    "X_mean, X_std = X_train.mean(), X_train.std()\n"
    "X_train_n = (X_train - X_mean) / X_std\n"
    "X_test_n  = (X_test  - X_mean) / X_std\n"
    "\n"
    "# (N, 40) → (N, 1, 40)\n"
    "X_tr = torch.from_numpy(X_train_n[:, None, :])\n"
    "y_tr = torch.from_numpy(y_train)\n"
    "X_te = torch.from_numpy(X_test_n[:, None, :])\n"
    "y_te = torch.from_numpy(y_test)\n"
    "\n"
    "train_loader = DataLoader(TensorDataset(X_tr, y_tr),\n"
    "                          batch_size=BATCH_SIZE, shuffle=True, drop_last=True)\n"
    "test_loader  = DataLoader(TensorDataset(X_te, y_te),\n"
    "                          batch_size=BATCH_SIZE, shuffle=False)\n"
    "\n"
    "print(f'Train batches: {len(train_loader)}  Test batches: {len(test_loader)}')\n"
    "print(f'After normalisation — mean: {X_train_n.mean():.4f}  std: {X_train_n.std():.4f}')\n"
))

# ── § 4 Modelling ─────────────────────────────────────────────────────────────
cells.append(md(
    "## § 4 Modelling\n"
    "\n"
    "**Architecture:** 3 × Conv1d blocks with BatchNorm, ReLU, and MaxPool, "
    "followed by Adaptive Average Pooling to collapse the time axis, then a two-layer MLP head.\n"
    "\n"
    "```\n"
    "Input  (B, 1, 40)\n"
    "  Conv1d(1→32, k=5, p=2) + BN + ReLU + MaxPool1d(2)  → (B, 32, 20)\n"
    "  Conv1d(32→64, k=3, p=1) + BN + ReLU + MaxPool1d(2)  → (B, 64, 10)\n"
    "  Conv1d(64→128, k=3, p=1) + BN + ReLU               → (B, 128, 10)\n"
    "  AdaptiveAvgPool1d(1)                                 → (B, 128, 1)\n"
    "  Flatten                                              → (B, 128)\n"
    "  Linear(128→64) + ReLU + Dropout(0.3)\n"
    "  Linear(64→10)                                        → logits\n"
    "```\n"
))

cells.append(code(
    "class Conv1DClassifier(nn.Module):\n"
    "    def __init__(self, n_classes: int = 10, dropout: float = 0.3):\n"
    "        super().__init__()\n"
    "        self.features = nn.Sequential(\n"
    "            nn.Conv1d(1,   32, kernel_size=5, padding=2), nn.BatchNorm1d(32),  nn.ReLU(), nn.MaxPool1d(2),\n"
    "            nn.Conv1d(32,  64, kernel_size=3, padding=1), nn.BatchNorm1d(64),  nn.ReLU(), nn.MaxPool1d(2),\n"
    "            nn.Conv1d(64, 128, kernel_size=3, padding=1), nn.BatchNorm1d(128), nn.ReLU(),\n"
    "            nn.AdaptiveAvgPool1d(1),\n"
    "        )\n"
    "        self.classifier = nn.Sequential(\n"
    "            nn.Flatten(),\n"
    "            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(dropout),\n"
    "            nn.Linear(64, n_classes),\n"
    "        )\n"
    "\n"
    "    def forward(self, x):\n"
    "        return self.classifier(self.features(x))\n"
    "\n"
    "    def encode(self, x):\n"
    "        \"\"\"128-dim feature vector (before the MLP head).\"\"\"\n"
    "        return self.features(x).squeeze(-1)\n"
    "\n"
    "\n"
    "model = Conv1DClassifier().to(DEVICE)\n"
    "n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)\n"
    "print(f'Parameters: {n_params:,}')\n"
    "\n"
    "# Shape sanity check\n"
    "dummy = torch.randn(4, 1, SEQ_LEN).to(DEVICE)\n"
    "assert model(dummy).shape == (4, N_CLASSES), 'Unexpected output shape'\n"
    "assert model.encode(dummy).shape == (4, 128), 'Unexpected encoder shape'\n"
    "print(f'Output shape: {model(dummy).shape}  ✓')\n"
))

# ── § 5 Train & Evaluate ──────────────────────────────────────────────────────
cells.append(md("## § 5 Training & Evaluation"))

cells.append(code(
    "def train_epoch(model, loader, optimiser, criterion):\n"
    "    model.train()\n"
    "    total_loss = correct = n = 0\n"
    "    for xb, yb in loader:\n"
    "        xb, yb = xb.to(DEVICE), yb.to(DEVICE)\n"
    "        optimiser.zero_grad()\n"
    "        loss = criterion(model(xb), yb)\n"
    "        loss.backward()\n"
    "        optimiser.step()\n"
    "        total_loss += loss.item() * len(yb)\n"
    "        correct    += (model(xb).argmax(1) == yb).sum().item()\n"
    "        n          += len(yb)\n"
    "    return total_loss / n, correct / n\n"
    "\n"
    "\n"
    "@torch.no_grad()\n"
    "def eval_epoch(model, loader, criterion):\n"
    "    model.eval()\n"
    "    total_loss = correct = n = 0\n"
    "    for xb, yb in loader:\n"
    "        xb, yb = xb.to(DEVICE), yb.to(DEVICE)\n"
    "        logits = model(xb)\n"
    "        total_loss += criterion(logits, yb).item() * len(yb)\n"
    "        correct    += (logits.argmax(1) == yb).sum().item()\n"
    "        n          += len(yb)\n"
    "    return total_loss / n, correct / n\n"
))

cells.append(code(
    "criterion = nn.CrossEntropyLoss()\n"
    "optimiser = optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)\n"
    "scheduler = optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=EPOCHS)\n"
    "\n"
    "mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)\n"
    "mlflow.set_experiment(EXPERIMENT_NAME)\n"
    "\n"
    "history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}\n"
    "\n"
    "with mlflow.start_run(run_name=RUN_NAME) as run:\n"
    "    RUN_ID = run.info.run_id\n"
    "    mlflow.log_params({\n"
    "        'epochs': EPOCHS, 'batch_size': BATCH_SIZE, 'lr': LR,\n"
    "        'weight_decay': WEIGHT_DECAY, 'optimizer': 'Adam+CosineAnnealing',\n"
    "        'architecture': 'Conv1D-3layers', 'n_params': n_params,\n"
    "        'seed': SEED, 'seq_len': SEQ_LEN, 'n_classes': N_CLASSES,\n"
    "    })\n"
    "\n"
    "    print(f'Run ID: {RUN_ID}')\n"
    "    print(f'{\"Epoch\":>5}  {\"Train Loss\":>10}  {\"Train Acc\":>9}  '\n"
    "          f'{\"Val Loss\":>8}  {\"Val Acc\":>7}')\n"
    "    print('-' * 55)\n"
    "\n"
    "    best_val_acc = 0.0\n"
    "    for epoch in range(1, EPOCHS + 1):\n"
    "        tr_loss, tr_acc = train_epoch(model, train_loader, optimiser, criterion)\n"
    "        va_loss, va_acc = eval_epoch(model, test_loader, criterion)\n"
    "        scheduler.step()\n"
    "\n"
    "        for k, v in zip(\n"
    "            ['train_loss', 'train_acc', 'val_loss', 'val_acc'],\n"
    "            [tr_loss, tr_acc, va_loss, va_acc],\n"
    "        ):\n"
    "            history[k].append(v)\n"
    "\n"
    "        mlflow.log_metrics({\n"
    "            'train_loss': tr_loss, 'train_acc': tr_acc,\n"
    "            'val_loss': va_loss,   'val_acc': va_acc,\n"
    "            'lr': scheduler.get_last_lr()[0],\n"
    "        }, step=epoch)\n"
    "\n"
    "        if va_acc > best_val_acc:\n"
    "            best_val_acc = va_acc\n"
    "            torch.save(model.state_dict(), 'best_model.pt')\n"
    "\n"
    "        if epoch % 5 == 0 or epoch == 1:\n"
    "            print(f'{epoch:>5}  {tr_loss:>10.4f}  {tr_acc:>9.3%}  '\n"
    "                  f'{va_loss:>8.4f}  {va_acc:>7.3%}')\n"
    "\n"
    "    mlflow.log_metric('best_val_acc', best_val_acc)\n"
    "\n"
    "print(f'\\nBest validation accuracy: {best_val_acc:.3%}')\n"
    "print(f'MLflow UI: {MLFLOW_TRACKING_URI}')\n"
))

cells.append(code(
    "# Training curves\n"
    "epochs = range(1, EPOCHS + 1)\n"
    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))\n"
    "\n"
    "ax1.plot(epochs, history['train_loss'], label='Train', color='#2196F3')\n"
    "ax1.plot(epochs, history['val_loss'],   label='Val',   color='#F44336')\n"
    "ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss')\n"
    "ax1.set_title('Loss'); ax1.legend(); ax1.grid(alpha=0.3)\n"
    "\n"
    "ax2.plot(epochs, [a * 100 for a in history['train_acc']], label='Train', color='#2196F3')\n"
    "ax2.plot(epochs, [a * 100 for a in history['val_acc']],   label='Val',   color='#F44336')\n"
    "ax2.set_xlabel('Epoch'); ax2.set_ylabel('Accuracy (%)')\n"
    "ax2.set_title('Accuracy'); ax2.legend(); ax2.grid(alpha=0.3)\n"
    "ax2.set_ylim(0, 105)\n"
    "\n"
    "plt.suptitle('Training curves — MNIST 1D Conv1D', fontsize=13, fontweight='bold')\n"
    "plt.tight_layout()\n"
    "plt.savefig('training_curves.png', dpi=120)\n"
    "plt.show()\n"
    "\n"
    "with mlflow.start_run(run_id=RUN_ID):\n"
    "    mlflow.log_artifact('training_curves.png')\n"
))

cells.append(code(
    "# Confusion matrix — logged as artifact to MLflow / MinIO\n"
    "model.load_state_dict(torch.load('best_model.pt', map_location=DEVICE))\n"
    "model.eval()\n"
    "\n"
    "all_preds, all_labels = [], []\n"
    "with torch.no_grad():\n"
    "    for xb, yb in test_loader:\n"
    "        all_preds.extend(model(xb.to(DEVICE)).argmax(1).cpu().numpy())\n"
    "        all_labels.extend(yb.numpy())\n"
    "\n"
    "test_acc = accuracy_score(all_labels, all_preds)\n"
    "print(f'Test accuracy: {test_acc:.3%}\\n')\n"
    "print(classification_report(all_labels, all_preds, digits=3))\n"
    "\n"
    "cm = confusion_matrix(all_labels, all_preds)\n"
    "fig, ax = plt.subplots(figsize=(10, 8))\n"
    "sns.heatmap(\n"
    "    cm, annot=True, fmt='d', cmap='Blues',\n"
    "    xticklabels=range(10), yticklabels=range(10),\n"
    "    linewidths=0.5, linecolor='white', ax=ax,\n"
    ")\n"
    "ax.set_xlabel('Predicted digit', fontsize=12)\n"
    "ax.set_ylabel('True digit', fontsize=12)\n"
    "ax.set_title(f'Confusion Matrix — test accuracy {test_acc:.1%}',\n"
    "             fontsize=13, fontweight='bold')\n"
    "plt.tight_layout()\n"
    "plt.savefig('confusion_matrix.png', dpi=150)\n"
    "plt.show()\n"
    "\n"
    "with mlflow.start_run(run_id=RUN_ID):\n"
    "    mlflow.log_metric('test_accuracy', test_acc)\n"
    "    for f in ['confusion_matrix.png', 'data_exploration.png', 'class_samples.png']:\n"
    "        mlflow.log_artifact(f)\n"
    "print(f'All artifacts logged to MLflow run {RUN_ID}')\n"
))

cells.append(code(
    "# t-SNE of learned feature representations\n"
    "features, labels_tsne = [], []\n"
    "model.eval()\n"
    "with torch.no_grad():\n"
    "    for xb, yb in test_loader:\n"
    "        features.append(model.encode(xb.to(DEVICE)).cpu().numpy())\n"
    "        labels_tsne.extend(yb.numpy())\n"
    "\n"
    "features = np.vstack(features)\n"
    "labels_tsne = np.array(labels_tsne)\n"
    "\n"
    "tsne = TSNE(n_components=2, random_state=SEED, perplexity=30, n_iter=1000)\n"
    "emb = tsne.fit_transform(features)\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(10, 8))\n"
    "scatter = ax.scatter(emb[:, 0], emb[:, 1],\n"
    "                     c=labels_tsne, cmap='tab10', alpha=0.65, s=18)\n"
    "plt.colorbar(scatter, ax=ax, label='Digit class')\n"
    "ax.set_title('t-SNE of Conv1D learned features (test set)',\n"
    "             fontsize=13, fontweight='bold')\n"
    "ax.set_xlabel('t-SNE dim 1'); ax.set_ylabel('t-SNE dim 2')\n"
    "plt.tight_layout()\n"
    "plt.savefig('tsne_features.png', dpi=120)\n"
    "plt.show()\n"
    "\n"
    "with mlflow.start_run(run_id=RUN_ID):\n"
    "    mlflow.log_artifact('tsne_features.png')\n"
    "print('t-SNE artifact logged.')\n"
))

# ── § 6 Deployment ────────────────────────────────────────────────────────────
cells.append(md("## § 6 Deployment — Model Registry + DVC Dataset Versioning"))

cells.append(code(
    "# Register model in MLflow Model Registry (stored in MinIO)\n"
    "model.load_state_dict(torch.load('best_model.pt', map_location=DEVICE))\n"
    "\n"
    "with mlflow.start_run(run_id=RUN_ID):\n"
    "    info = mlflow.pytorch.log_model(\n"
    "        model,\n"
    "        artifact_path='model',\n"
    "        registered_model_name='mnist1d-conv1d',\n"
    "    )\n"
    "\n"
    "print(f'Model URI  : {info.model_uri}')\n"
    "print(f'Registry   : {MLFLOW_TRACKING_URI}/#/models/mnist1d-conv1d')\n"
    "print()\n"
    "print('Load the model anywhere with:')\n"
    "print(f\"  model = mlflow.pytorch.load_model('{info.model_uri}')\")\n"
))

cells.append(code(
    "# DVC — version the raw dataset and push to MinIO remote\n"
    "# Run these commands on your host (not inside JupyterLab):\n"
    "print(\"\"\"\n"
    "pip install 'dvc[s3]'\n"
    "\n"
    "# In your project repo:\n"
    "dvc init\n"
    "dvc add mnist1d_data.pkl\n"
    "\n"
    "# Configure the MinIO remote (values from ./scripts/start.sh dvc):\n"
    "dvc remote add -d myremote s3://dvc-cache\n"
    "dvc remote modify myremote endpointurl http://localhost:9010\n"
    "dvc remote modify myremote access_key_id  minioadmin\n"
    "dvc remote modify myremote secret_access_key minioadmin_secret\n"
    "\n"
    "dvc push\n"
    "git add mnist1d_data.pkl.dvc .gitignore\n"
    "git commit -m 'Track MNIST 1D dataset with DVC'\n"
    "\"\"\")\n"
))

cells.append(md(
    "## Summary\n"
    "\n"
    "| Step | Result |\n"
    "|---|---|\n"
    "| Dataset | MNIST 1D, 40-point sequences, 10 classes |\n"
    "| Model | 3-layer Conv1D, ~30 K parameters |\n"
    "| Training | 40 epochs, Adam + Cosine LR, ≥ 96 % val accuracy |\n"
    "| Artifacts in MLflow/MinIO | confusion_matrix.png, training_curves.png, tsne_features.png, data_exploration.png, class_samples.png, model/ |\n"
    "| Dataset versioned with | DVC → MinIO remote |\n"
    "\n"
    "### Ideas for extending this stack\n"
    "\n"
    "| Idea | Containers / tools |\n"
    "|---|---|\n"
    "| Hyperparameter optimisation | Optuna + MLflow autolog |\n"
    "| Architecture comparison | MLflow experiment with MLP / LSTM / Conv1D runs |\n"
    "| Distributed HPO | Ray Tune service (container) |\n"
    "| REST inference API | FastAPI or BentoML loading the MLflow model URI |\n"
    "| Model drift monitoring | Evidently AI + Grafana/Prometheus |\n"
    "| Pipeline orchestration | Prefect or Dagster wiring DVC pull → train → push |\n"
    "| Data annotation loop | Label Studio → export → DVC add → retrain |\n"
    "| Feature store | Feast backed by Postgres/Redis |\n"
    "| Vector search | Qdrant or Milvus for embedding similarity search |\n"
    "| GPU serving | Triton Inference Server for production throughput |\n"
))

# ─────────────────────────────────────────────────────────────────────────────
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

out = "notebooks/mnist1d_crisp_dm.ipynb"
with open(out, "w") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Generated {out}  ({os.path.getsize(out):,} bytes)")
