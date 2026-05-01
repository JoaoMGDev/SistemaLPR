import cv2
import numpy as np
import pytesseract
import re
import json 

# =========================================================
# BANCO DE DADOS FICTÍCIO
# =========================================================

banco_dados_json = """
{
    "LSU3J43": {"cor": "BRANCO", "roubado": true},
    "FTR51EI5": {"cor": "BRANCO", "roubado": false},
    "HAE4025": {"cor": "VERMELHO", "roubado": false}
}
"""
base_veiculos = json.loads(banco_dados_json)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'


def alinhar_placa(imagem_binarizada):
    """Corrigir a inclinação (deskew) da placa usando Transformação Afim."""
    coordenadas = np.column_stack(np.where(imagem_binarizada > 0))
    if len(coordenadas) == 0:
        return imagem_binarizada

    angulo = cv2.minAreaRect(coordenadas)[-1]

    if angulo < -45:
        angulo = -(90 + angulo)
    else:
        angulo = -angulo

    if abs(angulo) < 1.5:
        return imagem_binarizada

    (altura, largura) = imagem_binarizada.shape[:2]
    centro = (largura // 2, altura // 2)
    matriz_rotacao = cv2.getRotationMatrix2D(centro, angulo, 1.0)
    imagem_alinhada = cv2.warpAffine(imagem_binarizada, matriz_rotacao, (largura, altura), 
                                     flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return imagem_alinhada

def ler_placa_com_ocr(imagem_alinhada):
    
    # inverte a cor a imagem 
    imagem_invertida = cv2.bitwise_not(imagem_alinhada)
    
    # limpeza de ruido
    kernel_limpeza = np.ones((2,2), np.uint8)
    imagem_limpa = cv2.morphologyEx(imagem_invertida, cv2.MORPH_OPEN, kernel_limpeza)

    # config. OCR
    configuracao_ocr = r'--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    texto_extraido = pytesseract.image_to_string(imagem_limpa, config=configuracao_ocr)
    
    # limpeza de caracteres nao desejados
    texto_maiusculo = texto_extraido.upper()
    texto_limpo = re.sub(r'[^A-Z0-9]', '', texto_maiusculo)
    
    return texto_limpo

def detectar_cor_veiculo(img_original, x, y, largura_placa, altura_placa):

    altura_roi = int(altura_placa * 1.5)
    inicio_y = max(0, y - altura_roi)
    
    roi_lataria = img_original[inicio_y:y, x:x+largura_placa]
    
    if roi_lataria.size == 0:
        return "Desconhecida"

    hsv_roi = cv2.cvtColor(roi_lataria, cv2.COLOR_BGR2HSV)
    
    limites_cores = {
        "BRANCO": ([0, 0, 180], [180, 40, 255]),
        "PRETO": ([0, 0, 0], [180, 255, 50]),
        "PRATA/CINZA": ([0, 0, 50], [180, 50, 180]),
        "AZUL": ([100, 50, 50], [140, 255, 255]),
        "VERMELHO_1": ([0, 50, 50], [10, 255, 255]),
        "VERMELHO_2": ([160, 50, 50], [180, 255, 255])
    }

    cor_predominante = "Desconhecida"
    maior_quantidade_pixels = 0
    area_total = roi_lataria.shape[0] * roi_lataria.shape[1]

    for nome_cor, (lower, upper) in limites_cores.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        
        mascara = cv2.inRange(hsv_roi, lower_np, upper_np)
        pixels_ativos = cv2.countNonZero(mascara)
        
        if pixels_ativos > maior_quantidade_pixels:
            maior_quantidade_pixels = pixels_ativos
            cor_predominante = "VERMELHO" if "VERMELHO" in nome_cor else nome_cor

    if area_total > 0 and (maior_quantidade_pixels / area_total) > 0.2:
        return cor_predominante
    
    return "Desconhecida"

# =========================================================
# PIPELINE PRINCIPAL 
# =========================================================

classificador = cv2.CascadeClassifier('cascade.xml') 

img_bruta = cv2.imread('images\carro_teste3.jpg') 
img = cv2.resize(img_bruta, (680, 453))
img_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

objetos = classificador.detectMultiScale(
    img_cinza, 
    scaleFactor=1.1,    
    minNeighbors=15,    
    minSize=(100, 30),  
)

if len(objetos) == 0: 
    print("Nenhuma placa detectada nesta imagem.")
else:
    for (x, y, l, a) in objetos: 
        
        ajuste_x = int(l * 0.20) 
        novo_x = max(0, x - ajuste_x)
        nova_largura = l + (2 * ajuste_x)
        
        ajuste_y = int(a * 0.15)
        novo_y = y + ajuste_y 
        nova_altura = int(a * 0.65) 
        
        roi_placa = img[novo_y:novo_y+nova_altura, novo_x:novo_x+nova_largura]
        roi_cinza = cv2.cvtColor(roi_placa, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(roi_cinza, (5, 5), 0)
        _, binarizada = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        placa_limpa = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel) 
        
        contornos, _ = cv2.findContours(placa_limpa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contornos) > 0:
            maior_contorno = max(contornos, key=cv2.contourArea)
            retangulo_inclinado = cv2.minAreaRect(maior_contorno)
            box = cv2.boxPoints(retangulo_inclinado)
            box = np.int32(box)
            
            box[:, 0] += novo_x
            box[:, 1] += novo_y
            cv2.drawContours(img, [box], 0, (255, 255, 0), 2)
        
        placa_alinhada = alinhar_placa(placa_limpa)
        texto_final_placa = ler_placa_com_ocr(placa_alinhada)
        
        cor_do_carro = detectar_cor_veiculo(img, novo_x, novo_y, nova_largura, nova_altura)
        
        # consulta 
        mensagem_status = "Em Ordem"
        cor_texto_status = (0, 255, 0) 

        if texto_final_placa in base_veiculos:
            dados_veiculo = base_veiculos[texto_final_placa]
            cor_registro = dados_veiculo.get("cor", "")
            veiculo_roubado = dados_veiculo.get("roubado", False)

            if veiculo_roubado:
                mensagem_status = "ALERTA: VEICULO ROUBADO!"
                cor_texto_status = (0, 0, 255) 
            
            elif cor_do_carro != "Desconhecida" and cor_do_carro != cor_registro:
                mensagem_status = f"ALERTA: Cor divergente (Registro: {cor_registro})"
                cor_texto_status = (0, 165, 255) 
        else:
            mensagem_status = "Placa nao consta no sistema."
            cor_texto_status = (0, 255, 255) 

        print("-" * 40)
        print(f"SUCESSO! ")
        print(f" ")
        print(f"O LPR detectou a Placa: {texto_final_placa}")
        print(f" ")
        print(f"Metadados adicionais:")
        print(f" ")
        print(f" - Cor do Veículo -> {cor_do_carro}")
        print(f" ")
        print(f" - Consulta ao Sistema -> {mensagem_status}")
        print(f" ")
        print("-" * 40)
        
        cv2.putText(img, f"Leitura: {texto_final_placa} - {cor_do_carro}", (novo_x, novo_y - 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(img, f"Status: {mensagem_status}", (novo_x, novo_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto_status, 2)
        
        cv2.imshow('1 - Recorte Bruto (ROI)', roi_placa)
        cv2.imshow('2 - Placa Tratada (Morfologia)', placa_limpa)
        cv2.imshow('3 - Placa Alinhada para OCR', placa_alinhada)
        
    cv2.imshow('LPR Final - Camera', img) 
    cv2.waitKey(0) 
    cv2.destroyAllWindows()