# PYMUS
**PY-MUS** es un reproductor de música ligero y minimalista que vive completamente en tu terminal. Diseñado para quienes prefieren la línea de comandos, ofrece una navegación fluida por carpetas, barras de progreso dinámicas y soporte para **Discord Rich Presence**.

[English Version](https://github.com/Ars-byte/Pymus/blob/main/README-EN.md)

---

## Características
* **Interfaz TUI:** Navegación visual mediante terminal con colores ANSI y efectos de resaltado.
* **Navegador de Archivos:** Explora directorios y selecciona carpetas de música en tiempo real.
* **Control Total:** Pausa, salto de pistas (`n`/`p`), ajuste de volumen (`+`/`-`) y búsqueda de tiempo (`h`/`l`).
* **Discord RPC:** Muestra automáticamente qué canción estás escuchando en tu perfil de Discord.
* **Soporte Multiformato:** Compatible con `.mp3`, `.wav`, `.ogg`, `.flac` y `.opus`.
* **Eficiencia:** Uso de `__slots__` para minimizar el consumo de memoria RAM.
* **Arquitectura modular:** Separación clara entre lógica de reproducción (`backend/`) e interfaz de terminal (`frontend/`).

Consumo de recursos:
<img width="991" height="25" alt="image" src="https://github.com/user-attachments/assets/b15fd805-555c-438c-b6a5-7d99fb5f120c" />

## Preview:
En sistemas inmutables:
<img width="1087" height="679" alt="image" src="https://github.com/user-attachments/assets/e6100d2a-e6b5-4884-abec-e4f74aef80f4" />

En sistemas mutables:
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e7db1c77-f007-41a7-a046-2442ce150030" />

---

## Compatibilidad
Este reproductor está diseñado para ser agnóstico al hardware y funciona donde sea que haya una terminal:
* **TTY:** Funciona sin necesidad de un entorno gráfico (X11/Wayland).
* **Steam Deck:** Perfecto para el "Desktop Mode" o mediante una terminal en el modo de juego para ahorrar recursos mientras juegas.
* **Termux:** Gracias a su interfaz basada en texto, es ideal para dispositivos Android usando Termux.
* **Terminales:** Totalmente compatible con Linux.

---

## Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/Ars-byte/Pymus.git && cd Pymus
```

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```
```bash
sudo apt install vlc ffmpeg
```

3. **Ejecuta el reproductor:**
```bash
python3 main.py
```

---

## Estructura del proyecto

```
Pymus/
├── main.py                   # Punto de entrada — orquesta backend y frontend
├── backend/
│   ├── __init__.py
│   ├── audio.py              # Backends de audio: VLCBackend, FFPlayBackend, make_backend()
│   └── player.py             # Clase Player: estado y operaciones de reproducción
└── frontend/
    ├── __init__.py
    ├── colors.py             # Códigos ANSI, W(), hline(), fmt_time()
    ├── input.py              # Lectura de teclado en modo raw
    ├── browser.py            # UI del navegador de directorios
    └── player_view.py        # UI del reproductor (lista + barra de progreso)
```

### backend/
| Archivo | Responsabilidad |
| --- | --- |
| `audio.py` | Abstracción de hardware: `VLCBackend` y `FFPlayBackend`. Detecta automáticamente cuál usar con `make_backend()`. |
| `player.py` | Lógica de dominio: escaneo de carpetas, reproducción, pausa, seek, volumen y Discord RPC. Sin imports de terminal. |

### frontend/
| Archivo | Responsabilidad |
| --- | --- |
| `colors.py` | Constantes ANSI y utilidades de formato (`fmt_time`, `hline`). |
| `input.py` | Captura de teclado aislada (`read_key`). |
| `browser.py` | Vista interactiva del navegador de archivos. |
| `player_view.py` | Renderizado de la pantalla del reproductor. |

---

## Controles

### Explorador (Browser)
| Tecla | Acción |
| --- | --- |
| `↑` / `↓` o `k` / `j` | Mover el cursor |
| `Enter` / `→` / `l` | Abrir carpeta o seleccionar directorio |
| `Backspace` / `←` / `h` | Volver a la carpeta anterior |
| `o` | Ir a la carpeta personal ($HOME) |
| `q` | Cancelar / Salir |

### Reproductor (Player)
| Tecla | Acción |
| --- | --- |
| `Espacio` | Pausar / Reanudar |
| `Enter` | Reproducir canción seleccionada |
| `n` / `p` | Siguiente / Anterior canción |
| `←` / `→` o `h` / `l` | Retroceder / Adelantar 5 segundos |
| `+` / `-` | Subir / Bajar volumen |
| `o` | Abrir el explorador de carpetas |
| `q` | Salir del programa |
| `s` | Random         |
| `r` | Repetir        |
