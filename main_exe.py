import os
import sys
import webbrowser
from threading import Timer
from waitress import serve
from app import create_app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Garante que as pastas necessárias existam no diretório do executável
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    
    # Inicia o app em modo produção
    app = create_app('production')
    
    # Abre o navegador após 1.5 segundos
    Timer(1.5, open_browser).start()
    
    print("FitControl Pro V2 Iniciado")
    print("Acesse: http://127.0.0.1:5000")
    print("Pressione Ctrl+C para encerrar")
    
    serve(app, host='0.0.0.0', port=5000, threads=8)
