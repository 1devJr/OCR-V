# OCR-V: Validação de Validade de Remédios com YOLO e Tesseract

Este projeto utiliza YOLO para detectar regiões de validade em embalagens de remédios e Tesseract para extrair e validar a data.

## Como usar

### 1. Build da imagem Docker

```sh
docker build -t ocr-v .
```

### 2. Rodar validação em uma imagem

```sh
docker run --rm -v $(pwd)/app:/app/app ocr-v python main.py /app/app/sua_imagem.jpg
```

### 3. Rodar validação em tempo real (webcam)

```sh
docker run --rm --device /dev/video0 -v $(pwd)/app:/app/app ocr-v python realtime.py
```

> Certifique-se de que sua webcam está acessível no Docker (`--device /dev/video0`).

## Estrutura
- `app/main.py`: Validação de imagens individuais
- `app/realtime.py`: Validação em tempo real via webcam
- `app/annotate.py`: Ferramenta para anotar imagens e gerar base de aprendizado (dataset) no formato YOLO
- `requirements.txt`: Dependências Python
- `Dockerfile`: Ambiente dockerizado

## Observações
- O modelo YOLO usado é o `yolov8n.pt` (pode ser customizado para melhor acurácia).
- O Tesseract precisa estar ajustado para o idioma e formato das datas.
- Para treinar um modelo YOLO customizado, adicione suas imagens anotadas e ajuste o código conforme necessário.

## Como anotar imagens para criar o dataset

1. Coloque suas imagens na pasta `app` ou em outra de sua escolha.
2. Execute o script de anotação para cada imagem:

```sh
docker run --rm -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/app:/app/app \
  ocr-v python annotate.py /app/app/sua_imagem.jpg /app/app/dataset
```

- Use o mouse para desenhar o retângulo sobre a validade.
- Pressione `s` para salvar a anotação ou `ESC` para cancelar.
- O script salva a imagem e um arquivo `.txt` no formato YOLO em `dataset/`.

## Como anotar imagens para duas classes (correta/errada)

1. Execute o script de anotação para cada imagem:

```sh
docker run --rm -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/app:/app/app \
  ocr-v python annotate.py /app/app/sua_imagem.jpg /app/app/dataset
```

- Desenhe a caixa sobre a validade.
- Pressione `0` para marcar como "correta" ou `1` para "errada".
- Pressione `s` para salvar a anotação.
- O script salva a imagem e o arquivo `.txt` com a classe escolhida.

No seu dataset YOLO:
- Classe 0 = validade correta
- Classe 1 = validade errada

Ajuste o arquivo `data.yaml` para:
```yaml
nc: 2
names: ['correta', 'errada']
```

O restante do fluxo de treino permanece igual.

## Como treinar o YOLO customizado com seu dataset

1. Estruture seu dataset assim:

```
dataset/
  images/
    train/
      img1.jpg
      img2.jpg
    val/
      img3.jpg
  labels/
    train/
      img1.txt
      img2.txt
    val/
      img3.txt
```

2. Crie um arquivo de configuração `data.yaml`:

```yaml
train: /app/app/dataset/images/train
val: /app/app/dataset/images/val
nc: 1
names: ['validade']
```

3. Execute o treinamento (exemplo usando Ultralytics YOLOv8):

```sh
docker run --rm -v $(pwd)/app:/app/app ocr-v yolo detect train data=/app/app/dataset/data.yaml model=yolov8n.pt epochs=50 imgsz=640
```

- O modelo treinado será salvo na pasta `runs/detect/train`.
- Use esse modelo no `main.py` e `realtime.py` para melhores resultados.
