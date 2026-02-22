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

---

##  Compatibilidad

Este reproductor está diseñado para ser agnóstico al hardware y funciona donde sea que haya una terminal:

* **TTY:** Funciona sin necesidad de un entorno gráfico (X11/Wayland).
* **Steam Deck:** Perfecto para el "Desktop Mode" o mediante una terminal en el modo de juego para ahorrar recursos mientras juegas.
* **Termux:** Gracias a su interfaz basada en texto, es ideal para dispositivos Android usando Termux.
* **Terminales:** Totalmente compatible con Linux.

---

## Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/Arsbyte/Pymus.git
cd pymus

```


2. **Instala las dependencias:**
```bash
pip install pygame mutagen pypresence

```
o

```bash
pip install -r requirements.txt

```
3. **Ejecuta el reproductor:**
```bash
python3 pymus.py

```



---

##  Controles

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

---

##  Requisitos

* **Python 3.7+**
* **Pygame:** Motor de audio principal.
* **Mutagen (Opcional):** Para lectura precisa de metadatos de duración.
* **Pypresence (Opcional):** Para integración con Discord.

---
