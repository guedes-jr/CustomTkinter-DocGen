# Guia de Compilação do DocGen Pro (Windows)

Este documento explica de forma simples os dois processos de geração do sistema que criamos: como criar a versão "portátil" que não precisa ser instalada, e como criar o "instalador oficial" (`.exe`) com Menu Iniciar e Atalho na Área de Trabalho.

---

## 1. O Executável Portátil (Feito via PyInstaller)

O executável portátil é um arquivo único (`DocGen Pro.exe`). Ele contém todo o Python, as bibliotecas, as interfaces gráficas e as imagens do seu sistema embutidas num único artefato.

**Vantagens:** 
- Roda imediatamente ao dar um duplo-clique.
- Não exige nenhuma instalação no computador do cliente, basta executar.

**Como Gerar:**
Na raiz deste projeto, nós configuramos um script inteligente chamado `build.bat` (e equivalente `make build` no Makefile).
1. Abra um terminal na pasta do projeto.
2. Certifique-se de que o seu ambiente virtual (`venv`) está ativo e atualizado.
3. Execute o comando:
   ```bash
   .\build.bat
   ```
4. Aguarde o processo (a tela limpará versões antigas e fará um novo build seguro).
5. Ao concluir, vá até a pasta `dist` recém-criada no projeto. O seu aplicativo estará lá como **`DocGen Pro.exe`**.

---

## 2. O Instalador Tradicional (Feito via Inno Setup)

O programa "Instalador" nada mais é do que uma "embalagem" automatizada para o seu executável portátil criado no passo acima. 
Esse processo utiliza uma tecnologia chamada **Inno Setup**, que copia os arquivos para `C:\Program Files`, gera atalhos e registra um desinstalador oficial no Windows.

**Vantagens:**
- Passa muito mais credibilidade e profissionalismo para o seu cliente final.
- O usuário encontra o atalho com o ícone correto na Área de Trabalho e no Menu Iniciar do Windows automaticamente.

### Pré-requisitos
Certifique-se de ter instalado o compilador Inno Setup no seu Windows. Se ainda não possui:
1. Acesse: [https://jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)
2. Faça o download da versão mais recente (`ispack-xxx.exe`) e instale no seu computador (ele é leve e gratuito).

**Como Gerar:**
1. Primeiro, siga completamente as etapas da seção `"1. O Executável Portátil"` para garantir que você possui a versão mais nova do seu `DocGen Pro.exe` dentro da pasta `dist`.
2. Vá na raiz deste projeto e dê um **clique duplo no arquivo chamado `setup.iss`**. Ele vai ser aberto pelo programa Inno Setup que você instalou.
3. No painel superior, procure a aba **Build** e depois clique na opção **Compile** (ou apenas pressione **Ctrl + F9**).
4. O processo demora 3 segundos! 
5. Em seguida, vá novamente na sua pasta `dist` e você observará o arquivo final **`Instalador_DocGen_Pro.exe`**. É este arquivo que você pode vender ou distribuir para as outras pessoas instalarem o DocGen Pro.
