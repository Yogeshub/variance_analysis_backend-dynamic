import tempfile
import os


def save_pdf_to_temp(buffer, filename="kpi_report.pdf"):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    with open(file_path, "wb") as f:
        f.write(buffer.getbuffer())

    return file_path
