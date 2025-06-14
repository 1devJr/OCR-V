from ultralytics import YOLO
import cv2
import pytesseract
from datetime import datetime, timedelta
import re

def detect_expiry_region(image_path):
    model = YOLO('yolov8n.pt')  # Substitua pelo seu modelo customizado, se houver
    image = cv2.imread(image_path)
    results = model(image)
    boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []
    regions = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        crop = image[y1:y2, x1:x2]
        regions.append(crop)
    return regions, boxes

def extract_date_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, config='--psm 7 --oem 3')
    # Tenta DD/MM/YYYY
    match = re.search(r'(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(20\d{2})', text)
    if match:
        return match.group(0)
    # Tenta MM/YYYY
    match = re.search(r'(0[1-9]|1[0-2])/(20\d{2})', text)
    if match:
        return match.group(0)
    return None

def is_date_valid(date_str):
    try:
        if len(date_str) == 10:
            expiry = datetime.strptime(date_str, '%d/%m/%Y')
        elif len(date_str) == 7:
            expiry = datetime.strptime(date_str, '%m/%Y')
            expiry = expiry.replace(day=28) + timedelta(days=4)
            expiry = expiry - timedelta(days=expiry.day)
        else:
            return False
        return expiry >= datetime.now()
    except Exception:
        return False

def validate_image(image_path):
    regions, boxes = detect_expiry_region(image_path)
    image = cv2.imread(image_path)
    for idx, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # Salva cada recorte detectado para inspeção manual
        if idx < len(regions):
            cv2.imwrite(f"recorte_{idx+1}.jpg", regions[idx])
    cv2.imwrite("detecao_yolo.jpg", image)
    for idx, region in enumerate(regions):
        date_str = extract_date_from_image(region)
        if date_str:
            valid = is_date_valid(date_str)
            print(f'Região {idx+1}: Data encontrada: {date_str} - {"VÁLIDA" if valid else "VENCIDA"}')
        else:
            print(f'Região {idx+1}: Nenhuma data encontrada')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        validate_image(sys.argv[1])
    else:
        print('Uso: python main.py <caminho_da_imagem>')
