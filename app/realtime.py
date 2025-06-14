from ultralytics import YOLO
import cv2
import pytesseract
from datetime import datetime, timedelta
import re

def detect_expiry_region(image):
    model = YOLO('yolov8n.pt')  # Substitua pelo seu modelo customizado, se houver
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
    text = pytesseract.image_to_string(gray, config='--psm 6')
    match = re.search(r'(\d{2}/\d{2}/\d{4})|(\d{2}/\d{4})', text)
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

def main():
    cap = cv2.VideoCapture(0)
    print("Pressione 'q' para sair.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        regions, boxes = detect_expiry_region(frame)
        for idx, region in enumerate(regions):
            date_str = extract_date_from_image(region)
            if date_str:
                valid = is_date_valid(date_str)
                x1, y1, x2, y2 = map(int, boxes[idx])
                color = (0,255,0) if valid else (0,0,255)
                label = f'{date_str} - {"VÁLIDA" if valid else "VENCIDA"}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            else:
                x1, y1, x2, y2 = map(int, boxes[idx])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
                cv2.putText(frame, 'N/A', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Se passar imagem, valida imagem
        image = cv2.imread(sys.argv[1])
        regions, boxes = detect_expiry_region(image)
        for idx, region in enumerate(regions):
            date_str = extract_date_from_image(region)
            if date_str:
                valid = is_date_valid(date_str)
                print(f'Região {idx+1}: Data encontrada: {date_str} - {"VÁLIDA" if valid else "VENCIDA"}')
            else:
                print(f'Região {idx+1}: Nenhuma data encontrada')
    else:
        main()
