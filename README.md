# PNG-JSON
PNG-JSON converter

## Usage with system Python
1. Install dependencies (preferably in a virtual environment):
   ```bash
   python -m pip install --upgrade -r requirements.txt
   ```
2. Launch the application:
   ```bash
   python gradio_app.py
   ```

If you run into an error mentioning `socket_options` when starting the
application, ensure that `httpcore` is at least version 0.18.0:

```bash
python -m pip install --upgrade "httpcore>=0.18"
```

---

## Использование системного Python
1. Установите зависимости (желательно в виртуальном окружении):
   ```bash
   python -m pip install --upgrade -r requirements.txt
   ```
2. Запустите приложение:
   ```bash
   python gradio_app.py
   ```

Если при запуске появляется ошибка `socket_options`, обновите пакет
`httpcore` до версии не ниже 0.18:

```bash
python -m pip install --upgrade "httpcore>=0.18"
```
