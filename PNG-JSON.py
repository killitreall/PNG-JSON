import gradio as gr
import tempfile, os, shutil, zipfile
from pack_tools import pack_png_sequence, extract_pngs

MAX_JSON_SIZE_MB = 200

custom_css = """
.gr-button,
button.svelte-1ipelgc,
button.svelte-1ipelgc:active,
button.svelte-1ipelgc:focus {
    background: orange !important;
    border-color: #e69500 !important;
    color: #fff !important;
}
.gr-button[disabled],
button.svelte-1ipelgc[disabled] {
    background: #ccc !important;
    color: #888 !important;
    border-color: #aaa !important;
    cursor: not-allowed !important;
}
.gr-step {
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 18px 18px 10px;
    margin-bottom: 18px;
    background: transparent;
}
.gr-step-title {
    font-weight: bold;
    color: #fff;
    margin-bottom: 8px;
    font-size: 1.1em;
}
.main-content-row {
    width: 50% !important;
    margin: 0 auto !important;
}
.gr-files .file-list {
    max-height: 300px;
    overflow-y: auto;
}
"""

def pack_png_interface(png_paths, fps):
    if not png_paths:
        return None, "Ошибка: Не выбраны PNG-файлы!"
    with tempfile.TemporaryDirectory() as tmpdir:
        for png_path in png_paths:
            fname = os.path.basename(png_path)
            with open(png_path, 'rb') as infile, \
                 open(os.path.join(tmpdir, fname), 'wb') as outfile:
                outfile.write(infile.read())
        output_json = os.path.join(tmpdir, 'output.json')
        pack_png_sequence(tmpdir, output_json, int(fps))
        fd, temp_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        shutil.copy2(output_json, temp_path)
    return temp_path, "JSON успешно создан!"

def extract_pngs_interface(json_path):
    try:
        # Проверяем размер файла
        size = os.path.getsize(json_path)
        size_mb = size / (1024 * 1024)
        if size == 0:
            return None, "Ошибка: Файл пустой!"
        if size_mb > MAX_JSON_SIZE_MB:
            return None, f"Ошибка: Файл слишком большой ({size_mb:.1f} МБ). Лимит: {MAX_JSON_SIZE_MB} МБ."
        with tempfile.TemporaryDirectory() as tmpdir:
            input_json_temp_path = os.path.join(tmpdir, 'input.json')
            shutil.copy2(json_path, input_json_temp_path)
            out_dir = os.path.join(tmpdir, 'pngs')
            os.makedirs(out_dir, exist_ok=True)
            files = extract_pngs(input_json_temp_path, out_dir)
            zip_path = os.path.join(tmpdir, 'frames.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for f in files:
                    zipf.write(f, os.path.basename(f))
            fd, temp_zip = tempfile.mkstemp(suffix='.zip')
            os.close(fd)
            shutil.copy2(zip_path, temp_zip)
        return temp_zip, f"PNG успешно распакованы! Размер JSON: {size_mb:.1f} МБ"
    except Exception as e:
        return None, f"Ошибка: {e}"

with gr.Blocks(css=custom_css) as demo:
    with gr.Column(elem_classes=["main-content-row"]):
        gr.Markdown("# PNG ⇄ JSON Bodymovin")
        with gr.Tab("PNG → JSON"):
            with gr.Row():
                with gr.Column():
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 1</div>Выделите все PNG-файлы в нужной папке (Ctrl+A) и загрузите их сюда.""")
                        pngs = gr.Files(label="PNG-файлы", file_types=[".png"], height=350)
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 2</div>Укажите FPS (частоту кадров).""")
                        fps = gr.Number(label="FPS", value=30, precision=0)
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 3</div>Нажмите <b>Собрать JSON</b> и скачайте результат.""")
                        btn1 = gr.Button("Собрать JSON", interactive=False)
                        json_out = gr.File(label="Скачать JSON", visible=False)
                        status = gr.Markdown(visible=False)
            def on_pack(pngs, fps):
                if not pngs:
                    return gr.update(value=None, visible=False), gr.update(value="Ошибка: Не выбраны PNG-файлы!", visible=True)
                result, msg = pack_png_interface(pngs, fps)
                return gr.update(value=result, visible=bool(result)), gr.update(value=msg, visible=True)
            btn1.click(on_pack, inputs=[pngs, fps], outputs=[json_out, status])
            def files_changed(files):
                return gr.update(interactive=bool(files))
            pngs.change(files_changed, inputs=pngs, outputs=btn1)
        with gr.Tab("JSON → PNG"):
            with gr.Row():
                with gr.Column():
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 1</div>Загрузите JSON-файл, полученный на предыдущем шаге.""")
                        json_in = gr.File(label="JSON файл", file_types=[".json"])
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 2</div>Нажмите <b>Распаковать PNG</b>.""")
                        btn2 = gr.Button("Распаковать PNG", interactive=False)
                    with gr.Column(elem_classes=["gr-step"]):
                        gr.Markdown("""<div class='gr-step-title'>Шаг 3</div>Скачайте архив с PNG-кадрами.""")
                        zip_out = gr.File(label="Скачать PNG (zip)", visible=False)
                        status2 = gr.Markdown(visible=False)
            def on_extract(json_in):
                if not json_in:
                    return gr.update(value=None, visible=False), gr.update(value="Ошибка: Не выбран JSON-файл!", visible=True)
                result, msg = extract_pngs_interface(json_in)
                return gr.update(value=result, visible=bool(result)), gr.update(value=msg, visible=True)
            btn2.click(on_extract, inputs=json_in, outputs=[zip_out, status2])
            def json_changed(file):
                return gr.update(interactive=bool(file))
            json_in.change(json_changed, inputs=json_in, outputs=btn2)

if __name__ == "__main__":
    demo.launch(inbrowser=True)
