# python_slackbot

## 準備

以下からアプリを追加する。

https://slack.com/apps/A0F7YS25R-bots

## ローカル実行

`slackbot_setting.py`に設定を記述する。トークンは`API_TOKEN`としてここで書いてもよいが、環境変数`SLACKBOT_API_TOKEN`でも渡せるので環境変数で渡す。
エラーの通知先のユーザーを指定する場合は`ERRORS_TO`を指定する。ユーザーがいない場合は起動エラーになるので注意。

必要なモジュールをインストールする。

```shell
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
docker build -t sotoiwa540/slackbot:1.1 .
docker push sotoiwa540/slackbot:1.1
```

Podをデプロイする専用のNamespaceを作成する。

```shell
kubectl create ns slackbot
```

ローカルで実行する場合は、kubectlは`HOME/.kube/config`から認証情報を読み込むが、Kubernetes上でPodとして実行する場合はPodを実行するServiceAccountの権限で実行されるので、適切な権限を与える必要がある。

Podに明示的にServiceAccountを指定しない場合は、Podは稼働するNamespaceの`default`のServiceAccountの権限で実行される。

ここではデフォルトで存在する`view`というClusterRoleを、`default`のServiceAccountに割り当てるRoleBindingを作成する。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: slackbot
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: view
subjects:
- kind: ServiceAccount
  name: default
  namespace: slackbot
```

```shell
kubectl apply -f slackbot-clusterrolebinding.yaml -n slackbot
```

APIトークンのSecretを作成する。

```shell
kubectl create secret generic slackbot-secret --from-literal=SLACKBOT_API_TOKEN=hogehoge -n slackbot
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
        image: sotoiwa540/slackbot:1.1
        imagePullPolicy: Always
        env:
        - name: SLACKBOT_API_TOKEN
          valueFrom:
            secretKeyRef:
              key: SLACKBOT_API_TOKEN
              name: slackbot-secret
```

```shell
kubectl apply -f slackbot-deployment.yaml -n slackbot
```
