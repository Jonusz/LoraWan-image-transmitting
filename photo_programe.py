import time
import subprocess
import datetime

print("Uruchamiam program do zdjęć...")
print("Aby zatrzymać, wciśnij w terminalu Ctrl + C")

# Nieskończona pętla
while True:
    # 1. Pobieramy aktualną datę i czas, żeby każde zdjęcie miało inną nazwę
    # Format: RRRR-MM-DD_GG-MM-SS
    teraz = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = f"zdjecie_{teraz}.jpg"
    
    print(f"Robie zdjecie: {nazwa_pliku}")
    
    # 2. Wywołanie komendy systemowej robiącej zdjęcie
    # -t 1000 oznacza czas na rozgrzanie matrycy (1 sekunda)
    # --nopreview wyłącza podgląd (ważne dla trybu headless, oszczędza prąd)
    subprocess.run([
        "rpicam-still", 
        "-o", nazwa_pliku, 
        "-t", "1000", 
        "--nopreview",
        "--autofocus-mode", "manual",
        "--lens-position", "4"
    ])
    
    # 3. Usypiamy program na 10 sekund
    time.sleep(30)