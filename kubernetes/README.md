# Deploying with Kubernetes

## TL;DR

```console
$ git clone git@github.com:jmbannon/ytdl-sub.git
$ cd ytdl-sub/kubernetes
$ $EDITOR kustomization.yaml subs.yaml presets.yaml
$ kuzomise build . | kubectl apply -f -
```

## Configuration

Make sure you set the following to the right values for your kubernetes setup:
- `storageClassName` for each of the volumes in `./volumes.yaml`
- `namespace` in `kustomization.yaml`
- `images` overrides in `kustomization.yaml` if you don't want to use the minimal image
- `schedule` in `cronjob.yaml` if you want to run on a different schedule (defaults to
  hourly.)

It should build a valid configuration without changing these kubernetes settings, but
it will probably not be what you're expecting.

See the normal documentation for configuring the `subs.yaml` and `presets.yaml` files.
