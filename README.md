# python_slackbot

## 準備

以下からアプリを追加する。

https://slack.com/apps/A0F7YS25R-bots

## ローカル実行

`slackbot_setting.py`に設定を記述する。トークンは`API_TOKEN`としてここで書いてもよいが、環境変数`SLACKBOT_API_TOKEN`でも渡せるので環境変数で渡す。
エラーの通知先のユーザーを指定する場合は`ERRORS_TO`を指定する。ユーザーがいない場合は起動エラーになるので注意。

必要なモジュールをインストールする。

```shell
pip install kubernetes
pip install prettytable
pip install slackbot
```

APIトークンを`export`する。

```
export SLACKBOT_API_TOKEN=hogehoge
```

Botを起動する。

```shell
python run.py
```

### Kubernetesへのデプロイ

イメージをビルドする。

```shell
docker build -t sotoiwa540/slackbot:1.0 .
docker push sotoiwa540/slackbot:1.0
```

ローカルで実行する場合は、`HOME/.kube/config`から認証情報を読み込むが、KubernetesでPodとして実行する場合はServiceAccountの権限で実行するので、ClusterRoleとClusterRoleBindingを作成する。
NamespaceのデフォルトのServiceAccountにClusterRoleをバインドしているので、Namespace名を適切に設定すること。

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: slackbot
rules:
- apiGroups: [""]
  resources:
  - pods
  - namespaces
  verbs:
  - list
```

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: slackbot
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: ClusterRole
  name: slackbot
  apiGroup: rbac.authorization.k8s.io
```

```shell
kubectl apply -f slackbot-clusterrole.yaml
kubectl apply -f slackbot-clusterrolebinding.yaml
```

APIトークンのSecretを作成する。

```shell
kubectl create secret generic slackbot-secret --from-literal=SLACKBOT_API_TOKEN=hogehoge
```

Deploymentを作成する。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
  labels:
    app: slackbot
  name: slackbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: slackbot
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: slackbot
    spec:
      containers:
      - name: slackbot
        image: sotoiwa540/slackbot:1.0
        imagePullPolicy: Always
        env:
        - name: SLACKBOT_API_TOKEN
          valueFrom:
            secretKeyRef:
              key: SLACKBOT_API_TOKEN
              name: slackbot-secret
```

```shell
kubectl apply -f slackbot-deployment.yaml
```
