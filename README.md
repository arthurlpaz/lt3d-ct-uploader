# 🦾 ProtesIA — CT Uploader

Interface web para upload de dados CT para a VM do HUAC.

## Início rápido

```bash
# Na VM
cd ~/ct_uploader
docker compose up -d
```

A médica acessa (com VPN ativa):
```
http://10.100.100.179:8000
```

## O que aceita

| Tipo | Extensões | Destino |
|------|-----------|---------|
| Pasta DICOM | qualquer | `raw_data/<nome_da_pasta>/` |
| Compactado | `.zip`, `.tar.gz`, `.tgz` | `raw_data/<nome_do_arquivo>/` |
| NIfTI | `.nii`, `.nii.gz` | `raw_data/` |

## raw_data no host

O bind mount faz `raw_data/` existir no host, não dentro do container:

```
container:/app/raw_data  ←→  host:~/ct_uploader/raw_data
```

O pipeline lê direto do host sem depender do container.

Para apontar para outra pasta:

```bash
RAW_DATA_HOST=/data/protesia/raw_data docker compose up -d
```

## Comandos

```bash
docker compose ps          # status
docker compose logs -f     # logs
docker compose down        # parar
docker compose build       # rebuild após alterar código
docker compose up -d       # subir
```