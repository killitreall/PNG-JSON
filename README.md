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
