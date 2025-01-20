FROM python:3.11.5

WORKDIR /dance_motion_capture

RUN apt-get update

RUN apt-get install -y libgl1

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy all files`
COPY . .

# Expose the default FastAPI port
EXPOSE 8000

#Run the FastAPI server
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]