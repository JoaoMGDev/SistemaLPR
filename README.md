# 🚗 Sistema de Leitura de Placas (LPR) com Visão Computacional

## 📌 Sobre o Projeto

Este projeto consiste em uma aplicação de **Visão Computacional sem uso de Inteligência Artificial**, capaz de:

- Detectar placas de veículos (padrão Mercosul)
- Realizar a leitura dos caracteres da placa (OCR)
- Identificar a cor predominante do veículo
- Consultar o status do veículo em um banco de dados fictício

Ao final, o sistema exibe:

- 📄 Placa detectada  
- 🎨 Cor do veículo  
- ⚠️ Status (Em ordem, roubado ou divergência de cor)  

Tudo isso é mostrado tanto no terminal quanto diretamente na imagem processada.

---

## 🎯 Problema Resolvido

O sistema simula uma solução para **monitoramento veicular automatizado**, podendo ser aplicado em:

- Estacionamentos inteligentes  
- Portarias automatizadas  
- Sistemas de segurança  
- Controle de acesso  

---

## 🧠 Técnicas Utilizadas (Sem IA)

O projeto foi desenvolvido **sem uso de redes neurais ou machine learning**, utilizando apenas algoritmos clássicos de visão computacional:

### 🔍 Detecção de Placas
- Classificador Haar Cascade (`cascade.xml`)
- Treinado manualmente com:
  - ~300 imagens positivas (placas)
  - ~300 imagens negativas (sem placas)
- Ferramenta utilizada: **Cascade-Trainer-GUI**

---

### 🖼️ Processamento de Imagem

- Conversão para escala de cinza
- Blur Gaussiano (remoção de ruído)
- Binarização com Otsu
- Operações morfológicas:
  - Abertura (remoção de ruído)
  - Fechamento (melhoria de contornos)

---

### 📐 Correção de Inclinação (Deskew)

- Uso de `cv2.minAreaRect`
- Transformação Afim para alinhar a placa antes do OCR

---

### 🔤 OCR (Reconhecimento de Caracteres)

- Biblioteca: **Tesseract OCR**
- Configuração:
  - `--psm 7` (linha única de texto)
  - Whitelist de caracteres (A-Z, 0-9)
- Pós-processamento com regex para limpeza

---

### 🎨 Detecção de Cor do Veículo

- Conversão para espaço de cor HSV
- Segmentação por faixas de cor
- Contagem de pixels por máscara
- Identificação da cor predominante

---

### 🗄️ Consulta de Dados

- Banco de dados fictício em JSON contendo:
  - Placa
  - Cor registrada
  - Status de roubo

O sistema verifica:

- 🚨 Se o veículo é roubado  
- ⚠️ Se há divergência de cor  
- ✅ Se está em ordem  

---

## 🛠️ Tecnologias Utilizadas

- Python 3  
- OpenCV  
- NumPy  
- Tesseract OCR  
- Regex (`re`)  
- JSON  

---

## ⚙️ Instalação e Execução

### 2️⃣ Instalar o Tesseract

    Baixe e instale:  
    👉 https://github.com/tesseract-ocr/tesseract

    Depois configure o caminho no código:

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

### 3️⃣ Executar o projeto

    python sistema_lpr.py

### 4️⃣ Testar com outras imagens

    Altere a linha no código:

    img_bruta = cv2.imread('images/carro_teste.jpg')
 
---

📸 Resultados

O sistema exibe:

📦 Bounding box na placa
🔤 Texto reconhecido
🎨 Cor do veículo
⚠️ Status

---

### Além disso, mostra etapas intermediárias:

    * ROI da placa
    * Imagem tratada
    * Placa alinhada

---

### 📷 Imagem e Video demonstrativo

## Exemplo de leitura da placa

<img width="973" height="486" alt="exemplo_teste" src="https://github.com/user-attachments/assets/26e0450d-2727-4545-9296-0a5ae5b78737" />

## Video demonstrativo

https://github.com/user-attachments/assets/767c75c7-4e65-4dc7-aa07-c419b0d3a150

## 📚 Considerações Finais

Este projeto demonstra que é possível construir soluções funcionais de visão computacional utilizando apenas técnicas clássicas, sem dependência de Inteligência Artificial.

Apesar de simples, o sistema resolve um problema real e pode ser expandido com:

Integração com banco de dados real
Uso de câmera em tempo real
Melhorias no OCR
Interface gráfica

---

## 👨‍💻 Autor

João Marcos Pereira Gouveia - 24877
