import cv2
import os

def draw_rectangle(event, x, y, flags, param):
    global drawing, ix, iy, ex, ey, img, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img = img_copy.copy()
            cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        ex, ey = x, y
        cv2.rectangle(img, (ix, iy), (ex, ey), (0, 255, 0), 2)

def save_yolo_format(image_path, bbox, output_dir, class_id):
    h, w, _ = cv2.imread(image_path).shape
    x_center = (bbox[0] + bbox[2]) / 2 / w
    y_center = (bbox[1] + bbox[3]) / 2 / h
    bw = abs(bbox[2] - bbox[0]) / w
    bh = abs(bbox[3] - bbox[1]) / h
    label = f"{class_id} {x_center} {y_center} {bw} {bh}\n"
    base = os.path.splitext(os.path.basename(image_path))[0]
    with open(os.path.join(output_dir, base + '.txt'), 'w') as f:
        f.write(label)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Uso: python annotate.py <imagem> <output_dir>')
        exit(1)
    image_path = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(image_path)
    img_copy = img.copy()
    drawing = False
    ix = iy = ex = ey = 0
    cv2.namedWindow('Annotate')
    cv2.setMouseCallback('Annotate', draw_rectangle)
    print('Desenhe a caixa. Pressione 0 para "correta" ou 1 para "errada" após desenhar. S para salvar, ESC para sair.')
    class_id = None
    while True:
        cv2.imshow('Annotate', img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('0'):
            class_id = 0
            print('Classe: correta')
        elif key == ord('1'):
            class_id = 1
            print('Classe: errada')
        elif key == ord('s'):
            if class_id is None:
                print('Selecione a classe: 0 (correta) ou 1 (errada)')
                continue
            bbox = [min(ix, ex), min(iy, ey), max(ix, ex), max(iy, ey)]
            save_yolo_format(image_path, bbox, output_dir, class_id)
            cv2.imwrite(os.path.join(output_dir, os.path.basename(image_path)), img_copy)
            print('Salvo!')
            break
        elif key == 27:
            break
    cv2.destroyAllWindows()
