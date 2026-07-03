FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python scripts/prepare_demo_data.py --force
EXPOSE 8501
CMD ["sh", "-c", "python scripts/prepare_demo_data.py && streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
