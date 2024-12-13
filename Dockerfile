FROM ubuntu:20.04

WORKDIR /app

COPY . .

RUN apt update
RUN apt upgrade
RUN apt install python3 python3-pip -y
RUN pip install numpy

EXPOSE 5555

CMD [ "python", "-m", "main"]